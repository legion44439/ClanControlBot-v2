from datetime import datetime


DATE_FORMAT = "%d.%m.%Y"


def _to_int(value, default=0):
    try:
        return int(value or default)
    except Exception:
        return default


def _joined_days(player):
    joined = player.get("joined")
    if not joined:
        return 0
    try:
        joined_date = datetime.strptime(joined, DATE_FORMAT)
        return max(0, (datetime.now() - joined_date).days)
    except Exception:
        return 0


def _progress_bar(current, target, size=10):
    if target <= 0:
        return "█" * size
    ratio = min(1, max(0, current / target))
    filled = int(ratio * size)
    return "█" * filled + "░" * (size - filled)


ACHIEVEMENTS = [
    # Стаж в клане
    {
        "id": "clan_first_step",
        "category": "🏅 Стаж в клане",
        "icon": "🥇",
        "name": "Первый шаг",
        "description": "Вступить в клан.",
        "points": 10,
        "target": 1,
        "progress": lambda p: 1 if p.get("joined") else 0,
    },
    {
        "id": "clan_first_role",
        "category": "🏅 Стаж в клане",
        "icon": "🎖",
        "name": "Первое повышение",
        "description": "Получить первую роль.",
        "points": 15,
        "target": 1,
        "progress": lambda p: 1 if p.get("role") and p.get("role") != "⚔️ Боец" else 0,
    },
    {
        "id": "clan_7_days",
        "category": "🏅 Стаж в клане",
        "icon": "🌱",
        "name": "Новенький",
        "description": "Пробыть в клане 7 дней.",
        "points": 10,
        "target": 7,
        "progress": _joined_days,
    },
    {
        "id": "clan_15_days",
        "category": "🏅 Стаж в клане",
        "icon": "🛡",
        "name": "Бывалый",
        "description": "Пробыть в клане 15 дней.",
        "points": 15,
        "target": 15,
        "progress": _joined_days,
    },
    {
        "id": "clan_30_days",
        "category": "🏅 Стаж в клане",
        "icon": "⚔️",
        "name": "Ветеран I",
        "description": "Пробыть в клане 30 дней.",
        "points": 25,
        "target": 30,
        "progress": _joined_days,
    },
    {
        "id": "clan_50_days",
        "category": "🏅 Стаж в клане",
        "icon": "⚔️",
        "name": "Ветеран II",
        "description": "Пробыть в клане 50 дней.",
        "points": 35,
        "target": 50,
        "progress": _joined_days,
    },
    {
        "id": "clan_75_days",
        "category": "🏅 Стаж в клане",
        "icon": "💪",
        "name": "Несгибаемый",
        "description": "Пробыть в клане 75 дней.",
        "points": 50,
        "target": 75,
        "progress": _joined_days,
    },
    {
        "id": "clan_100_days",
        "category": "🏅 Стаж в клане",
        "icon": "🤝",
        "name": "Верный клану",
        "description": "Пробыть в клане 100 дней.",
        "points": 75,
        "target": 100,
        "progress": _joined_days,
    },
    {
        "id": "clan_365_days",
        "category": "🏅 Стаж в клане",
        "icon": "👑",
        "name": "Живая легенда",
        "description": "Пробыть в клане 365 дней.",
        "points": 150,
        "target": 365,
        "progress": _joined_days,
    },

    # Склад
    {
        "id": "warehouse_loader",
        "category": "📦 Склад",
        "icon": "📦",
        "name": "Грузчик",
        "description": "Передать на склад 10 000 ресурсов.",
        "points": 10,
        "target": 10000,
        "progress": lambda p: _to_int(p.get("warehouse_added")),
    },
    {
        "id": "warehouse_keeper",
        "category": "📦 Склад",
        "icon": "📦",
        "name": "Складовщик",
        "description": "Передать на склад 50 000 ресурсов.",
        "points": 25,
        "target": 50000,
        "progress": lambda p: _to_int(p.get("warehouse_added")),
    },
    {
        "id": "warehouse_supplier",
        "category": "📦 Склад",
        "icon": "🏗",
        "name": "Снабженец",
        "description": "Передать на склад 100 000 ресурсов.",
        "points": 50,
        "target": 100000,
        "progress": lambda p: _to_int(p.get("warehouse_added")),
    },
    {
        "id": "warehouse_quartermaster",
        "category": "📦 Склад",
        "icon": "🚚",
        "name": "Интендант",
        "description": "Передать на склад 250 000 ресурсов.",
        "points": 75,
        "target": 250000,
        "progress": lambda p: _to_int(p.get("warehouse_added")),
    },
    {
        "id": "warehouse_treasurer",
        "category": "📦 Склад",
        "icon": "🏛",
        "name": "Казначей",
        "description": "Передать на склад 500 000 ресурсов.",
        "points": 100,
        "target": 500000,
        "progress": lambda p: _to_int(p.get("warehouse_added")),
    },
    {
        "id": "warehouse_benefactor",
        "category": "📦 Склад",
        "icon": "💎",
        "name": "Благодетель клана",
        "description": "Передать на склад 1 000 000 ресурсов.",
        "points": 150,
        "target": 1000000,
        "progress": lambda p: _to_int(p.get("warehouse_added")),
    },
    {
        "id": "warehouse_pillar",
        "category": "📦 Склад",
        "icon": "👑",
        "name": "Опора клана",
        "description": "Передать на склад 5 000 000 ресурсов.",
        "points": 250,
        "target": 5000000,
        "progress": lambda p: _to_int(p.get("warehouse_added")),
    },
    {
        "id": "warehouse_legend",
        "category": "📦 Склад",
        "icon": "🌍",
        "name": "Легенда снабжения",
        "description": "Передать на склад 10 000 000 ресурсов.",
        "points": 500,
        "target": 10000000,
        "progress": lambda p: _to_int(p.get("warehouse_added")),
    },

    # Активность
    {
        "id": "activity_50",
        "category": "🔥 Активность",
        "icon": "🔥",
        "name": "Активный участник",
        "description": "Набрать 50 активности.",
        "points": 10,
        "target": 50,
        "progress": lambda p: _to_int(p.get("activity")),
    },
    {
        "id": "activity_200",
        "category": "🔥 Активность",
        "icon": "⚡",
        "name": "Двигатель клана",
        "description": "Набрать 200 активности.",
        "points": 25,
        "target": 200,
        "progress": lambda p: _to_int(p.get("activity")),
    },
    {
        "id": "activity_500",
        "category": "🔥 Активность",
        "icon": "🌋",
        "name": "Незаменимый",
        "description": "Набрать 500 активности.",
        "points": 50,
        "target": 500,
        "progress": lambda p: _to_int(p.get("activity")),
    },
    {
        "id": "activity_1000",
        "category": "🔥 Активность",
        "icon": "💎",
        "name": "Опора клана",
        "description": "Набрать 1000 активности.",
        "points": 100,
        "target": 1000,
        "progress": lambda p: _to_int(p.get("activity")),
    },
    {
        "id": "activity_2500",
        "category": "🔥 Активность",
        "icon": "❤️",
        "name": "Сердце клана",
        "description": "Набрать 2500 активности.",
        "points": 250,
        "target": 2500,
        "progress": lambda p: _to_int(p.get("activity")),
    },
    {
        "id": "activity_5000",
        "category": "🔥 Активность",
        "icon": "👑",
        "name": "Легенда активности",
        "description": "Набрать 5000 активности.",
        "points": 500,
        "target": 5000,
        "progress": lambda p: _to_int(p.get("activity")),
    },

    # Роли
    {
        "id": "role_officer",
        "category": "🎖 Должности",
        "icon": "🛡",
        "name": "Офицер",
        "description": "Получить роль офицера.",
        "points": 25,
        "target": 1,
        "progress": lambda p: 1 if p.get("role") == "🛡 Офицер" else 0,
    },
    {
        "id": "role_deputy",
        "category": "🎖 Должности",
        "icon": "⭐",
        "name": "Правая рука",
        "description": "Получить роль заместителя.",
        "points": 50,
        "target": 1,
        "progress": lambda p: 1 if p.get("role") == "⭐ Заместитель" else 0,
    },
    {
        "id": "role_leader",
        "category": "🎖 Должности",
        "icon": "👑",
        "name": "Лидер",
        "description": "Стать лидером клана.",
        "points": 100,
        "target": 1,
        "progress": lambda p: 1 if p.get("role") == "👑 Лидер" else 0,
    },
]


