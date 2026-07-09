from datetime import datetime


def safe_int(value, default=0):
    try:
        return int(value or default)
    except Exception:
        return default


def progress_bar(current, target, size=10):
    current = safe_int(current)
    target = safe_int(target, 1)

    if target <= 0:
        return "▰" * size + " 100%"

    percent = min(100, max(0, int((current / target) * 100)))
    filled = int(size * percent / 100)
    empty = size - filled

    return f"{'▰' * filled}{'▱' * empty} {percent}%"


def get_joined_days(player):
    joined = player.get("joined")
    if not joined:
        return 0

    try:
        joined_date = datetime.strptime(joined, "%d.%m.%Y")
        return max(0, (datetime.now() - joined_date).days)
    except Exception:
        return 0


def get_level_rank(level):
    level = safe_int(level, 1)

    if level >= 100:
        return "🔴 Мифический"
    if level >= 50:
        return "🟡 Легенда"
    if level >= 25:
        return "🟣 Элита"
    if level >= 10:
        return "🔵 Ветеран"
    if level >= 5:
        return "🟢 Опытный"

    return "⚪ Новичок"


def get_tournament_totals(player):
    stats = player.get("tournaments")
    if not isinstance(stats, dict):
        return 0, 0, 0

    played = 0
    wins = 0

    for item in stats.values():
        if isinstance(item, dict):
            played += safe_int(item.get("played"))
            wins += safe_int(item.get("wins"))

    winrate = int((wins / played) * 100) if played else 0
    return played, wins, winrate
