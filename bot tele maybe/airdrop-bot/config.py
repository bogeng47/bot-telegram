import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API credentials
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")

# Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(BASE_DIR, "accounts", "sessions")
DB_PATH = os.path.join(BASE_DIR, "data", "airdrop.db")

# Scheduler
TASK_INTERVAL_MINUTES = int(os.getenv("TASK_INTERVAL", 60))
