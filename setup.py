from setuptools import setup, find_packages

setup(
    name="review-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot",
        "python-gitlab",
        "jira",
        "python-dotenv",
    ],
    python_requires=">=3.7",
) 