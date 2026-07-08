import os

# Telegram bot token. In Render add Environment Variable: TOKEN
TOKEN = os.getenv("TOKEN") or os.getenv("BOT_TOKEN")

# Main leader Telegram ID
LEADER_ID = int(os.getenv("LEADER_ID", "7816223649"))

# Supabase settings. Keep keys ONLY in Render Environment Variables.
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Old local file name used only for one-time migration if Supabase users table is empty.
DATA_FILE = "members.json"
