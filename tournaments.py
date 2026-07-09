from datetime import datetime


TOURNAMENT_MODES = [
    {
        "id": "storm",
        "name": "🏰 Штурм",
        "short": "Штурм",
    },
    {
        "id": "arena_1v1",
        "name": "⚔️ Арена 1×1",
        "short": "Арена 1×1",
    },
    {
        "id": "arena_2v2",
        "name": "🤝 Арена 2×2",
        "short": "Арена 2×2",
    },
    {
        "id": "arena_3v3",
        "name": "🛡 Арена 3×3",
        "short": "Арена 3×3",
    },
    {
        "id": "gladiator_1v1",
        "name": "🏛 Гладиаторские бои 1×1",
        "short": "Гладиаторы 1×1",
    },
    {
        "id": "gladiator_2v2",
        "name": "🏛 Гладиаторские бои 2×2",
        "short": "Гладиаторы 2×2",
    },
    {
        "id": "gladiator_3v3",
        "name": "🏛 Гладиаторские бои 3×3",
        "short": "Гладиаторы 3×3",
    },
]


def get_mode(mode_id):
    for mode in TOURNAMENT_MODES:
        if mode["id"] == mode_id:
            return mode
    return None


def get_default_tournament_stats():
    return {
        mode["id"]: {
            "played": 0,
            "wins": 0,
        }
        for mode in TOURNAMENT_MODES
    }


def ensure_tournament_stats(player):
    stats = player.get("tournaments")
    if not isinstance(stats, dict):
        stats = {}

    defaults = get_default_tournament_stats()
    for mode_id, values in defaults.items():
        if mode_id not in stats or not isinstance(stats.get(mode_id), dict):
            stats[mode_id] = values.copy()
        else:
            stats[mode_id]["played"] = int(stats[mode_id].get("played", 0) or 0)
            stats[mode_id]["wins"] = int(stats[mode_id].get("wins", 0) or 0)

    player["tournaments"] = stats
    return stats


def get_total_tournament_played(player):
    stats = ensure_tournament_stats(player)
    return sum(int(item.get("played", 0) or 0) for item in stats.values())


def get_total_tournament_wins(player):
    stats = ensure_tournament_stats(player)
    return sum(int(item.get("wins", 0) or 0) for item in stats.values())


def update_level(player):
    xp = int(player.get("xp", 0) or 0)
    player["level"] = max(1, xp // 1000 + 1)


def add_tournament_result(users, participant_ids, winner_ids, mode_id):
    mode = get_mode(mode_id)
    if not mode:
        return []

    changed = []
    participant_ids = [int(uid) for uid in participant_ids]
    winner_ids = [int(uid) for uid in winner_ids]

    for user_id in participant_ids:
        if user_id not in users:
            continue

        player = users[user_id]
        stats = ensure_tournament_stats(player)
        stats[mode_id]["played"] += 1
        player["activity"] = int(player.get("activity", 0) or 0) + 2
        player["xp"] = int(player.get("xp", 0) or 0) + 100

        if user_id in winner_ids:
            stats[mode_id]["wins"] += 1
            player["activity"] = int(player.get("activity", 0) or 0) + 3
            player["xp"] = int(player.get("xp", 0) or 0) + 200

        update_level(player)
        changed.append(user_id)

    return changed


def render_tournament_stats(player):
    stats = ensure_tournament_stats(player)
    total_played = get_total_tournament_played(player)
    total_wins = get_total_tournament_wins(player)
    winrate = int((total_wins / total_played) * 100) if total_played else 0

    text = (
        "🏆 Турнирная статистика\n\n"
        f"🎮 Всего участий: {total_played}\n"
        f"🥇 Всего побед: {total_wins}\n"
        f"📈 Общий винрейт: {winrate}%\n\n"
    )

    for mode in TOURNAMENT_MODES:
        item = stats.get(mode["id"], {})
        played = int(item.get("played", 0) or 0)
        wins = int(item.get("wins", 0) or 0)
        mode_winrate = int((wins / played) * 100) if played else 0

        text += (
            f"{mode['name']}\n"
            f"🎮 Участий: {played}\n"
            f"🥇 Побед: {wins}\n"
            f"📈 Винрейт: {mode_winrate}%\n\n"
        )

    return text.strip()


def tournament_history_item(mode_id, participant_names, winner_names, actor_name):
    mode = get_mode(mode_id)
    mode_name = mode["name"] if mode else mode_id
    return {
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "mode": mode_name,
        "participants": participant_names,
        "winners": winner_names,
        "actor": actor_name,
    }