def achievement_ids(player):
    achievements = player.get("achievements") or []
    if isinstance(achievements, str):
        return [achievements]
    return list(achievements)


def get_unlocked_achievement_ids(player):
    unlocked = []
    for ach in ACHIEVEMENTS:
        progress = ach["progress"](player)
        if progress >= ach["target"]:
            unlocked.append(ach["id"])
    for ach_id in achievement_ids(player):
        if ach_id not in unlocked:
            unlocked.append(ach_id)
    return unlocked


def sync_achievements(player):
    old = set(achievement_ids(player))
    new = set(get_unlocked_achievement_ids(player))
    gained = [ach for ach in ACHIEVEMENTS if ach["id"] in new and ach["id"] not in old]
    player["achievements"] = list(new)
    return gained


def get_achievement_points(player):
    ids = set(get_unlocked_achievement_ids(player))
    return sum(ach["points"] for ach in ACHIEVEMENTS if ach["id"] in ids)


def render_achievements(player):
    unlocked_ids = set(get_unlocked_achievement_ids(player))
    total = len(ACHIEVEMENTS)
    unlocked_count = len([ach for ach in ACHIEVEMENTS if ach["id"] in unlocked_ids])
    percent = int((unlocked_count / total) * 100) if total else 0
    points = get_achievement_points(player)

    text = (
        "🏆 Достижения игрока\n\n"
        f"Получено: {unlocked_count} / {total} ({percent}%)\n"
        f"Очки достижений: {points}\n"
        f"{_progress_bar(unlocked_count, total, 12)}\n\n"
    )

    current_category = None
    for ach in ACHIEVEMENTS:
        if ach["category"] != current_category:
            current_category = ach["category"]
            text += f"\n{current_category}\n"

        progress = ach["progress"](player)
        target = ach["target"]
        is_unlocked = ach["id"] in unlocked_ids
        status = "✅" if is_unlocked else "🔒"
        progress_text = f"{min(progress, target)} / {target}" if target > 1 else ach["description"]
        bar = _progress_bar(progress, target, 8) if not is_unlocked and target > 1 else ""

        text += f"{status} {ach['icon']} {ach['name']} — {ach['description']}\n"
        if not is_unlocked and target > 1:
            text += f"   Прогресс: {progress_text} {bar}\n"

    return text.strip()



