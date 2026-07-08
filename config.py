import os

# ==============================
# Telegram
# ==============================

# Токен Telegram-бота
TOKEN = os.getenv("TOKEN") or os.getenv("BOT_TOKEN")

# Telegram ID лидера клана
LEADER_ID = int(os.getenv("LEADER_ID", "7816223649"))


# ==============================
# Supabase
# ==============================

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")

SUPABASE_KEY = (
    os.getenv("SUPABASE_SECRET_KEY")
    or os.getenv("SUPABASE_KEY")
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)


# ==============================
# Локальные файлы
# ==============================

# Используется только для первой миграции
DATA_FILE = "members.json"


# ==============================
# ClanControl Bot
# ==============================

BOT_NAME = "ClanControl Bot"

BOT_VERSION = "3.0"

CLAN_NAME = "SB"

MAX_LOG_HISTORY = 1000

MAX_WAREHOUSE_HISTORY = 1000