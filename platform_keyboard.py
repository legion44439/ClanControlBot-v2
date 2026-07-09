from telegram import ReplyKeyboardMarkup


platform_menu = ReplyKeyboardMarkup(
    [
        ["🏰 Кланы", "👥 Владельцы"],
        ["➕ Создать клан", "💳 Подписки"],
        ["📊 Статистика платформы", "🌐 Админ-панель"],
        ["⚙️ Настройки платформы"],
        ["⬅️ Назад"],
    ],
    resize_keyboard=True
)


platform_clan_menu = ReplyKeyboardMarkup(
    [
        ["👥 Участники клана", "📦 Склад клана"],
        ["🏆 Турниры клана", "🏅 Награды клана"],
        ["💳 Подписка клана", "🚫 Заблокировать клан"],
        ["⬅️ К платформе"],
    ],
    resize_keyboard=True
)