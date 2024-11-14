import os
import re
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)
from .repositories.user_repository import UserRepository
from .services.review_service import ReviewService
from .services.gitlab_service import GitLabService
from .services.jira_service import JiraService
from .models import UserStatus
from .config import load_config

# Conversation states
GITLAB_NAME, JIRA_NAME = range(2)

class ReviewBot:
    def __init__(self):
        self.user_repository = UserRepository(os.getenv('DB_PATH', 'review_bot.db'))
        self.review_service = ReviewService(self.user_repository)
        self.gitlab_service = GitLabService()
        self.jira_service = JiraService()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send welcome message when the command /start is issued."""
        await update.message.reply_text(
            "Welcome to Review Bot! Use /register to join the review queue."
        )

    async def register(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the registration process."""
        user = self.user_repository.get_user(
            update.effective_user.id,
            update.effective_chat.id
        )
        
        if user:
            await update.message.reply_text("You are already registered!")
            return ConversationHandler.END

        await update.message.reply_text("Please enter your GitLab username:")
        return GITLAB_NAME

    async def gitlab_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store GitLab name and ask for Jira name."""
        context.user_data['gitlab_name'] = update.message.text
        await update.message.reply_text("Please enter your Jira username:")
        return JIRA_NAME

    async def jira_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Store Jira name and complete registration."""
        try:
            user = self.user_repository.add_user(
                telegram_id=update.effective_user.id,
                chat_id=update.effective_chat.id,
                gitlab_name=context.user_data['gitlab_name'],
                jira_name=update.message.text
            )
            await update.message.reply_text(
                f"Registration complete! You've been added to the review queue."
            )
        except Exception as e:
            await update.message.reply_text(
                f"Error during registration: {str(e)}"
            )
        return ConversationHandler.END

    async def unregister(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Unregister user from the review queue."""
        try:
            self.user_repository.delete_user(
                update.effective_user.id,
                update.effective_chat.id
            )
            await update.message.reply_text("You've been unregistered successfully.")
        except Exception as e:
            await update.message.reply_text(f"Error during unregistration: {str(e)}")

    async def review(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle review command."""
        if not context.args:
            await update.message.reply_text("Please provide a merge request link!")
            return

        mr_link = context.args[0]
        if not re.match(r'https?://gitlab\.com/.+/\-/merge_requests/\d+', mr_link):
            await update.message.reply_text("Invalid merge request link format!")
            return

        # Get MR author's GitLab username
        success, mr_title, message = self.gitlab_service.get_mr_title(mr_link)
        if not success:
            await update.message.reply_text(message)
            return

        # Assign review
        success, reviewer, message = self.review_service.assign_review(
            update.effective_chat.id,
            mr_link,
            context.user_data['gitlab_name']  # MR author's username
        )

        if not success or not reviewer:
            await update.message.reply_text(message)
            return

        # Assign MR in GitLab
        success, message = self.gitlab_service.assign_merge_request(
            mr_link,
            reviewer.gitlab_name
        )
        if not success:
            await update.message.reply_text(f"Error assigning MR: {message}")
            return

        # Update Jira task
        # Extract Jira task key from MR title (assuming format: "PROJ-123: Description")
        jira_key_match = re.match(r'([A-Z]+-\d+)', mr_title)
        if jira_key_match:
            jira_key = jira_key_match.group(1)
            success, message = self.jira_service.update_task_status(
                jira_key,
                reviewer.jira_name
            )
            if not success:
                await update.message.reply_text(f"Error updating Jira: {message}")

        await update.message.reply_text(
            f"Review assigned to @{reviewer.gitlab_name}!"
        )

    async def end_review(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle end_review command."""
        user = self.user_repository.get_user(
            update.effective_user.id,
            update.effective_chat.id
        )

        if not user:
            await update.message.reply_text("You are not registered!")
            return

        if user.status != UserStatus.REVIEWING:
            await update.message.reply_text("You are not reviewing anything!")
            return

        success, message = self.review_service.end_review(user)
        await update.message.reply_text(
            "Review completed, you've been added back to the queue!" if success 
            else f"Error: {message}"
        )

def main():
    # Load environment variables
    load_config()
    
    bot = ReviewBot()
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()

    # Add conversation handler for registration
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', bot.register)],
        states={
            GITLAB_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.gitlab_name)],
            JIRA_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.jira_name)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', bot.start))
    application.add_handler(CommandHandler('unregister', bot.unregister))
    application.add_handler(CommandHandler('review', bot.review))
    application.add_handler(CommandHandler('end_review', bot.end_review))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main() 