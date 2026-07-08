from datetime import datetime

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from database import (
    approved_users,
    pending_users,
    has_access,
    save_users,
    add_log,
    clan_log,
    warehouse,
    warehouse_requests,
    warehouse_history,
    save_warehouse,
    save_warehouse_requests,
    add_warehouse_history,
    is_leader,
    is_admin,
    can_manage_members,
    can_broadcast,
    can_confirm_warehouse,
)

from keyboards import (
    main_menu,
    guest_menu,
    clan_menu,
    warehouse_menu,
    warehouse_categories_menu,
    resources_menu,
    components_menu,
    weapons_menu,
    ammo_menu,
    armor_menu,
    tools_menu,
    raid_menu,
)

WAREHOUSE_CATEGORIES = {
    "🪨 Ресурсы": [
        "🪵 Древесина", "🪨 Камень", "⚫ Уголь", "🟡 Сера",
        "🔩 Металлические фрагменты", "⬛ МВК", "⚙️ Металлолом",
        "🦴 Кость", "🧥 Кожа", "🧴 Животный жир", "🧶 Ткань",
    ],
    "⚙️ Компоненты": [
        "🪢 Верёвка", "⛽ Топливо", "💥 Порох", "⚙️ Шестерни",
        "🔧 Металлическая труба", "🌀 Металлическая пружина", "🪡 Швейный набор",
    ],
    "🔫 Оружие": [
        "🔫 Револьвер", "🔫 Кустарный пистолет", "🔫 Desert Eagle", "🔫 Дробовик",
        "🔫 Охотничья винтовка", "🔫 Полуавтоматическая винтовка",
        "🔫 Штурмовая винтовка", "🔫 Пистолет-пулемёт", "🔫 Сигнальный пистолет",
        "🔫 Томпсон", "🔫 W94", "🔫 B51", "🏹 Деревянный лук", "🏹 Арбалет",
    ],
    "💣 Боеприпасы": [
        "🏹 Стрела", "🏹 Болт", "🔫 Пистолетный патрон", "🔫 5.56 винтовочный патрон",
        "🔫 Самодельный патрон", "🔫 Картечь 12 калибра", "⚪ Стальной шарик",
    ],
    "🛡 Броня": [
        "🪖 Деревянный шлем", "🪖 Костяной шлем", "🪖 Кожаный шлем",
        "🪖 Металлический шлем", "🦺 Деревянный нагрудник", "🦺 Костяной нагрудник",
        "🦺 Кожаный нагрудник", "🦺 Металлический нагрудник", "👖 Деревянная защита ног",
        "👖 Костяная защита ног", "👖 Кожаная защита ног", "👖 Металлическая защита ног",
        "👢 Деревянные сандалии", "👢 Костяная обувь", "👢 Кожаные сапоги",
        "👢 Металлические ботинки", "☢️ Антирадиационный костюм",
    ],
    "🛠 Инструменты": [
        "🪓 Каменный топор", "🪓 Топор", "⛏ Кирка", "🔥 Факел",
        "⛏ Камнекрушитель", "🪚 Пила-потрошитель", "🪚 Бензопила", "⛏ Бур",
    ],
}

WAREHOUSE_ITEMS = set()
for items in WAREHOUSE_CATEGORIES.values():
    WAREHOUSE_ITEMS.update(items)


def today():
    return datetime.now().strftime("%d.%m.%Y")


def now():
    return datetime.now().strftime("%d.%m.%Y %H:%M")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if has_access(user_id):
        await update.message.reply_text(
            "🏰 ClanControl Bot\n\nВыберите раздел:",
            reply_markup=main_menu
        )
    else:
        await update.message.reply_text(
            "🛡 Добро пожаловать!\n\n"
            "У тебя пока нет доступа.\n"
            "Чтобы войти в клан, подай заявку.",
            reply_markup=guest_menu
        )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    text = update.message.text.strip()