def get_achievement_categories():
    """Возвращает список категорий достижений в правильном порядке."""
    categories = []
    for ach in ACHIEVEMENTS:
        category = ach["category"]
        if category not in categories:
            categories.append(category)
    return categories


def achievement_summary(player):
    unlocked_ids = set(get_unlocked_achievement_ids(player))
    total = len(ACHIEVEMENTS)
    unlocked_count = len([ach for ach in ACHIEVEMENTS if ach["id"] in unlocked_ids])
    percent = int((unlocked_count / total) * 100) if total else 0
    points = get_achievement_points(player)

    return {
        "total": total,
        "unlocked": unlocked_count,
        "percent": percent,
        "points": points,
        "bar": _progress_bar(unlocked_count, total, 12),
    }


def render_achievements_overview(player):
    summary = achievement_summary(player)
    categories = get_achievement_categories()
    unlocked_ids = set(get_unlocked_achievement_ids(player))

    text = (
        "🏆 Достижения игрока\n\n"
        f"Получено: {summary['unlocked']} / {summary['total']} ({summary['percent']}%)\n"
        f"Очки достижений: {summary['points']}\n"
        f"{summary['bar']}\n\n"
        "📂 Категории:\n"
    )

    for category in categories:
        category_items = [ach for ach in ACHIEVEMENTS if ach["category"] == category]
        category_unlocked = len([ach for ach in category_items if ach["id"] in unlocked_ids])
        text += f"• {category}: {category_unlocked} / {len(category_items)}\n"

    text += "\nВыберите категорию кнопками ниже."
    return text.strip()


def render_achievement_category(player, category):
    unlocked_ids = set(get_unlocked_achievement_ids(player))
    items = [ach for ach in ACHIEVEMENTS if ach["category"] == category]

    if not items:
        return "⚠️ Категория не найдена."

    unlocked_count = len([ach for ach in items if ach["id"] in unlocked_ids])
    text = f"{category}\n\nПолучено: {unlocked_count} / {len(items)}\n\n"

    for ach in items:
        progress = ach["progress"](player)
        target = ach["target"]
        is_unlocked = ach["id"] in unlocked_ids
        status = "✅" if is_unlocked else "🔒"

        text += f"{status} {ach['icon']} {ach['name']}\n"
        text += f"   {ach['description']}\n"
        text += f"   🏅 Очки: {ach['points']}\n"

        if not is_unlocked and target > 1:
            current = min(progress, target)
            text += f"   Прогресс: {current} / {target}\n"
            text += f"   {_progress_bar(progress, target, 10)}\n"

        text += "\n"

    return text.strip()


def render_new_achievement_message(achievement):
    return (
        "🎉 Новое достижение!\n\n"
        f"{achievement['icon']} {achievement['name']}\n\n"
        f"📖 {achievement['description']}\n"
        f"🏅 +{achievement['points']} очков достижений\n"
        "🔥 +2 активности"
    )
