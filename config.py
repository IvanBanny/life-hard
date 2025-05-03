# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BUNQ_API_KEY = os.getenv("BUNQ_API_KEY")
DEVICE_DESCRIPTION = os.getenv("DEVICE_DESCRIPTION")
API_CONTEXT_FILE = os.getenv("CONTEXT_FILE")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")