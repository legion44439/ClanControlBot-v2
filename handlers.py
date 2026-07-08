from datetime import datetime

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from config import LEADER_ID
from database import approved_users, pending_users, has_access, save_users
from keyboards import main_menu, guest_menu, clan_menu, raid_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if has_access(user_id):
        await update.message.reply_text(
            "🏰 Добро пожаловать в ClanControl Bot!\n\nВыберите раздел:",
            reply_markup=main_menu
        )
    else:
        await update.message.reply_text(
            "🛡 Добро пожаловать в ClanControl Bot!\n\n"
            "У тебя пока нет доступа.\n"
            "Чтобы войти в клан, подай заявку.",
            reply_markup=guest_menu
        )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    text = update.message.text.strip()

    if not has_access(user_id):
        await handle_guest(update, context, user, user_id, text)
        return

    if text == "👥 Клан":
        await update.message.reply_text(
            "👥 Раздел клана\n\nВыберите действие:",
            reply_markup=clan_menu
        )

    elif text == "👤 Мой профиль":
        data = approved_users.get(user_id)

        if data:
            await update.message.reply_text(
                "👤 Профиль игрока\n\n"
                f"🎮 Ник: {data['name']}\n"
                f"🎖 Роль: {data['role']}\n"
                f"📅 В клане с: {data.get('joined', 'неизвестно')}\n"
                f"🏆 Активность: {data.get('activity', 0)}\n"
                f"💰 Взносы: {data.get('contribution', 0)}\n"
                f"🆔 Telegram ID: {user_id}"
            )
            return

        await update.message.reply_text("⚠️ Профиль не найден.")
        return

    elif text == "📋 Список участников":
        result = "👥 Участники клана:\n\n"

        for data in approved_users.values():
            result += f"{data['role']} {data['name']}\n"

        await update.message.reply_text(result)

    elif text == "🎖 Изменить роль":
        if user_id != LEADER_ID:
            await update.message.reply_text("⛔ Только лидер может менять роли.")
            return

        await update.message.reply_text(
            "🎖 Напиши команду:\n\n"
            "Офицер Ник\n"
            "Боец Ник\n"
            "Фармер Ник\n"
            "Строитель Ник\n"
            "Разведчик Ник\n\n"
            "Пример: Офицер Akame09"
        )

    elif text.startswith("Офицер "):
        await change_role(update, "🛡 Офицер", text.replace("Офицер ", "", 1))

    elif text.startswith("Боец "):
        await change_role(update, "⚔️ Боец", text.replace("Боец ", "", 1))

    elif text.startswith("Фармер "):
        await change_role(update, "⛏ Фармер", text.replace("Фармер ", "", 1))

    elif text.startswith("Строитель "):
        await change_role(update, "🏗 Строитель", text.replace("Строитель ", "", 1))

    elif text.startswith("Разведчик "):
        await change_role(update, "🛰 Разведчик", text.replace("Разведчик ", "", 1))

    elif text == "❌ Исключить участника":
        if user_id != LEADER_ID:
            await update.message.reply_text("⛔ Только лидер может исключать игроков.")
            return

        await update.message.reply_text(
            "❌ Напиши команду:\n\n"
            "кик Ник\n\n"
            "Пример: кик Akame09"
        )

    elif text.startswith("кик "):
        await kick_user(update, text.replace("кик ", "", 1))

    elif text == "⚔️ Рейды":
        await update.message.reply_text(
            "⚔️ Раздел рейдов\n\nВыберите цель для расчёта:",
            reply_markup=raid_menu
        )

    elif text == "💣 Калькулятор рейда":
        await update.message.reply_text(
            "💣 Выберите объект:\n"
            "🧱 Каменная стена\n"
            "🚪 Железная дверь\n"
            "🏠 Шкаф\n"
            "🪟 Люк"
        )

    elif text == "🧱 Каменная стена":
        await update.message.reply_text(
            "🧱 Каменная стена\n\n"
            "💣 C4: 4 шт.\n"
            "🚀 РПГ: 8 шт."
        )

    elif text == "🚪 Железная дверь":
        await update.message.reply_text(
            "🚪 Железная дверь\n\n"
            "💣 C4: 1-2 шт.\n"
            "🚀 РПГ: 2-3 шт."
        )

    elif text == "🏠 Шкаф":
        await update.message.reply_text(
            "🏠 Шкаф\n\n"
            "💣 C4: 1 шт.\n"
            "🚀 РПГ: 1-2 шт."
        )

    elif text == "🪟 Люк":
        await update.message.reply_text(
            "🪟 Люк\n\n"
            "💣 C4: 1-2 шт.\n"
            "🚀 РПГ: 2-3 шт."
        )

    elif text == "📦 Склад":
        await update.message.reply_text("📦 Скоро добавим учёт склада.")

    elif text == "🛰 Разведка":
        await update.message.reply_text("🛰 Скоро добавим разведку.")

    elif text == "📊 Статистика":
        await update.message.reply_text("📊 Скоро добавим статистику.")

    elif text == "⚙️ Настройки":
        await update.message.reply_text("⚙️ Скоро добавим настройки.")

    elif text == "⬅️ Назад":
        await update.message.reply_text(
            "🏰 Главное меню",
            reply_markup=main_menu
        )

    else:
        await update.message.reply_text("Выберите раздел через кнопки меню.")


