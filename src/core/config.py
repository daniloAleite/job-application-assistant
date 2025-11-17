import os

from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Configuration settings


class Settings:
    # OpenAI API Key
    openai_api_key: str = os.getenv("OPENAI_API_KEY")


# Instantiate settings
settings = Settings()
