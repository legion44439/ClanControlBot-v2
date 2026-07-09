from telegram import Update
from telegram.ext import ContextTypes

from platform_core import (
    is_platform_owner,
    get_all_clans,
    register_clan,
    render_clans_list,
)

from keyboards import (
    platform_menu,
    get_main_menu,
)


async def handle_platform_create_clan(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
):
    user_id = update.message.from_user.id

    if not context.user_data.get("platform_create_clan"):
        return False

    if not is_platform_owner(user_id):
        context.user_data.pop("platform_create_clan", None)
        await update.message.reply_text("⛔ Нет доступа.")
        return True

    name = text.strip()

    if text == "⬅️ Назад":
        context.user_data.pop("platform_create_clan", None)
        await update.message.reply_text(
            "🛡 Панель платформы",
            reply_markup=platform_menu,
        )
        return True

    if len(name) < 2:
        await update.message.reply_text("⚠️ Название клана слишком короткое.")
        return True

    register_clan(name=name, owner_id=user_id)

    context.user_data.pop("platform_create_clan", None)

    await update.message.reply_text(
        f"✅ Клан создан.\n\n🏰 Название: {name}",
        reply_markup=platform_menu,
    )

    return True


async def handle_platform_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
):
    user_id = update.message.from_user.id

    platform_buttons = [
        "🛡 Платформа",
        "🏰 Кланы",
        "👥 Владельцы",
        "➕ Создать клан",
        "💳 Подписки",
        "📊 Статистика платформы",
        "🌐 Админ-панель",
        "⚙️ Настройки платформы",
        "⬅️ К платформе",
    ]

    if text not in platform_buttons:
        return False

    if not is_platform_owner(user_id):
        await update.message.reply_text("⛔ Нет доступа.")
        return True

    if text == "🛡 Платформа":
        await update.message.reply_text(
            "🛡 Панель владельца платформы\n\nВыберите действие:",
            reply_markup=platform_menu,
        )
        return True

    if text == "🏰 Кланы":
        clans = get_all_clans()
        await update.message.reply_text(render_clans_list(clans))
        return True

    if text == "➕ Создать клан":
        context.user_data["platform_create_clan"] = True
        await update.message.reply_text(
            "🏰 Создание нового клана\n\n"
            "Введите название клана:\n\n"
            "Для отмены нажмите ⬅️ Назад"
        )
        return True

    if text == "👥 Владельцы":
        clans = get_all_clans()

        if not clans:
            await update.message.reply_text("👥 Владельцев пока нет.")
            return True

        result = "👥 Владельцы кланов\n\n"

        for clan in clans:
            result += (
                f"🏰 {clan.get('name')}\n"
                f"👑 Owner ID: {clan.get('owner_id')}\n"
                "━━━━━━━━━━━━━━\n"
            )

        await update.message.reply_text(result)
        return True

    if text == "💳 Подписки":
        await update.message.reply_text(
            "💳 Подписки\n\n"
            "Система тарифов будет добавлена следующим этапом."
        )
        return True

    if text == "📊 Статистика платформы":
        clans = get_all_clans()

        active = 0
        blocked = 0
        expired = 0

        for clan in clans:
            status = clan.get("subscription_status") or "active"

            if status in ("active", "trial"):
                active += 1
            elif status == "blocked":
                blocked += 1
            elif status == "expired":
                expired += 1

        await update.message.reply_text(
            "📊 Статистика платформы\n\n"
            f"🏰 Всего кланов: {len(clans)}\n"
            f"🟢 Активных: {active}\n"
            f"🔴 Заблокированных: {blocked}\n"
            f"🟡 Истекших: {expired}"
        )
        return True

    if text == "🌐 Админ-панель":
        await update.message.reply_text(
            "🌐 Веб-админка\n\n"
            "Панель будет добавлена отдельным модулем."
        )
        return True

    if text == "⚙️ Настройки платформы":
        await update.message.reply_text(
            "⚙️ Настройки платформы\n\n"
            "Раздел в разработке."
        )
        return True

    if text == "⬅️ К платформе":
        await update.message.reply_text(
            "🛡 Панель владельца платформы",
            reply_markup=platform_menu,
        )
        return True

    return False