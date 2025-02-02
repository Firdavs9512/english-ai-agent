import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_VOCABULARY_DB = os.getenv("NOTION_VOCABULARY_DB")
NOTION_GRAMMAR_PAGE = os.getenv("NOTION_GRAMMAR_PAGE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
