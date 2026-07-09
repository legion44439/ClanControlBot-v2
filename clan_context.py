DEFAULT_CLAN_ID = 1


def get_clan_id(update=None, user_id=None):
    """
    Пока все старые данные работают через clan_id = 1.
    Позже сюда добавим определение клана по чату, владельцу или подписке.
    """
    return DEFAULT_CLAN_ID