async def handle_guest(update: Update, context: ContextTypes.DEFAULT_TYPE, user, user_id: int, text: str):
    if text == "📝 Подать заявку":
        context.user_data["waiting_nick"] = True
        await update.message.reply_text("🎮 Введи свой игровой ник:")
        return

    if context.user_data.get("waiting_nick"):
        nick = text.strip()

        pending_users[user_id] = {
            "telegram_name": user.first_name,
            "username": user.username,
            "nick": nick
        }

        context.user_data["waiting_nick"] = False

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"deny_{user_id}")
            ]
        ])

        username_text = f"@{user.username}" if user.username else "нет username"

        await context.bot.send_message(
            chat_id=LEADER_ID,
            text=(
                "📥 Новая заявка в клан\n\n"
                f"👤 Telegram: {user.first_name}\n"
                f"🔗 Username: {username_text}\n"
                f"🆔 ID: {user_id}\n"
                f"🎮 Ник: {nick}\n\n"
                "Одобрить заявку?"
            ),
            reply_markup=keyboard
        )

        await update.message.reply_text("✅ Заявка отправлена лидеру.")
        return

    await update.message.reply_text(
        "⛔ Сначала подай заявку.",
        reply_markup=guest_menu
    )


async def change_role(update: Update, new_role: str, nick: str):
    user_id = update.message.from_user.id

    if user_id != LEADER_ID:
        await update.message.reply_text("⛔ Только лидер может менять роли.")
        return

    nick = nick.strip()

    for uid, data in approved_users.items():
        if data["name"].lower() == nick.lower():
            if uid == LEADER_ID:
                await update.message.reply_text("⛔ Роль лидера менять нельзя.")
                return

            data["role"] = new_role
            save_users(approved_users)

            await update.message.reply_text(
                f"✅ Роль игрока {data['name']} изменена на {new_role}."
            )
            return

    await update.message.reply_text("⚠️ Игрок не найден.")


async def kick_user(update: Update, nick: str):
    user_id = update.message.from_user.id

    if user_id != LEADER_ID:
        await update.message.reply_text("⛔ Только лидер может исключать участников.")
        return

    nick = nick.strip()

    for uid, data in list(approved_users.items()):
        if data["name"].lower() == nick.lower():
            if uid == LEADER_ID:
                await update.message.reply_text("⛔ Лидера исключить нельзя.")
                return

            removed_name = data["name"]
            del approved_users[uid]
            save_users(approved_users)

            await update.message.reply_text(
                f"❌ Игрок {removed_name} исключён из клана."
            )
            return

    await update.message.reply_text("⚠️ Игрок не найден.")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != LEADER_ID:
        await query.edit_message_text("⛔ Только лидер может принимать заявки.")
        return

    data = query.data

    if data.startswith("approve_"):
        user_id = int(data.replace("approve_", ""))

        if user_id not in pending_users:
            await query.edit_message_text("⚠️ Заявка уже обработана.")
            return

        user_data = pending_users.pop(user_id)
        nick = user_data["nick"]

        approved_users[user_id] = {
            "name": nick,
            "role": "⚔️ Боец",
            "joined": datetime.now().strftime("%d.%m.%Y"),
            "activity": 0,
            "contribution": 0
        }

        save_users(approved_users)

        await context.bot.send_message(
            chat_id=user_id,
            text="🎉 Твоя заявка одобрена!\n\nНапиши /start"
        )

        await query.edit_message_text(
            f"✅ Заявка одобрена.\n\n🎮 Игрок: {nick}"
        )

    elif data.startswith("deny_"):
        user_id = int(data.replace("deny_", ""))

        if user_id not in pending_users:
            await query.edit_message_text("⚠️ Заявка уже обработана.")
            return

        user_data = pending_users.pop(user_id)
        nick = user_data["nick"]

        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Твоя заявка отклонена."
        )

        await query.edit_message_text(
            f"❌ Заявка отклонена.\n\n🎮 Игрок: {nick}"
        )