if context.user_data.get("state") == "warehouse_search":
    context.user_data.pop("state", None)

    query = text.lower()
    result = []

    for item, amount in warehouse.items():
        if query in item.lower():
            result.append(f"📦 {item} — {amount}")

    if result:
        await update.message.reply_text(
            "🔎 Найдено:\n\n" + "\n".join(result)
        )
    else:
        await update.message.reply_text("❌ Предмет не найден.")

    return
    if not has_access(user_id):
        await handle_guest(update, context, user, user_id, text)
        return

    if context.user_data.get("waiting_broadcast"):
        await handle_broadcast(update, context, user_id, text)
        return

    if context.user_data.get("waiting_warehouse_amount"):
        await handle_warehouse_amount(update, context, user_id, text)
        return

    if text == "👥 Клан":
        await update.message.reply_text(
            "👥 Раздел клана\n\nВыберите действие:",
            reply_markup=clan_menu
        )

    elif text == "👤 Мой профиль":
        data = approved_users.get(user_id)
        if not data:
            await update.message.reply_text("⚠️ Профиль не найден.")
            return

        if "joined" not in data:
            data["joined"] = today()
            save_users(approved_users)

        await update.message.reply_text(
            "👤 Профиль игрока\n\n"
            f"🎮 Ник: {data['name']}\n"
            f"🎖 Роль: {data['role']}\n"
            f"📅 В клане с: {data.get('joined', 'неизвестно')}\n"
            f"🏆 Активность: {data.get('activity', 0)}\n"
            f"💰 Взносы: {data.get('contribution', 0)}\n"
            f"🆔 Telegram ID: {user_id}"
        )

    elif text == "📋 Список участников":
        result = "👥 Участники клана:\n\n"
        for data in approved_users.values():
            result += f"{data['role']} {data['name']}\n📅 С нами с: {data.get('joined', 'неизвестно')}\n\n"
        await update.message.reply_text(result)

    elif text == "🎖 Изменить роль":
        if not can_manage_members(user_id):
            await update.message.reply_text("⛔ У тебя нет прав менять роли.")
            return

        keyboard = []
        for uid, data in approved_users.items():
            if not is_leader(uid):
                keyboard.append([InlineKeyboardButton(f"{data['name']} — {data['role']}", callback_data=f"select_role_user_{uid}")])

        if not keyboard:
            await update.message.reply_text("⚠️ Нет участников для изменения роли.")
            return

        await update.message.reply_text("🎖 Выбери участника:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "❌ Исключить участника":
        if not can_manage_members(user_id):
            await update.message.reply_text("⛔ У тебя нет прав исключать участников.")
            return

        keyboard = []
        for uid, data in approved_users.items():
            if not is_leader(uid):
                keyboard.append([InlineKeyboardButton(f"❌ {data['name']} — {data['role']}", callback_data=f"kick_user_{uid}")])

        if not keyboard:
            await update.message.reply_text("⚠️ Нет участников для исключения.")
            return

        await update.message.reply_text("❌ Выбери участника:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "📢 Рассылка клану":
        if not can_broadcast(user_id):
            await update.message.reply_text("⛔ У тебя нет прав делать рассылку.")
            return
        context.user_data["waiting_broadcast"] = True
        await update.message.reply_text("📢 Напиши текст рассылки.")

    elif text == "📜 Журнал клана":
        if not clan_log:
            await update.message.reply_text("📜 Журнал клана пока пуст.")
            return
        result = "📜 Журнал клана\n\n"
        for item in clan_log[-10:]:
            result += f"🕒 {item['date']}\n{item['text']}\n\n"
        await update.message.reply_text(result)

    elif text == "👑 Передать лидерство":
        if not is_leader(user_id):
            await update.message.reply_text("⛔ Только лидер может передать лидерство.")
            return

        keyboard = []
        for uid, data in approved_users.items():
            if uid != user_id:
                keyboard.append([InlineKeyboardButton(f"{data['name']} — {data['role']}", callback_data=f"transfer_leader_{uid}")])

        if not keyboard:
            await update.message.reply_text("⚠️ Некому передать лидерство.")
            return

        await update.message.reply_text("👑 Выбери нового лидера:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif text == "📦 Склад":
        await update.message.reply_text("📦 Склад клана\n\nВыберите действие:", reply_markup=warehouse_menu)

    elif text == "📥 Пополнить склад":
        context.user_data["warehouse_action"] = "add"
        await update.message.reply_text("📥 Пополнение склада\n\nВыбери категорию:", reply_markup=warehouse_categories_menu)

  elif text == "🔎 Поиск предмета" or text == "🔍 Поиск предмета":
    context.user_data["state"] = "warehouse_search"
    await update.message.reply_text(
        "🔍 Введите название предмета для поиска:"
    )
    return
  elif text == "📤 Списать со склада":
        context.user_data["warehouse_action"] = "remove"
        await update.message.reply_text("📤 Списание со склада\n\nВыбери категорию:", reply_markup=warehouse_categories_menu)

    elif text == "🪨 Ресурсы":
        await update.message.reply_text("🪨 Ресурсы\n\nВыбери предмет:", reply_markup=resources_menu)

    elif text == "⚙️ Компоненты":
        await update.message.reply_text("⚙️ Компоненты\n\nВыбери предмет:", reply_markup=components_menu)

    elif text == "🔫 Оружие":
        await update.message.reply_text("🔫 Оружие\n\nВыбери предмет:", reply_markup=weapons_menu)

    elif text == "💣 Боеприпасы":
        await update.message.reply_text("💣 Боеприпасы\n\nВыбери предмет:", reply_markup=ammo_menu)

    elif text == "🛡 Броня":
        await update.message.reply_text("🛡 Броня\n\nВыбери предмет:", reply_markup=armor_menu)

    elif text == "🛠 Инструменты":
        await update.message.reply_text("🛠 Инструменты\n\nВыбери предмет:", reply_markup=tools_menu)

    elif text == "⬅️ К категориям":
        await update.message.reply_text("📦 Выбери категорию:", reply_markup=warehouse_categories_menu)

    elif text in WAREHOUSE_ITEMS:
        context.user_data["warehouse_item"] = text
        context.user_data["waiting_warehouse_amount"] = True
        action = context.user_data.get("warehouse_action", "add")
        if action == "add":
            await update.message.reply_text(f"📥 Пополнение\n\nПредмет: {text}\n\nВведите количество:")
        else:
            await update.message.reply_text(f"📤 Списание\n\nПредмет: {text}\n\nВведите количество:")

    elif text == "📦 Остатки склада":
        await show_warehouse(update)

    elif text == "⏳ Ожидает подтверждения":
        if not warehouse_requests:
            await update.message.reply_text("⏳ Заявок на склад пока нет.")
            return
        result = "⏳ Заявки склада:\n\n"
        for i, req in enumerate(warehouse_requests, start=1):
            op = "📥 Пополнение" if req.get("type") == "add" else "📤 Списание"
            result += f"{i}. {op}\n👤 {req['player_name']}\n📦 {req['item']}: {req['amount']}\n\n"
        await update.message.reply_text(result)

    elif text == "📜 История склада":
        if not warehouse_history:
            await update.message.reply_text("📜 История склада пока пустая.")
            return
        result = "📜 История склада\n\n"
        for item in warehouse_history[-10:]:
            result += f"🕒 {item['date']}\n{item['text']}\n\n"
        await update.message.reply_text(result)

    elif text == "⚔️ Рейды":
        await update.message.reply_text("⚔️ Раздел рейдов\n\nВыберите цель:", reply_markup=raid_menu)

    elif text == "💣 Калькулятор рейда":
        await update.message.reply_text("💣 Выберите объект для расчёта.")

    elif text == "🧱 Каменная стена":
        await update.message.reply_text("🧱 Каменная стена\n\n💣 C4: 4 шт.\n🚀 РПГ: 8 шт.")

    elif text == "🚪 Железная дверь":
        await update.message.reply_text("🚪 Железная дверь\n\n💣 C4: 1-2 шт.\n🚀 РПГ: 2-3 шт.")

    elif text == "🏠 Шкаф":
        await update.message.reply_text("🏠 Шкаф\n\n💣 C4: 1 шт.\n🚀 РПГ: 1-2 шт.")

    elif text == "🪟 Люк":
        await update.message.reply_text("🪟 Люк\n\n💣 C4: 1-2 шт.\n🚀 РПГ: 2-3 шт.")

    elif text == "🛰 Разведка":
        await update.message.reply_text("🛰 Разведку скоро добавим.")

    elif text == "📊 Статистика":
        await update.message.reply_text("📊 Статистику скоро добавим.")

    elif text == "⚙️ Настройки":
        await update.message.reply_text("⚙️ Настройки скоро добавим.")

    elif text == "⬅️ Назад":
        await update.message.reply_text("🏰 Главное меню", reply_markup=main_menu)

    else:
        await update.message.reply_text("Выберите раздел через кнопки меню.")


async def show_warehouse(update: Update):
    if not warehouse:
        await update.message.reply_text("📦 Склад пока пуст.")
        return

    result = "📦 Остатки склада\n\n"
    known_items = set()

    for category_name, items in WAREHOUSE_CATEGORIES.items():
        lines = []
        for item in items:
            known_items.add(item)
            amount = warehouse.get(item, 0)
            if amount > 0:
                lines.append(f"• {item}: {amount}")
        if lines:
            result += f"{category_name}\n"
            result += "\n".join(lines)
            result += "\n\n"

    other_lines = []
    for item, amount in warehouse.items():
        if item not in known_items and amount > 0:
            other_lines.append(f"• {item}: {amount}")

    if other_lines:
        result += "📌 Другое\n"
        result += "\n".join(other_lines)
        result += "\n\n"

    if result == "📦 Остатки склада\n\n":
        result += "Склад пока пуст."

    await update.message.reply_text(result)


async def handle_warehouse_amount(update, context, user_id, text):
    context.user_data["waiting_warehouse_amount"] = False

    if not text.isdigit():
        await update.message.reply_text("⚠️ Количество должно быть числом.")
        return

    amount = int(text)
    if amount <= 0:
        await update.message.reply_text("⚠️ Количество должно быть больше 0.")
        return

    item = context.user_data.get("warehouse_item")
    request_type = context.user_data.get("warehouse_action", "add")

    if not item:
        await update.message.reply_text("⚠️ Предмет не выбран. Начни заново через склад.")
        return

    player_name = approved_users[user_id]["name"]
    request_id = len(warehouse_requests)

    warehouse_requests.append({
        "type": request_type,
        "player_id": user_id,
        "player_name": player_name,
        "item": item,
        "amount": amount,
        "date": now(),
    })
    save_warehouse_requests()

    action_text = "пополнение" if request_type == "add" else "списание"
    emoji = "📥" if request_type == "add" else "📤"

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"warehouse_confirm_{request_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"warehouse_deny_{request_id}"),
    ]])

    for uid in approved_users.keys():
        if can_confirm_warehouse(uid):
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=(
                        f"{emoji} Новая заявка на {action_text} склада\n\n"
                        f"👤 Игрок: {player_name}\n"
                        f"📦 Предмет: {item}\n"
                        f"🔢 Количество: {amount}\n\n"
                        "Подтвердить?"
                    ),
                    reply_markup=keyboard,
                )
            except Exception:
                pass

    await update.message.reply_text(
        f"✅ Заявка на {action_text} отправлена.\n\n📦 {item}: {amount}",
        reply_markup=warehouse_menu,
    )


