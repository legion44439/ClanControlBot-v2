from datetime import datetime
import random

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
    save_tournament_record,
    load_tournament_history,
    add_tournament_history,
    tournament_history,
    is_leader,
    is_admin,
    can_manage_members,
    can_broadcast,
    can_confirm_warehouse,
)

from achievements import (
    sync_achievements,
    render_achievements,
    render_achievements_overview,
    render_achievement_category,
    render_new_achievement_message,
    get_achievement_categories,
    get_achievement_points,
)


from tournaments import (
    TOURNAMENT_MODES,
    add_tournament_result,
    render_tournament_stats,
    tournament_history_item,
)

from view_utils import safe_int
from honor_awards import (
    HONOR_AWARDS,
    get_honor_award,
    get_player_honor_award_ids,
    render_honor_awards_collection,
)
from profile_card import render_profile_card

from platform_core import (
    is_platform_owner,
    get_all_clans,
    register_clan,
    render_clans_list,
)

from platform_handlers import (
    handle_platform_menu,
    handle_platform_create_clan,
)

from keyboards import (
    get_main_menu,
    main_menu,
    guest_menu,
    clan_menu,
    honor_awards_menu,
    warehouse_menu,
    warehouse_categories_menu,
    resources_menu,
    components_menu,
    weapons_menu,
    ammo_menu,
    armor_menu,
    tools_menu,
    raid_menu,
    tournament_menu,
    tournament_modes_menu,
    tournament_bracket_size_menu,
    platform_menu,
    platform_clan_menu,
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



def update_player_achievements(user_id):
    if user_id not in approved_users:
        return []

    gained = sync_achievements(approved_users[user_id])

    if gained:
        approved_users[user_id]["activity"] = (
            int(approved_users[user_id].get("activity", 0) or 0) + len(gained) * 2
        )

    save_users(approved_users)
    return gained


async def send_achievement_notifications(context, chat_id, gained):
    if not gained:
        return

    for achievement in gained:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=render_new_achievement_message(achievement),
            )
        except Exception:
            pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if has_access(user_id):
        await update.message.reply_text(
            "🏰 ClanControl Bot\n\nВыберите раздел:",
            reply_markup=get_main_menu(user_id),
        )
    else:
        await update.message.reply_text(
            "🛡 Добро пожаловать!\n\n"
            "У тебя пока нет доступа.\n"
            "Чтобы войти в клан, подай заявку.",
            reply_markup=guest_menu,
        )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    text = update.message.text.strip()

    if await handle_platform_create_clan(update, context, text):
        return

    if await handle_platform_menu(update, context, text):
        return

    # ===== Редактирование профиля =====
    edit_profile = context.user_data.get("edit_profile")
    if edit_profile:
        if user_id not in approved_users:
            context.user_data.pop("edit_profile", None)
            await update.message.reply_text("⚠️ Профиль не найден.")
            return

        if edit_profile == "game_nick":
            approved_users[user_id]["name"] = text
            save_users(approved_users)
            context.user_data.pop("edit_profile", None)

            await update.message.reply_text(
                f"✅ Игровой ник изменён.\n\n🎮 Новый ник: {text}"
            )
            return

        if edit_profile == "telegram_account":
            telegram_account = text.strip()
            if telegram_account.lower() in ("нет", "-", "не указан"):
                telegram_account = "не указан"
            elif telegram_account and not telegram_account.startswith("@"):
                telegram_account = f"@{telegram_account}"

            approved_users[user_id]["telegram_account"] = telegram_account
            save_users(approved_users)
            context.user_data.pop("edit_profile", None)

            await update.message.reply_text(
                f"✅ Telegram аккаунт изменён.\n\n📨 {telegram_account}"
            )
            return

        if edit_profile == "telegram_name":
            approved_users[user_id]["telegram_name"] = text
            save_users(approved_users)
            context.user_data.pop("edit_profile", None)

            await update.message.reply_text(
                f"✅ Ник в Telegram изменён.\n\n👤 {text}"
            )
            return

    # ===== Поиск предмета на складе =====
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

    if context.user_data.get("waiting_create_clan"):
        if not is_platform_owner(user_id):
            context.user_data.pop("waiting_create_clan", None)
            await update.message.reply_text("⛔ Нет доступа.")
            return

        clan_name = text.strip()
        if not clan_name:
            await update.message.reply_text("⚠️ Название клана не может быть пустым.")
            return

        register_clan(name=clan_name, owner_id=user_id)
        context.user_data.pop("waiting_create_clan", None)

        await update.message.reply_text(
            f"✅ Клан создан.\n\n🏰 Название: {clan_name}",
            reply_markup=platform_menu,
        )
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

        if "telegram_account" not in data:
            username = update.effective_user.username
            data["telegram_account"] = f"@{username}" if username else "не указан"

        if "telegram_name" not in data:
            data["telegram_name"] = update.effective_user.full_name or "не указан"

        update_player_achievements(user_id)
        achievement_points = get_achievement_points(data)

        keyboard_rows = [
            [InlineKeyboardButton("✏️ Изменить данные", callback_data="edit_profile")],
            [InlineKeyboardButton("🏆 Достижения", callback_data="profile_achievements")],
            [InlineKeyboardButton("🏅 Почётные награды", callback_data="profile_honor_awards")],
            [InlineKeyboardButton("📊 Моя статистика", callback_data="profile_stats")],
            [InlineKeyboardButton("🏆 Турниры", callback_data="tournaments_menu")],
        ]

        if can_manage_members(user_id):
            keyboard_rows.append([
                InlineKeyboardButton("🎖 Выдать награду", callback_data="honor_give_menu")
            ])

        keyboard = InlineKeyboardMarkup(keyboard_rows)

        await update.message.reply_text(
            render_profile_card(data, user_id, achievement_points),
            reply_markup=keyboard,
        )

    elif text == "📋 Список участников":
        if not approved_users:
            await update.message.reply_text("👥 Список участников пуст.")
            return

        result = "📋 Список участников клана\n\n"

        for uid, data in approved_users.items():
            result += (
                f"👤 Игрок: {data.get('name', 'не указан')}\n"
                f"📨 Telegram аккаунт: {data.get('telegram_account', 'не указан')}\n"
                f"🪪 Ник в Telegram: {data.get('telegram_name', 'не указан')}\n"
                f"🎖 Роль: {data.get('role', 'не указана')}\n"
                f"📅 В клане с: {data.get('joined', 'неизвестно')}\n"
                f"🏆 Активность: {data.get('activity', 0)}\n"
                f"💰 Взносы: {data.get('contribution', 0)}\n"
                f"📦 Передано на склад: {data.get('warehouse_added', 0)}\n"
                f"📤 Получено со склада: {data.get('warehouse_taken', 0)}\n"
                f"⭐ Уровень: {data.get('level', 1)}\n"
                f"💎 Опыт: {data.get('xp', 0)}\n"
                f"🆔 Telegram ID: {uid}\n"
                f"━━━━━━━━━━━━━━\n"
            )

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

    elif text == "🏅 Почётные награды":
        if can_manage_members(user_id):
            keyboard = []
            for uid, player in approved_users.items():
                keyboard.append([
                    InlineKeyboardButton(
                        f"{player.get('role', '⚔️ Боец')} {player.get('name', 'Игрок')}",
                        callback_data=f"honor_target_{uid}"
                    )
                ])

            await update.message.reply_text(
                "🎖 Выберите игрока для награждения:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(render_honor_awards_collection(approved_users.get(user_id, {})))

    elif text == "📦 Склад":
        await update.message.reply_text("📦 Склад клана\n\nВыберите действие:", reply_markup=warehouse_menu)

    elif text == "📥 Пополнить склад":
        context.user_data["warehouse_action"] = "add"
        await update.message.reply_text("📥 Пополнение склада\n\nВыбери категорию:", reply_markup=warehouse_categories_menu)

    elif text in ("🔎 Поиск предмета", "🔍 Поиск предмета"):
        context.user_data["state"] = "warehouse_search"
        await update.message.reply_text("🔎 Введите название предмета:")
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

    elif text == "🏆 Турниры":
        await update.message.reply_text(
            "🏆 Турниры\n\nВыберите действие:",
            reply_markup=tournament_menu
        )

    elif text in ("🏅 Турнирная сетка", "🎲 Жеребьёвка"):
        if not can_manage_members(user_id):
            await update.message.reply_text(
                "⛔ Создавать турнирную сетку может только лидер или заместитель."
            )
            return

        context.user_data["bracket_create"] = {
            "size": None,
            "participants": [],
        }

        await update.message.reply_text(
            "🏅 Турнирная сетка\n\n"
            "Выберите размер сетки:",
            reply_markup=tournament_bracket_size_menu
        )
        return

    elif text in ("4 участника", "8 участников", "16 участников", "32 участника"):
        if not can_manage_members(user_id):
            await update.message.reply_text("⛔ Нет прав.")
            return

        size = int(text.split()[0])
        context.user_data["bracket_create"] = {
            "size": size,
            "participants": [],
        }

        await send_bracket_participants_menu(update, context)
        return

    elif text == "📊 Турнирная статистика":
        await update.message.reply_text(render_tournament_stats(approved_users.get(user_id, {})))

    elif text == "📜 История турниров":
        await update.message.reply_text(
            "📜 История турниров\n\n"
            "История турниров будет добавлена следующим этапом."
        )

    elif text == "➕ Добавить результат турнира":
        if not can_manage_members(user_id):
            await update.message.reply_text(
                "⛔ Добавлять результаты турниров может только лидер или заместитель."
            )
            return

        keyboard = []
        for index, mode in enumerate(TOURNAMENT_MODES):
            keyboard.append([
                InlineKeyboardButton(mode["name"], callback_data=f"t_mode_{index}")
            ])

        await update.message.reply_text(
            "🏆 Добавление результата турнира\n\nВыберите режим:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

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
        total_players = len(approved_users)

        role_counts = {
            "👑 Лидер": 0,
            "⭐ Заместитель": 0,
            "🛡 Офицер": 0,
            "⚔️ Боец": 0,
            "⛏ Фармер": 0,
            "🏗 Строитель": 0,
            "📦 Логист": 0,
            "🛰 Разведчик": 0,
        }

        for data in approved_users.values():
            role = data.get("role", "")
            if role in role_counts:
                role_counts[role] += 1

        total_items = sum(int(amount or 0) for amount in warehouse.values())
        unique_items = len([amount for amount in warehouse.values() if int(amount or 0) > 0])

        top_players = sorted(
            approved_users.values(),
            key=lambda player: (
                int(player.get("activity", 0) or 0),
                int(player.get("contribution", 0) or 0),
            ),
            reverse=True,
        )[:10]

        players_text = ""
        if top_players:
            for index, player in enumerate(top_players, start=1):
                players_text += (
                    f"{index}. {player.get('role', '⚔️ Боец')} "
                    f"{player.get('name', 'Игрок')} — "
                    f"активность: {player.get('activity', 0)}, "
                    f"взносы: {player.get('contribution', 0)}\n"
                )
        else:
            players_text = "Нет участников.\n"

        await update.message.reply_text(
            f"📊 Статистика клана\n\n"
            f"👥 Всего участников: {total_players}\n\n"
            f"👑 Лидеров: {role_counts['👑 Лидер']}\n"
            f"⭐ Заместителей: {role_counts['⭐ Заместитель']}\n"
            f"🛡 Офицеров: {role_counts['🛡 Офицер']}\n"
            f"⚔️ Бойцов: {role_counts['⚔️ Боец']}\n"
            f"⛏ Фармеров: {role_counts['⛏ Фармер']}\n"
            f"🏗 Строителей: {role_counts['🏗 Строитель']}\n"
            f"📦 Логистов: {role_counts['📦 Логист']}\n"
            f"🛰 Разведчиков: {role_counts['🛰 Разведчик']}\n\n"
            f"📦 Всего ресурсов на складе: {total_items}\n"
            f"📋 Разных предметов: {unique_items}\n"
            f"⏳ Заявок на подтверждении: {len(warehouse_requests)}\n"
            f"📜 Записей в истории склада: {len(warehouse_history)}\n\n"
            f"👤 Топ игроков по активности\n"
            f"{players_text}"
        )

    elif text == "🛡 Платформа":
        if not is_platform_owner(user_id):
            await update.message.reply_text("⛔ Нет доступа.")
            return

        await update.message.reply_text(
            "🛡 Панель владельца платформы\n\nВыберите действие:",
            reply_markup=platform_menu,
        )

    elif text == "🏰 Кланы":
        if not is_platform_owner(user_id):
            await update.message.reply_text("⛔ Нет доступа.")
            return

        clans = get_all_clans()
        await update.message.reply_text(render_clans_list(clans), reply_markup=platform_menu)

    elif text == "➕ Создать клан":
        if not is_platform_owner(user_id):
            await update.message.reply_text("⛔ Нет доступа.")
            return

        context.user_data["waiting_create_clan"] = True
        await update.message.reply_text(
            "➕ Создание нового клана\n\nВведите название клана:",
            reply_markup=platform_menu,
        )

    elif text == "👥 Владельцы":
        if not is_platform_owner(user_id):
            await update.message.reply_text("⛔ Нет доступа.")
            return

        clans = get_all_clans()
        owners = []
        for clan in clans:
            owners.append(
                f"🏰 {clan.get('name')}\n"
                f"👑 Владелец: {clan.get('owner_id')}\n"
                "━━━━━━━━━━━━━━"
            )

        await update.message.reply_text(
            "👥 Владельцы кланов\n\n" + ("\n".join(owners) if owners else "Пока нет кланов."),
            reply_markup=platform_menu,
        )

    elif text == "💳 Подписки":
        if not is_platform_owner(user_id):
            await update.message.reply_text("⛔ Нет доступа.")
            return

        clans = get_all_clans()
        lines = []
        for clan in clans:
            lines.append(
                f"🏰 {clan.get('name')} — {clan.get('subscription_status', 'active')}"
            )

        await update.message.reply_text(
            "💳 Подписки\n\n" + ("\n".join(lines) if lines else "Кланы пока не созданы."),
            reply_markup=platform_menu,
        )

    elif text == "📊 Статистика платформы":
        if not is_platform_owner(user_id):
            await update.message.reply_text("⛔ Нет доступа.")
            return

        clans = get_all_clans()
        await update.message.reply_text(
            "📊 Статистика платформы\n\n"
            f"🏰 Всего кланов: {len(clans)}\n"
            "💳 Подписки: скоро добавим расширенную аналитику.",
            reply_markup=platform_menu,
        )

    elif text == "🌐 Админ-панель":
        if not is_platform_owner(user_id):
            await update.message.reply_text("⛔ Нет доступа.")
            return

        await update.message.reply_text(
            "🌐 Веб-админка будет следующим этапом.\n\n"
            "Сейчас управление платформой уже доступно через Telegram.",
            reply_markup=platform_menu,
        )

    elif text == "⚙️ Настройки платформы":
        if not is_platform_owner(user_id):
            await update.message.reply_text("⛔ Нет доступа.")
            return

        await update.message.reply_text(
            "⚙️ Настройки платформы скоро добавим.",
            reply_markup=platform_menu,
        )

    elif text == "⬅️ К платформе":
        if not is_platform_owner(user_id):
            await update.message.reply_text("⛔ Нет доступа.")
            return

        await update.message.reply_text(
            "🛡 Панель владельца платформы",
            reply_markup=platform_menu,
        )

    elif text in ("👥 Участники клана", "📦 Склад клана", "🏆 Турниры клана", "🏅 Награды клана", "💳 Подписка клана", "🚫 Заблокировать клан"):
        if not is_platform_owner(user_id):
            await update.message.reply_text("⛔ Нет доступа.")
            return

        await update.message.reply_text(
            "⚙️ Управление выбранным кланом будет добавлено следующим этапом.",
            reply_markup=platform_clan_menu,
        )

    elif text == "⚙️ Настройки":
        await update.message.reply_text("⚙️ Настройки скоро добавим.")

    elif text == "⬅️ Назад":
        await update.message.reply_text("🏰 Главное меню", reply_markup=get_main_menu(user_id))

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



async def send_tournament_participants_menu(query, context):
    tournament = context.user_data.get("tournament_add", {})
    selected = set(tournament.get("participants", []))

    keyboard = []
    for uid, data in approved_users.items():
        mark = "✅" if uid in selected else "⬜"
        keyboard.append([
            InlineKeyboardButton(
                f"{mark} {data.get('name', 'Игрок')}",
                callback_data=f"t_part_{uid}"
            )
        ])

    keyboard.append([InlineKeyboardButton("➡️ Далее: победители", callback_data="t_part_done")])

    await query.message.reply_text(
        "🎮 Выберите участников турнира:\n\n"
        "Можно выбрать несколько игроков.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def send_tournament_winners_menu(query, context):
    tournament = context.user_data.get("tournament_add", {})
    participants = tournament.get("participants", [])
    winners = set(tournament.get("winners", []))

    keyboard = []
    for uid in participants:
        if uid not in approved_users:
            continue
        mark = "🥇" if uid in winners else "⬜"
        keyboard.append([
            InlineKeyboardButton(
                f"{mark} {approved_users[uid].get('name', 'Игрок')}",
                callback_data=f"t_win_{uid}"
            )
        ])

    keyboard.append([InlineKeyboardButton("✅ Сохранить результат", callback_data="t_win_done")])

    await query.message.reply_text(
        "🏆 Выберите победителя или победителей:\n\n"
        "Для командных режимов можно выбрать несколько игроков.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )



def render_tournament_bracket(participant_ids):
    names = []
    for uid in participant_ids:
        if uid in approved_users:
            names.append(approved_users[uid].get("name", "Игрок"))

    if not names:
        return "⚠️ Участники не выбраны."

    title = f"🏅 Турнирная сетка на {len(names)} участников\n\n"
    lines = []
    round_name = "1/2 финала" if len(names) == 4 else "1/4 финала" if len(names) == 8 else "1/8 финала" if len(names) == 16 else "1/16 финала"
    lines.append(f"{round_name}\n")

    for i in range(0, len(names), 2):
        first = names[i]
        second = names[i + 1] if i + 1 < len(names) else "Свободный слот"
        lines.append(f"{first} 🆚 {second}")

    lines.append("\n🎲 Участники распределены случайно.")
    lines.append("Победителей можно будет внести через «➕ Добавить результат турнира».")

    return title + "\n".join(lines)


async def send_bracket_participants_menu(update_or_query, context):
    bracket = context.user_data.get("bracket_create", {})
    size = bracket.get("size")
    selected = set(bracket.get("participants", []))

    keyboard = []
    for uid, data in approved_users.items():
        mark = "✅" if uid in selected else "⬜"
        keyboard.append([
            InlineKeyboardButton(
                f"{mark} {data.get('name', 'Игрок')}",
                callback_data=f"b_part_{uid}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("🎲 Перемешать и создать сетку", callback_data="b_shuffle")
    ])
    keyboard.append([
        InlineKeyboardButton("❌ Отмена", callback_data="b_cancel")
    ])

    text = (
        f"🏅 Создание турнирной сетки\n\n"
        f"Размер: {size} участников\n"
        f"Выбрано: {len(selected)} / {size}\n\n"
        "Выберите участников:"
    )

    if hasattr(update_or_query, "message") and update_or_query.message:
        await update_or_query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update_or_query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def save_bracket_to_history(actor_id, participants):
    actor_name = approved_users.get(actor_id, {}).get("name", "Руководство")
    participant_names = [
        approved_users[uid].get("name", "Игрок")
        for uid in participants
        if uid in approved_users
    ]

    bracket_data = {
        "participants": participant_names,
        "participant_ids": participants,
        "created_at": now(),
    }

    save_tournament_record(
        mode="🏅 Турнирная сетка",
        participants=participant_names,
        winners=[],
        created_by=actor_id,
        created_by_name=actor_name,
        bracket=bracket_data,
        status="active",
    )

    add_tournament_history({
        "mode": "🏅 Турнирная сетка",
        "participants": participant_names,
        "winners": [],
        "bracket": bracket_data,
        "created_by": actor_id,
        "created_by_name": actor_name,
        "date": now(),
        "status": "active",
    })


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    actor_id = query.from_user.id
    data = query.data

    if data == "edit_profile":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 Игровой ник", callback_data="edit_game_nick")],
            [InlineKeyboardButton("📨 Telegram аккаунт", callback_data="edit_username")],
            [InlineKeyboardButton("👤 Ник в Telegram", callback_data="edit_fullname")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="profile_back")],
        ])

        await query.edit_message_text(
            "✏️ Что вы хотите изменить?",
            reply_markup=keyboard
        )
        return

    if data == "edit_game_nick":
        context.user_data["edit_profile"] = "game_nick"
        await query.message.reply_text("🎮 Введите новый игровой ник:")
        return

    if data == "edit_username":
        context.user_data["edit_profile"] = "telegram_account"
        await query.message.reply_text(
            "📨 Введите Telegram аккаунт.\n\n"
            "Пример: @username или username"
        )
        return

    if data == "edit_fullname":
        context.user_data["edit_profile"] = "telegram_name"
        await query.message.reply_text("👤 Введите новый ник в Telegram:")
        return

    if data == "profile_back":
        user_data = approved_users.get(actor_id)
        if not user_data:
            await query.edit_message_text("⚠️ Профиль не найден.")
            return

        keyboard_rows = [
            [InlineKeyboardButton("✏️ Изменить данные", callback_data="edit_profile")],
            [InlineKeyboardButton("🏆 Достижения", callback_data="profile_achievements")],
            [InlineKeyboardButton("🏅 Почётные награды", callback_data="profile_honor_awards")],
            [InlineKeyboardButton("📊 Моя статистика", callback_data="profile_stats")],
            [InlineKeyboardButton("🏆 Турниры", callback_data="tournaments_menu")],
        ]

        if can_manage_members(actor_id):
            keyboard_rows.append([
                InlineKeyboardButton("🎖 Выдать награду", callback_data="honor_give_menu")
            ])

        keyboard = InlineKeyboardMarkup(keyboard_rows)

        achievement_points = get_achievement_points(user_data)

        await query.edit_message_text(
            render_profile_card(user_data, actor_id, achievement_points),
            reply_markup=keyboard,
        )
        return

    if data == "profile_achievements":
        user_data = approved_users.get(actor_id, {})
        gained = update_player_achievements(actor_id)
        await send_achievement_notifications(context, actor_id, gained)

        categories = get_achievement_categories()
        keyboard = []
        for index, category in enumerate(categories):
            keyboard.append([
                InlineKeyboardButton(category, callback_data=f"ach_category_{index}")
            ])
        keyboard.append([
            InlineKeyboardButton("📜 Все достижения", callback_data="ach_all")
        ])

        await query.message.reply_text(
            render_achievements_overview(user_data),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data.startswith("ach_category_"):
        user_data = approved_users.get(actor_id, {})
        categories = get_achievement_categories()

        try:
            category_index = int(data.replace("ach_category_", ""))
            category = categories[category_index]
        except Exception:
            await query.message.reply_text("⚠️ Категория не найдена.")
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ К категориям", callback_data="profile_achievements")]
        ])

        await query.message.reply_text(
            render_achievement_category(user_data, category),
            reply_markup=keyboard
        )
        return

    if data == "ach_all":
        user_data = approved_users.get(actor_id, {})
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ К категориям", callback_data="profile_achievements")]
        ])
        await query.message.reply_text(
            render_achievements(user_data),
            reply_markup=keyboard
        )
        return

    if data == "profile_stats":
        user_data = approved_users.get(actor_id, {})
        await query.message.reply_text(
            "📊 Моя статистика\n\n"
            f"🎮 Игрок: {user_data.get('name', 'не указан')}\n"
            f"🎖 Роль: {user_data.get('role', 'не указана')}\n"
            f"🏆 Активность: {user_data.get('activity', 0)}\n"
            f"💰 Взносы: {user_data.get('contribution', 0)}\n"
            f"📦 Передано на склад: {user_data.get('warehouse_added', 0)}\n"
            f"📤 Получено со склада: {user_data.get('warehouse_taken', 0)}\n"
            f"⭐ Уровень: {user_data.get('level', 1)}\n"
            f"💎 Опыт: {user_data.get('xp', 0)}\n"
            f"📅 В клане с: {user_data.get('joined', 'неизвестно')}\n\n"
            f"{render_tournament_stats(user_data)}"
        )
        return

    if data == "profile_honor_awards":
        user_data = approved_users.get(actor_id, {})
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Назад к профилю", callback_data="profile_back")]
        ])
        await query.message.reply_text(
            render_honor_awards_collection(user_data),
            reply_markup=keyboard
        )
        return

    if data == "honor_give_menu":
        if not can_manage_members(actor_id):
            await query.message.reply_text("⛔ Выдавать почётные награды может только лидер или заместитель.")
            return

        keyboard = []
        for uid, player in approved_users.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"{player.get('role', '⚔️ Боец')} {player.get('name', 'Игрок')}",
                    callback_data=f"honor_target_{uid}"
                )
            ])

        await query.message.reply_text(
            "🎖 Выберите игрока для награждения:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data.startswith("honor_target_"):
        if not can_manage_members(actor_id):
            await query.message.reply_text("⛔ Нет прав.")
            return

        try:
            target_id = int(data.replace("honor_target_", ""))
        except Exception:
            await query.message.reply_text("⚠️ Игрок не найден.")
            return

        if target_id not in approved_users:
            await query.message.reply_text("⚠️ Игрок не найден.")
            return

        context.user_data["honor_target"] = target_id
        target_name = approved_users[target_id].get("name", "Игрок")

        keyboard = []
        for award in HONOR_AWARDS:
            keyboard.append([
                InlineKeyboardButton(
                    f"{award['icon']} {award['name']}",
                    callback_data=f"honor_award_{award['id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="honor_cancel")])

        await query.message.reply_text(
            f"🏅 Выберите награду для игрока {target_name}:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data.startswith("honor_award_"):
        if not can_manage_members(actor_id):
            await query.message.reply_text("⛔ Нет прав.")
            return

        target_id = context.user_data.get("honor_target")
        if target_id not in approved_users:
            await query.message.reply_text("⚠️ Сначала выберите игрока.")
            return

        award_id = data.replace("honor_award_", "")
        award = get_honor_award(award_id)
        if not award:
            await query.message.reply_text("⚠️ Награда не найдена.")
            return

        target = approved_users[target_id]
        records = target.get("honor_awards")
        if not isinstance(records, list):
            records = []

        already_has = award_id in get_player_honor_award_ids(target)
        if already_has:
            await query.message.reply_text(
                f"⚠️ У игрока {target.get('name', 'Игрок')} уже есть награда:\n\n"
                f"{award['icon']} {award['name']}"
            )
            return

        actor_name = approved_users.get(actor_id, {}).get("name", "Руководство")
        record = {
            "id": award_id,
            "date": now(),
            "by": actor_id,
            "by_name": actor_name,
        }
        records.append(record)

        target["honor_awards"] = records
        target["activity"] = safe_int(target.get("activity")) + 10
        target["xp"] = safe_int(target.get("xp")) + 250
        target["level"] = max(1, safe_int(target.get("xp")) // 1000 + 1)

        gained = update_player_achievements(target_id)
        save_users(approved_users)

        target_name = target.get("name", "Игрок")
        add_log(
            f"🏅 {actor_name} выдал почётную награду {award['icon']} {award['name']} игроку {target_name}."
        )

        try:
            await context.bot.send_message(
                chat_id=target_id,
                text=(
                    "🎉 Вам выдана почётная награда!\n\n"
                    f"{award['icon']} {award['name']}\n"
                    f"📖 {award['description']}\n\n"
                    "🔥 +10 активности\n"
                    "💎 +250 XP"
                )
            )
            await send_achievement_notifications(context, target_id, gained)
        except Exception:
            pass

        context.user_data.pop("honor_target", None)

        await query.message.reply_text(
            "✅ Почётная награда выдана.\n\n"
            f"👤 Игрок: {target_name}\n"
            f"🏅 Награда: {award['icon']} {award['name']}"
        )
        return

    if data == "honor_cancel":
        context.user_data.pop("honor_target", None)
        await query.message.reply_text("❌ Выдача награды отменена.")
        return

    if data == "tournaments_menu":
        keyboard = [
            [InlineKeyboardButton("📊 Моя турнирная статистика", callback_data="tournaments_my_stats")],
        ]

        if can_manage_members(actor_id):
            keyboard.append([InlineKeyboardButton("➕ Добавить результат турнира", callback_data="tournament_add")])

        await query.message.reply_text(
            "🏆 Турниры\n\n"
            "Здесь хранится статистика участий и побед.\n"
            "Добавлять результаты могут только лидер и заместитель.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data == "tournaments_my_stats":
        user_data = approved_users.get(actor_id, {})
        await query.message.reply_text(render_tournament_stats(user_data))
        return

    if data == "tournament_add":
        if not can_manage_members(actor_id):
            await query.message.reply_text("⛔ Добавлять результаты турниров может только лидер или заместитель.")
            return

        keyboard = []
        for index, mode in enumerate(TOURNAMENT_MODES):
            keyboard.append([
                InlineKeyboardButton(mode["name"], callback_data=f"t_mode_{index}")
            ])

        await query.message.reply_text(
            "🏆 Добавление результата турнира\n\nВыберите режим:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data.startswith("t_mode_"):
        if not can_manage_members(actor_id):
            await query.message.reply_text("⛔ Нет прав.")
            return

        try:
            mode_index = int(data.replace("t_mode_", ""))
            mode = TOURNAMENT_MODES[mode_index]
        except Exception:
            await query.message.reply_text("⚠️ Режим турнира не найден.")
            return

        context.user_data["tournament_add"] = {
            "mode_id": mode["id"],
            "participants": [],
            "winners": [],
        }

        await send_tournament_participants_menu(query, context)
        return

    if data.startswith("t_part_"):
        if not can_manage_members(actor_id):
            await query.message.reply_text("⛔ Нет прав.")
            return

        tournament = context.user_data.get("tournament_add")
        if not tournament:
            await query.message.reply_text("⚠️ Сначала выберите режим турнира.")
            return

        if data == "t_part_done":
            if not tournament.get("participants"):
                await query.message.reply_text("⚠️ Выберите хотя бы одного участника.")
                return
            await send_tournament_winners_menu(query, context)
            return

        target_id = int(data.replace("t_part_", ""))
        participants = tournament.setdefault("participants", [])

        if target_id in participants:
            participants.remove(target_id)
        else:
            participants.append(target_id)

        await send_tournament_participants_menu(query, context)
        return

    if data.startswith("t_win_"):
        if not can_manage_members(actor_id):
            await query.message.reply_text("⛔ Нет прав.")
            return

        tournament = context.user_data.get("tournament_add")
        if not tournament:
            await query.message.reply_text("⚠️ Турнир не найден.")
            return

        if data == "t_win_done":
            participants = tournament.get("participants", [])
            winners = tournament.get("winners", [])
            mode_id = tournament.get("mode_id")

            if not winners:
                await query.message.reply_text("⚠️ Выберите хотя бы одного победителя.")
                return

            changed_ids = add_tournament_result(approved_users, participants, winners, mode_id)
            winner_names = [approved_users[uid].get("name", "Игрок") for uid in winners if uid in approved_users]
            participant_names = [approved_users[uid].get("name", "Игрок") for uid in participants if uid in approved_users]
            actor_name = approved_users.get(actor_id, {}).get("name", "Руководство")
            mode_name = mode_id
            for mode in TOURNAMENT_MODES:
                if mode.get("id") == mode_id:
                    mode_name = mode.get("name", mode_id)
                    break

            for uid in changed_ids:
                gained = update_player_achievements(uid)
                await send_achievement_notifications(context, uid, gained)

            save_users(approved_users)

            save_tournament_record(
                mode=mode_name,
                participants=participant_names,
                winners=winner_names,
                created_by=actor_id,
                created_by_name=actor_name,
                bracket={},
                status="finished",
            )

            add_tournament_history({
                "mode": mode_name,
                "participants": participant_names,
                "winners": winner_names,
                "bracket": {},
                "created_by": actor_id,
                "created_by_name": actor_name,
                "date": now(),
                "status": "finished",
            })

            add_log(
                f"🏆 {actor_name} добавил результат турнира. "
                f"Участники: {', '.join(participant_names)}. "
                f"Победители: {', '.join(winner_names)}."
            )

            context.user_data.pop("tournament_add", None)

            await query.message.reply_text(
                "✅ Результат турнира сохранён.\n\n"
                f"🎮 Участников: {len(participants)}\n"
                f"🏆 Победителей: {', '.join(winner_names)}"
            )
            return

        target_id = int(data.replace("t_win_", ""))
        winners = tournament.setdefault("winners", [])

        if target_id in winners:
            winners.remove(target_id)
        else:
            winners.append(target_id)

        await send_tournament_winners_menu(query, context)
        return

    if data.startswith("b_part_"):
        if not can_manage_members(actor_id):
            await query.message.reply_text("⛔ Нет прав.")
            return

        bracket = context.user_data.get("bracket_create")
        if not bracket:
            await query.message.reply_text("⚠️ Сначала выберите размер сетки.")
            return

        target_id = int(data.replace("b_part_", ""))
        participants = bracket.setdefault("participants", [])
        size = int(bracket.get("size") or 0)

        if target_id in participants:
            participants.remove(target_id)
        else:
            if len(participants) >= size:
                await query.message.reply_text(f"⚠️ Уже выбрано {size} участников.")
                return
            participants.append(target_id)

        await send_bracket_participants_menu(query, context)
        return

    if data == "b_shuffle":
        if not can_manage_members(actor_id):
            await query.message.reply_text("⛔ Нет прав.")
            return

        bracket = context.user_data.get("bracket_create")
        if not bracket:
            await query.message.reply_text("⚠️ Сетка не найдена.")
            return

        size = int(bracket.get("size") or 0)
        participants = bracket.get("participants", [])

        if len(participants) != size:
            await query.message.reply_text(
                f"⚠️ Нужно выбрать ровно {size} участников. Сейчас выбрано: {len(participants)}."
            )
            return

        random.shuffle(participants)
        bracket["participants"] = participants

        await save_bracket_to_history(actor_id, participants)

        add_log(
            f"🏅 {approved_users.get(actor_id, {}).get('name', 'Руководство')} создал турнирную сетку на {size} участников."
        )

        await query.message.reply_text(render_tournament_bracket(participants))
        context.user_data.pop("bracket_create", None)
        return

    if data == "b_cancel":
        context.user_data.pop("bracket_create", None)
        await query.message.reply_text("❌ Создание турнирной сетки отменено.")
        return

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
            "telegram_account": f"@{user_data.get('username')}" if user_data.get("username") else "не указан",
            "telegram_name": user_data.get("telegram_name") or "не указан",
            "role": "⚔️ Боец",
            "joined": today(),
            "activity": 0,
            "contribution": 0,
            "warehouse_added": 0,
            "warehouse_taken": 0,
            "level": 1,
            "xp": 0,
            "raids": 0,
            "achievements": [],
            "honor_awards": [],
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
        approved_users[target_id]["activity"] = int(approved_users[target_id].get("activity", 0) or 0) + 5
        gained = update_player_achievements(target_id)
        await send_achievement_notifications(context, target_id, gained)
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
    amount = int(req["amount"])
    player_id = int(req["player_id"])
    player_name = req["player_name"]
    actor_name = approved_users[actor_id]["name"]
    request_type = req.get("type", "add")

    if request_type == "add":
        warehouse[item] = warehouse.get(item, 0) + amount

        if player_id in approved_users:
            player = approved_users[player_id]

            player["warehouse_added"] = int(player.get("warehouse_added", 0) or 0) + amount
            player["contribution"] = int(player.get("contribution", 0) or 0) + amount
            player["activity"] = int(player.get("activity", 0) or 0) + 1
            player["xp"] = int(player.get("xp", 0) or 0) + amount
            player["level"] = max(1, int(player.get("xp", 0) or 0) // 1000 + 1)
            gained = sync_achievements(player)
            if gained:
                player["activity"] = int(player.get("activity", 0) or 0) + len(gained) * 2

            save_users(approved_users)
            await send_achievement_notifications(context, player_id, gained)

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

        if player_id in approved_users:
            player = approved_users[player_id]

            player["warehouse_taken"] = int(player.get("warehouse_taken", 0) or 0) + amount
            player["activity"] = int(player.get("activity", 0) or 0) + 1
            player["xp"] = int(player.get("xp", 0) or 0) + max(1, amount // 10)
            player["level"] = max(1, int(player.get("xp", 0) or 0) // 1000 + 1)
            gained = sync_achievements(player)
            if gained:
                player["activity"] = int(player.get("activity", 0) or 0) + len(gained) * 2

            save_users(approved_users)
            await send_achievement_notifications(context, player_id, gained)

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
            chat_id=player_id,
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

# ==============================
# PLATFORM OWNER COMMANDS
# ==============================

async def platform_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not is_platform_owner(user_id):
        await update.message.reply_text("⛔ Нет доступа.")
        return

    await update.message.reply_text(
        "🛡 Панель владельца платформы\n\n"
        "/clans — список кланов\n"
        "/create_clan Название — создать новый клан",
        reply_markup=platform_menu,
    )


async def clans_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not is_platform_owner(user_id):
        await update.message.reply_text("⛔ Нет доступа.")
        return

    clans = get_all_clans()
    await update.message.reply_text(render_clans_list(clans))


async def create_clan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not is_platform_owner(user_id):
        await update.message.reply_text("⛔ Нет доступа.")
        return

    name = " ".join(context.args).strip()

    if not name:
        await update.message.reply_text(
            "⚠️ Укажи название клана.\n\n"
            "Пример:\n"
            "/create_clan Alpha"
        )
        return

    register_clan(name=name, owner_id=user_id)

    await update.message.reply_text(
        f"✅ Клан создан.\n\n🏰 Название: {name}"
    )