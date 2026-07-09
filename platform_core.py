from clan_database import (
    load_clans,
    get_clan,
    create_clan,
)


PLATFORM_OWNER_ID = 7816223649


SUBSCRIPTION_ACTIVE = "active"
SUBSCRIPTION_TRIAL = "trial"
SUBSCRIPTION_BLOCKED = "blocked"
SUBSCRIPTION_EXPIRED = "expired"


def is_platform_owner(user_id):
    return int(user_id) == int(PLATFORM_OWNER_ID)


def get_all_clans():
    return load_clans()


def get_clan_by_id(clan_id):
    return get_clan(clan_id)


def is_clan_owner(user_id, clan):
    if not clan:
        return False

    return int(clan.get("owner_id") or 0) == int(user_id)


def is_subscription_active(clan):
    if not clan:
        return False

    status = clan.get("subscription_status") or SUBSCRIPTION_ACTIVE

    return status in [
        SUBSCRIPTION_ACTIVE,
        SUBSCRIPTION_TRIAL,
    ]


def register_clan(name, owner_id, telegram_chat_id=None):
    return create_clan(
        name=name,
        owner_id=owner_id,
        telegram_chat_id=telegram_chat_id,
        settings={
            "features": {
                "warehouse": True,
                "tournaments": True,
                "achievements": True,
                "honor_awards": True,
                "admin_panel": False,
            }
        },
    )


def render_clan_card(clan):
    if not clan:
        return "⚠️ Клан не найден."

    status = clan.get("subscription_status") or "active"
    settings = clan.get("settings") or {}

    features = settings.get("features", {}) if isinstance(settings, dict) else {}

    return (
        "🏰 Клан\n\n"
        f"ID: {clan.get('id')}\n"
        f"Название: {clan.get('name')}\n"
        f"Владелец: {clan.get('owner_id')}\n"
        f"Telegram chat: {clan.get('telegram_chat_id')}\n"
        f"Подписка: {status}\n\n"
        "Функции:\n"
        f"📦 Склад: {'✅' if features.get('warehouse', True) else '❌'}\n"
        f"🏆 Турниры: {'✅' if features.get('tournaments', True) else '❌'}\n"
        f"🏅 Достижения: {'✅' if features.get('achievements', True) else '❌'}\n"
        f"🎖 Награды: {'✅' if features.get('honor_awards', True) else '❌'}\n"
        f"🌐 Админ-панель: {'✅' if features.get('admin_panel', False) else '❌'}"
    )


def render_clans_list(clans):
    if not clans:
        return "🏰 Кланы пока не созданы."

    text = "🏰 Все кланы платформы\n\n"

    for clan in clans:
        text += (
            f"ID: {clan.get('id')}\n"
            f"🏷 {clan.get('name')}\n"
            f"👑 Владелец: {clan.get('owner_id')}\n"
            f"💳 Статус: {clan.get('subscription_status')}\n"
            "━━━━━━━━━━━━━━\n"
        )

    return text.strip()