async def handle_broadcast(update, context, user_id, text):
    if not can_broadcast(user_id):
        context.user_data["waiting_broadcast"] = False
        await update.message.reply_text("⛔ У тебя нет прав делать рассылку.")
        return

    context.user_data["waiting_broadcast"] = False
    sent = 0
    failed = 0

    for uid in approved_users.keys():
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 Объявление клана\n\n{text}")
            sent += 1
        except Exception:
            failed += 1

    sender = approved_users[user_id]["name"]
    add_log(f"📢 {sender} сделал рассылку клану.")
    await update.message.reply_text(f"✅ Рассылка завершена.\n\n📨 Отправлено: {sent}\n⚠️ Не доставлено: {failed}")


async def handle_guest(update, context, user, user_id, text):
    if text == "📝 Подать заявку":
        context.user_data["waiting_nick"] = True
        await update.message.reply_text("🎮 Введи свой игровой ник:")
        return

    if context.user_data.get("waiting_nick"):
        nick = text.strip()
        pending_users[user_id] = {
            "telegram_name": user.first_name,
            "username": user.username,
            "nick": nick,
        }
        context.user_data["waiting_nick"] = False

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"deny_{user_id}"),
        ]])

        username_text = f"@{user.username}" if user.username else "нет username"
        for uid in approved_users.keys():
            if is_admin(uid):
                try:
                    await context.bot.send_message(
                        chat_id=uid,
                        text=(
                            "📥 Новая заявка в клан\n\n"
                            f"👤 Telegram: {user.first_name}\n"
                            f"🔗 Username: {username_text}\n"
                            f"🆔 ID: {user_id}\n"
                            f"🎮 Ник: {nick}\n\n"
                            "Одобрить заявку?"
                        ),
                        reply_markup=keyboard,
                    )
                except Exception:
                    pass

        await update.message.reply_text("✅ Заявка отправлена руководству.")
        return

    await update.message.reply_text("⛔ Сначала подай заявку.", reply_markup=guest_menu)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    actor_id = query.from_user.id
    data = query.data

    if data.startswith("warehouse_confirm_"):
        await confirm_warehouse_request(query, context, actor_id, data)
        return

    if data.startswith("warehouse_deny_"):
        await deny_warehouse_request(query, context, actor_id, data)
        return

    if not is_admin(actor_id):
        await query.edit_message_text("⛔ У тебя нет прав использовать эти кнопки.")
        return

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
            "joined": today(),
            "activity": 0,
            "contribution": 0,
        }
        save_users(approved_users)
        add_log(f"✅ {nick} принят в клан.")
        await context.bot.send_message(chat_id=user_id, text="🎉 Твоя заявка одобрена!\n\nНапиши /start")
        await query.edit_message_text(f"✅ Заявка одобрена.\n\n🎮 Игрок: {nick}")

    elif data.startswith("deny_"):
        user_id = int(data.replace("deny_", ""))
        if user_id not in pending_users:
            await query.edit_message_text("⚠️ Заявка уже обработана.")
            return

        user_data = pending_users.pop(user_id)
        nick = user_data["nick"]
        add_log(f"❌ Заявка игрока {nick} отклонена.")
        await context.bot.send_message(chat_id=user_id, text="❌ Твоя заявка отклонена.")
        await query.edit_message_text(f"❌ Заявка отклонена.\n\n🎮 Игрок: {nick}")

    elif data.startswith("select_role_user_"):
        target_id = int(data.replace("select_role_user_", ""))
        keyboard = [
            [InlineKeyboardButton("⭐ Заместитель", callback_data=f"set_role_{target_id}_Заместитель")],
            [InlineKeyboardButton("🛡 Офицер", callback_data=f"set_role_{target_id}_Офицер")],
            [InlineKeyboardButton("⚔️ Боец", callback_data=f"set_role_{target_id}_Боец")],
            [InlineKeyboardButton("⛏ Фармер", callback_data=f"set_role_{target_id}_Фармер")],
            [InlineKeyboardButton("🏗 Строитель", callback_data=f"set_role_{target_id}_Строитель")],
            [InlineKeyboardButton("📦 Логист", callback_data=f"set_role_{target_id}_Логист")],
            [InlineKeyboardButton("🛰 Разведчик", callback_data=f"set_role_{target_id}_Разведчик")],
        ]
        await query.edit_message_text(
            f"🎖 Выбери новую роль для {approved_users[target_id]['name']}:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data.startswith("set_role_"):
        parts = data.split("_")
        target_id = int(parts[2])
        role_name = parts[3]
        roles = {
            "Заместитель": "⭐ Заместитель",
            "Офицер": "🛡 Офицер",
            "Боец": "⚔️ Боец",
            "Фармер": "⛏ Фармер",
            "Строитель": "🏗 Строитель",
            "Логист": "📦 Логист",
            "Разведчик": "🛰 Разведчик",
        }
        if is_leader(target_id):
            await query.edit_message_text("⛔ Роль лидера менять нельзя.")
            return

        old_role = approved_users[target_id]["role"]
        approved_users[target_id]["role"] = roles[role_name]
        save_users(approved_users)
        name = approved_users[target_id]["name"]
        actor = approved_users[actor_id]["name"]
        add_log(f"🎖 {actor} изменил роль {name}: {old_role} → {roles[role_name]}.")
        await query.edit_message_text(f"✅ Роль игрока {name} изменена на {roles[role_name]}.")

    elif data.startswith("kick_user_"):
        target_id = int(data.replace("kick_user_", ""))
        if is_leader(target_id):
            await query.edit_message_text("⛔ Лидера исключить нельзя.")
            return

        removed_name = approved_users[target_id]["name"]
        actor = approved_users[actor_id]["name"]
        del approved_users[target_id]
        save_users(approved_users)
        add_log(f"❌ {actor} исключил {removed_name} из клана.")
        await query.edit_message_text(f"❌ Игрок {removed_name} исключён из клана.")
        try:
            await context.bot.send_message(chat_id=target_id, text="❌ Ты был исключён из клана.")
        except Exception:
            pass

    elif data.startswith("transfer_leader_"):
        target_id = int(data.replace("transfer_leader_", ""))
        if not is_leader(actor_id):
            await query.edit_message_text("⛔ Только лидер может передать лидерство.")
            return

        old_leader_name = approved_users[actor_id]["name"]
        new_leader_name = approved_users[target_id]["name"]
        approved_users[actor_id]["role"] = "⭐ Заместитель"
        approved_users[target_id]["role"] = "👑 Лидер"
        save_users(approved_users)
        add_log(f"👑 {old_leader_name} передал лидерство игроку {new_leader_name}.")
        await query.edit_message_text(
            f"👑 Лидерство передано игроку {new_leader_name}.\n\n"
            f"{old_leader_name} теперь ⭐ Заместитель."
        )
        try:
            await context.bot.send_message(chat_id=target_id, text="👑 Тебе передали лидерство в клане!")
        except Exception:
            pass


async def confirm_warehouse_request(query, context, actor_id, data):
    if not can_confirm_warehouse(actor_id):
        await query.edit_message_text("⛔ У тебя нет прав подтверждать склад.")
        return

    request_id = int(data.replace("warehouse_confirm_", ""))
    if request_id >= len(warehouse_requests):
        await query.edit_message_text("⚠️ Заявка уже обработана.")
        return

    req = warehouse_requests[request_id]
    item = req["item"]
    amount = req["amount"]
    player_name = req["player_name"]
    actor_name = approved_users[actor_id]["name"]
    request_type = req.get("type", "add")

    if request_type == "add":
        warehouse[item] = warehouse.get(item, 0) + amount
        action_text = f"добавил {amount} {item}"
        result_text = f"📦 {item}: +{amount}\n📊 Теперь на складе: {warehouse[item]}"
    else:
        current_amount = warehouse.get(item, 0)
        if current_amount < amount:
            add_warehouse_history(
                f"❌ {actor_name} отклонил списание. "
                f"{player_name} хотел забрать {amount} {item}, "
                f"но на складе только {current_amount}."
            )
            await query.edit_message_text(
                f"❌ Списание невозможно!\n\n"
                f"📦 Ресурс: {item}\n"
                f"📊 На складе: {current_amount}\n"
                f"📤 Запрошено: {amount}\n\n"
                f"Склад не изменён."
            )
            del warehouse_requests[request_id]
            save_warehouse_requests()
            return

        warehouse[item] = current_amount - amount
        action_text = f"забрал {amount} {item}"
        result_text = f"📦 {item}: -{amount}\n📊 Осталось на складе: {warehouse[item]}"

    del warehouse_requests[request_id]
    save_warehouse()
    save_warehouse_requests()
    add_warehouse_history(f"✅ {actor_name} подтвердил: {player_name} {action_text}.")
    add_log(f"📦 {actor_name} подтвердил склад: {player_name} {action_text}.")

    await query.edit_message_text(
        f"✅ Заявка подтверждена.\n\n"
        f"👤 Игрок: {player_name}\n"
        f"{result_text}"
    )

    try:
        await context.bot.send_message(
            chat_id=req["player_id"],
            text=f"✅ Твоя заявка по складу подтверждена.\n\n{result_text}"
        )
    except Exception:
        pass


async def deny_warehouse_request(query, context, actor_id, data):
    if not can_confirm_warehouse(actor_id):
        await query.edit_message_text("⛔ У тебя нет прав отклонять заявки склада.")
        return

    request_id = int(data.replace("warehouse_deny_", ""))
    if request_id >= len(warehouse_requests):
        await query.edit_message_text("⚠️ Заявка уже обработана.")
        return

    req = warehouse_requests.pop(request_id)
    save_warehouse_requests()
    actor_name = approved_users[actor_id]["name"]
    action = "пополнение" if req.get("type") == "add" else "списание"

    add_warehouse_history(
        f"❌ {actor_name} отклонил {action}: "
        f"{req['player_name']} — {req['amount']} {req['item']}."
    )

    await query.edit_message_text(
        f"❌ Заявка отклонена.\n\n"
        f"👤 Игрок: {req['player_name']}\n"
        f"📦 {req['item']}: {req['amount']}"
    )

    try:
        await context.bot.send_message(
            chat_id=req["player_id"],
            text=f"❌ Твоя заявка по складу отклонена.\n\n📦 {req['item']}: {req['amount']}"
        )
    except Exception:
        pass
