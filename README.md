# Review Bot

A Telegram bot for managing code reviews with GitLab and Jira integration.

## Installation

1. Clone the repository: 

```
git clone https://github.com/yourusername/review-bot.git
cd review-bot
```

2. Create and activate virtual environment:

```
# For Unix/macOS
python -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:

```
pip install -e .
```

4. Copy `.env.example` to `.env` and fill in your credentials:

```
cp .env.example .env
# Edit .env with your favorite text editor
```

## Running the bot

```
python -m bot.main
```

## Environment Variables

- `TELEGRAM_TOKEN`: Your Telegram bot token from @BotFather
- `GITLAB_URL`: GitLab instance URL (e.g., https://gitlab.com)
- `GITLAB_TOKEN`: Your GitLab personal access token
- `JIRA_URL`: Your Jira instance URL
- `JIRA_USER`: Jira username (email)
- `JIRA_TOKEN`: Jira API token
- `DB_PATH`: (Optional) Path to SQLite database file

Now, here are the step-by-step instructions to install and run the bot:

1. First, make sure you have Python 3.7 or higher installed:

```
python --version
```

2. Create and navigate to project directory:

```
mkdir review_bot
cd review_bot
```

3. Create all the files as shown in the structure above with the code we've written previously.

4. Create and activate virtual environment:

```
# For Unix/macOS
python -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

5. Install the project in editable mode:

```
pip install -e .
```

6. Create and configure your .env file:

```
cp .env.example .env
# Edit .env with your credentials
```

7. Run the bot:

```
python -m bot.main
```

To test if the bot is working:
1. Open Telegram
2. Find your bot using the username you created with @BotFather
3. Send the `/start` command
4. Try registering with `/register`

Common troubleshooting:
1. If you get import errors, make sure you're running from the correct directory and the virtual environment is activated
2. If the bot doesn't respond, check your TELEGRAM_TOKEN
3. If you get database errors, check if the DB_PATH directory is writable
4. For GitLab/Jira integration issues, verify your API tokens and permissions

Would you like me to explain any part in more detail or help with specific issues?

