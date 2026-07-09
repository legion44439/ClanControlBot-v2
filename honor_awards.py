from view_utils import progress_bar


HONOR_AWARDS = [
    {
        "id": "season_champion",
        "icon": "🥇",
        "name": "Чемпион сезона",
        "description": "За победу и выдающийся результат в сезоне.",
    },
    {
        "id": "best_fighter",
        "icon": "⚔️",
        "name": "Лучший боец",
        "description": "За отличные боевые результаты и силу в сражениях.",
    },
    {
        "id": "undefeated",
        "icon": "🛡",
        "name": "Непобедимый",
        "description": "За серию побед и уверенную игру.",
    },
    {
        "id": "tournament_winner",
        "icon": "🏆",
        "name": "Победитель турнира",
        "description": "За победу в клановом турнире.",
    },
    {
        "id": "clan_hero",
        "icon": "👑",
        "name": "Герой клана",
        "description": "За важный поступок и вклад в судьбу клана.",
    },
    {
        "id": "clan_legend",
        "icon": "💎",
        "name": "Легенда клана",
        "description": "Одна из высших почётных наград клана.",
    },
    {
        "id": "honor_veteran",
        "icon": "🎖",
        "name": "Почётный ветеран",
        "description": "За долгую службу и верность клану.",
    },
    {
        "id": "loyalty",
        "icon": "🤝",
        "name": "Верность клану",
        "description": "За надёжность, поддержку и преданность коллективу.",
    },
    {
        "id": "best_supplier",
        "icon": "📦",
        "name": "Лучший снабженец",
        "description": "За огромный вклад в склад и обеспечение клана.",
    },
    {
        "id": "best_builder",
        "icon": "🏗",
        "name": "Лучший строитель",
        "description": "За развитие базы и строительную помощь клану.",
    },
    {
        "id": "supply_master",
        "icon": "⚒",
        "name": "Мастер обеспечения",
        "description": "За стабильную помощь ресурсами и предметами.",
    },
    {
        "id": "most_active",
        "icon": "🔥",
        "name": "Самый активный",
        "description": "За высокую активность и постоянное участие в жизни клана.",
    },
    {
        "id": "player_month",
        "icon": "⭐",
        "name": "Игрок месяца",
        "description": "За лучший общий вклад в течение месяца.",
    },
    {
        "id": "clan_pride",
        "icon": "🌟",
        "name": "Гордость клана",
        "description": "За примерное поведение, пользу и уважение внутри клана.",
    },
]


def get_honor_award(award_id):
    for award in HONOR_AWARDS:
        if award["id"] == award_id:
            return award
    return None


def get_player_honor_award_ids(player):
    awards = player.get("honor_awards") or []
    result = []

    if not isinstance(awards, list):
        return result

    for item in awards:
        if isinstance(item, dict):
            award_id = item.get("id")
        else:
            award_id = str(item)

        if award_id and award_id not in result:
            result.append(award_id)

    return result


def get_player_honor_award_records(player):
    awards = player.get("honor_awards") or []
    result = []

    if not isinstance(awards, list):
        return result

    for item in awards:
        if isinstance(item, dict):
            result.append(item)
        else:
            result.append({"id": str(item)})

    return result


def render_honor_awards_collection(player):
    received_ids = set(get_player_honor_award_ids(player))
    total = len(HONOR_AWARDS)
    received = len(received_ids)

    text = (
        "🏅 Почётные награды\n\n"
        f"Получено: {received} / {total}\n"
        f"{progress_bar(received, total, 10)}\n\n"
    )

    current_category = None
    categories = {
        "season_champion": "🏆 Боевые",
        "best_fighter": "🏆 Боевые",
        "undefeated": "🏆 Боевые",
        "tournament_winner": "🏆 Боевые",
        "clan_hero": "👑 Клановые",
        "clan_legend": "👑 Клановые",
        "honor_veteran": "👑 Клановые",
        "loyalty": "👑 Клановые",
        "best_supplier": "📦 Склад",
        "best_builder": "📦 Склад",
        "supply_master": "📦 Склад",
        "most_active": "🔥 Активность",
        "player_month": "🔥 Активность",
        "clan_pride": "🔥 Активность",
    }

    for award in HONOR_AWARDS:
        category = categories.get(award["id"], "🏅 Другое")
        if category != current_category:
            current_category = category
            text += f"\n{category}\n"

        status = "✅" if award["id"] in received_ids else "🔒"
        text += f"{status} {award['icon']} {award['name']} — {award['description']}\n"

    return text.strip()


def render_honor_awards_short(player):
    records = get_player_honor_award_records(player)
    if not records:
        return "Пока нет"

    lines = []
    for record in records[-3:]:
        award = get_honor_award(record.get("id"))
        if award:
            lines.append(f"{award['icon']} {award['name']}")

    if not lines:
        return "Пока нет"

    extra = len(records) - len(lines)
    if extra > 0:
        lines.append(f"…и ещё {extra}")

    return "\n".join(lines)
