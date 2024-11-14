import os
from dotenv import load_dotenv

def load_config():
    # Load .env file
    load_dotenv()

    # Required environment variables
    required_vars = [
        'TELEGRAM_TOKEN',
        'GITLAB_URL',
        'GITLAB_TOKEN',
        'JIRA_URL',
        'JIRA_USER',
        'JIRA_TOKEN'
    ]

    # Check if all required variables are set
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    # Optional variables with defaults
    os.environ.setdefault('DB_PATH', 'review_bot.db') 