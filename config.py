import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")
ADMIN_IDS = {int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()}
SIGNUP_BONUS = int(os.getenv("SIGNUP_BONUS", "5"))
REFERRAL_BONUS = int(os.getenv("REFERRAL_BONUS", "3"))
DAILY_BONUS = int(os.getenv("DAILY_BONUS", "2"))
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Add it to your .env file.")
