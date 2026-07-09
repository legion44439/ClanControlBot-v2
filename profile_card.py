from view_utils import safe_int, progress_bar, get_joined_days, get_level_rank, get_tournament_totals
from honor_awards import render_honor_awards_short


def render_profile_card(player, user_id, achievement_points):
    level = safe_int(player.get("level"), 1)
    xp = safe_int(player.get("xp"), 0)
    xp_current = xp % 1000
    xp_needed = 1000 - xp_current if xp_current else 1000
    level_bar = progress_bar(xp_current, 1000, 10)

    activity = safe_int(player.get("activity"), 0)
    activity_target = 50
    for target in (50, 200, 500, 1000, 2500, 5000):
        if activity < target:
            activity_target = target
            break
    else:
        activity_target = max(5000, activity)
    activity_bar = progress_bar(activity, activity_target, 10)

    joined_days = get_joined_days(player)
    tournament_played, tournament_wins, tournament_winrate = get_tournament_totals(player)

    return (
        "╔══════════════════════╗\n"
        "        👤 ПРОФИЛЬ ИГРОКА\n"
        "╚══════════════════════╝\n\n"
        f"🎮 {player.get('name', 'не указан')}\n"
        f"{player.get('role', '⚔️ Боец')}\n"
        f"{get_level_rank(level)}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📈 ПРОГРЕСС\n\n"
        f"⭐ Уровень: {level}\n"
        f"💎 XP: {xp_current} / 1000\n"
        f"{level_bar}\n"
        f"⏳ До следующего уровня: {xp_needed} XP\n\n"
        f"🔥 Активность: {activity} / {activity_target}\n"
        f"{activity_bar}\n"
        f"🏅 Очки достижений: {achievement_points}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🏰 КЛАН\n\n"
        f"📅 В клане: {joined_days} дней\n"
        f"📆 Дата вступления: {player.get('joined', 'неизвестно')}\n"
        f"💰 Общий вклад: {player.get('contribution', 0)}\n"
        f"📥 Передано на склад: {player.get('warehouse_added', 0)}\n"
        f"📤 Получено со склада: {player.get('warehouse_taken', 0)}\n"
        f"⚔️ Рейдов: {player.get('raids', 0)}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🏆 ТУРНИРЫ\n\n"
        f"🎮 Участий: {tournament_played}\n"
        f"🥇 Побед: {tournament_wins}\n"
        f"📈 Винрейт: {tournament_winrate}%\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🏅 ПОЧЁТНЫЕ НАГРАДЫ\n\n"
        f"{render_honor_awards_short(player)}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📱 TELEGRAM\n\n"
        f"👤 Имя: {player.get('telegram_name', 'не указано')}\n"
        f"📨 Аккаунт: {player.get('telegram_account', 'не указан')}\n"
        f"🆔 ID: {user_id}"
    )
