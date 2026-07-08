import json
import os
from datetime import datetime
import requests

from config import DATA_FILE, LEADER_ID, SUPABASE_KEY, SUPABASE_URL


REQUEST_TIMEOUT = 20


def now_date():
    return datetime.now().strftime("%d.%m.%Y")


def now_datetime():
    return datetime.now().strftime("%d.%m.%Y %H:%M")


def default_user_data(data=None):
    data = data or {}

    return {
        "name": data.get("name") or data.get("nick") or "Игрок",
        "role": data.get("role") or "⚔️ Боец",
        "joined": data.get("joined") or now_date(),
        "activity": int(data.get("activity", 0) or 0),
        "contribution": int(data.get("contribution", 0) or 0),

        "telegram_account": data.get("telegram_account") or data.get("username") or "",
        "telegram_name": data.get("telegram_name") or "",
        "level": int(data.get("level", 1) or 1),
        "xp": int(data.get("xp", 0) or 0),
        "warehouse_added": int(data.get("warehouse_added", 0) or 0),
        "warehouse_taken": int(data.get("warehouse_taken", 0) or 0),
        "raids": int(data.get("raids", 0) or 0),
        "achievements": data.get("achievements") or [],
    }


def _require_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "Supabase не настроен. Добавь Environment Variables: "
            "SUPABASE_URL и SUPABASE_SECRET_KEY."
        )


def _headers(extra=None):
    _require_supabase()
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if extra:
        headers.update(extra)
    return headers


def _url(table):
    return f"{SUPABASE_URL}/rest/v1/{table}"


def _check(response):
    if response.status_code >= 400:
        raise RuntimeError(f"Supabase error {response.status_code}: {response.text}")

    if response.text:
        try:
            return response.json()
        except Exception:
            return response.text

    return None


def _get(table, params=None):
    response = requests.get(
        _url(table),
        headers=_headers(),
        params=params or {},
        timeout=REQUEST_TIMEOUT,
    )
    return _check(response) or []


def _post(table, rows, upsert=False):
    if not rows:
        return None

    headers = _headers({"Prefer": "return=minimal"})

    if upsert:
        headers["Prefer"] = "resolution=merge-duplicates,return=minimal"

    response = requests.post(
        _url(table),
        headers=headers,
        json=rows,
        timeout=REQUEST_TIMEOUT,
    )
    return _check(response)


def _delete(table, params):
    response = requests.delete(
        _url(table),
        headers=_headers({"Prefer": "return=minimal"}),
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    return _check(response)


def _load_json(file_name, default):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as file:
            return json.load(file)
    return default


class PersistentDict(dict):
    def __init__(self, *args, save_callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._save_callback = save_callback
        self._autosave = True

    def _save(self):
        if self._autosave and self._save_callback:
            self._save_callback()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._save()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._save()

    def pop(self, key, default=None):
        value = super().pop(key, default)
        self._save()
        return value

    def clear(self):
        super().clear()
        self._save()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self._save()


class PersistentList(list):
    def __init__(self, *args, save_callback=None):
        super().__init__(*args)
        self._save_callback = save_callback
        self._autosave = True

    def _save(self):
        if self._autosave and self._save_callback:
            self._save_callback()

    def append(self, item):
        super().append(item)
        self._save()

    def pop(self, index=-1):
        value = super().pop(index)
        self._save()
        return value

    def __delitem__(self, index):
        super().__delitem__(index)
        self._save()

    def clear(self):
        super().clear()
        self._save()

    def extend(self, items):
        super().extend(items)
        self._save()


# ---------- LOADERS ----------

def load_users():
    rows = _get("approved_users", {"select": "*", "order": "user_id.asc"})
    users = {}

    for row in rows:
        users[int(row["user_id"])] = default_user_data(row)

    if users:
        return users

    local_users = _load_json(DATA_FILE, {})

    if local_users:
        users = {
            int(user_id): default_user_data(data)
            for user_id, data in local_users.items()
        }
    else:
        users = {
            LEADER_ID: default_user_data({
                "name": "Legi",
                "role": "👑 Лидер",
            })
        }

    _save_users_raw(users)
    return users


def load_pending_users():
    rows = _get("pending_users", {"select": "*", "order": "user_id.asc"})
    result = {}

    for row in rows:
        result[int(row["user_id"])] = {
            "telegram_name": row.get("telegram_name"),
            "username": row.get("username"),
            "nick": row.get("nick"),
        }

    return result


def load_clan_log():
    rows = _get("clan_log", {"select": "date,text", "order": "id.asc"})
    return [
        {
            "date": row.get("date"),
            "text": row.get("text"),
        }
        for row in rows
    ]


def load_warehouse():
    rows = _get("warehouse", {"select": "item,amount", "order": "item.asc"})
    return {
        row["item"]: row.get("amount") or 0
        for row in rows
    }


def load_warehouse_requests():
    rows = _get("warehouse_requests", {"select": "*", "order": "id.asc"})
    result = []

    for row in rows:
        result.append({
            "type": row.get("action") or row.get("type") or "add",
            "player_id": int(row.get("user_id") or 0),
            "player_name": row.get("username") or "Игрок",
            "item": row.get("item"),
            "amount": row.get("amount") or 0,
            "date": row.get("date") or row.get("created_at") or now_datetime(),
        })

    return result


def load_warehouse_history():
    rows = _get("warehouse_history", {"select": "*", "order": "id.asc"})
    result = []

    for row in rows:
        text = row.get("text")
        if text:
            result.append({
                "date": row.get("date") or now_datetime(),
                "text": text,
                "user_id": row.get("user_id"),
                "username": row.get("username"),
                "action": row.get("action"),
                "item": row.get("item"),
                "amount": row.get("amount"),
            })

    return result


# ---------- SAVERS ----------

def _save_users_raw(users):
    rows = []

    for user_id, data in users.items():
        user_data = default_user_data(data)

        rows.append({
            "user_id": int(user_id),
            "name": user_data["name"],
            "role": user_data["role"],
            "joined": user_data["joined"],
            "activity": user_data["activity"],
            "contribution": user_data["contribution"],

            "telegram_account": user_data["telegram_account"],
            "telegram_name": user_data["telegram_name"],
            "level": user_data["level"],
            "xp": user_data["xp"],
            "warehouse_added": user_data["warehouse_added"],
            "warehouse_taken": user_data["warehouse_taken"],
            "raids": user_data["raids"],
            "achievements": user_data["achievements"],
        })

    db_rows = _get("approved_users", {"select": "user_id"})
    wanted = {int(row["user_id"]) for row in rows}

    for row in db_rows:
        uid = int(row["user_id"])
        if uid not in wanted:
            _delete("approved_users", {"user_id": f"eq.{uid}"})

    if rows:
        _post("approved_users", rows, upsert=True)


def save_users(users):
    _save_users_raw(users)


def save_pending_users():
    _delete("pending_users", {"user_id": "not.is.null"})

    rows = []

    for user_id, data in pending_users.items():
        rows.append({
            "user_id": int(user_id),
            "telegram_name": data.get("telegram_name"),
            "username": data.get("username"),
            "nick": data.get("nick"),
        })

    if rows:
        _post("pending_users", rows, upsert=True)


def save_clan_log():
    _delete("clan_log", {"id": "not.is.null"})

    rows = []

    for item in clan_log[-1000:]:
        rows.append({
            "date": item.get("date") or now_datetime(),
            "text": item.get("text", ""),
        })

    if rows:
        _post("clan_log", rows)


def save_warehouse():
    db_rows = _get("warehouse", {"select": "item"})
    wanted = set(warehouse.keys())

    for row in db_rows:
        item = row["item"]
        if item not in wanted:
            _delete("warehouse", {"item": f"eq.{item}"})

    rows = [
        {
            "item": item,
            "amount": int(amount or 0),
        }
        for item, amount in warehouse.items()
    ]

    if rows:
        _post("warehouse", rows, upsert=True)


def save_warehouse_requests():
    _delete("warehouse_requests", {"id": "not.is.null"})

    rows = []

    for req in warehouse_requests:
        rows.append({
            "user_id": int(req.get("player_id") or req.get("user_id") or 0),
            "username": req.get("player_name") or req.get("username") or "Игрок",
            "action": req.get("type") or req.get("action") or "add",
            "item": req.get("item"),
            "amount": int(req.get("amount") or 0),
            "date": req.get("date") or now_datetime(),
        })

    if rows:
        _post("warehouse_requests", rows)


def save_warehouse_history():
    _delete("warehouse_history", {"id": "not.is.null"})

    rows = []

    for item in warehouse_history[-1000:]:
        rows.append({
            "user_id": item.get("user_id"),
            "username": item.get("username"),
            "action": item.get("action"),
            "item": item.get("item"),
            "amount": item.get("amount"),
            "date": item.get("date") or now_datetime(),
            "text": item.get("text", ""),
        })

    if rows:
        _post("warehouse_history", rows)


# ---------- GLOBAL DATA ----------

approved_users = PersistentDict(
    load_users(),
    save_callback=lambda: save_users(approved_users)
)

pending_users = PersistentDict(
    load_pending_users(),
    save_callback=save_pending_users
)

clan_log = PersistentList(
    load_clan_log(),
    save_callback=save_clan_log
)

warehouse = PersistentDict(
    load_warehouse(),
    save_callback=save_warehouse
)

warehouse_requests = PersistentList(
    load_warehouse_requests(),
    save_callback=save_warehouse_requests
)

warehouse_history = PersistentList(
    load_warehouse_history(),
    save_callback=save_warehouse_history
)


# ---------- HELPERS ----------

def add_log(text):
    clan_log.append({
        "date": now_datetime(),
        "text": text,
    })

    if len(clan_log) > 1000:
        del clan_log[:-1000]

    save_clan_log()


def add_warehouse_history(text):
    warehouse_history.append({
        "date": now_datetime(),
        "text": text,
    })

    if len(warehouse_history) > 1000:
        del warehouse_history[:-1000]

    save_warehouse_history()


def add_xp(user_id, amount):
    if user_id not in approved_users:
        return

    approved_users[user_id]["xp"] = int(approved_users[user_id].get("xp", 0)) + amount
    approved_users[user_id]["level"] = max(1, approved_users[user_id]["xp"] // 100 + 1)

    save_users(approved_users)


def add_achievement(user_id, achievement):
    if user_id not in approved_users:
        return

    achievements = approved_users[user_id].get("achievements", [])

    if achievement not in achievements:
        achievements.append(achievement)

    approved_users[user_id]["achievements"] = achievements
    save_users(approved_users)


def has_access(user_id):
    return user_id in approved_users


def get_role(user_id):
    return approved_users.get(user_id, {}).get("role", "")


def is_leader(user_id):
    return get_role(user_id) == "👑 Лидер"


def is_deputy(user_id):
    return get_role(user_id) == "⭐ Заместитель"


def is_officer(user_id):
    return get_role(user_id) == "🛡 Офицер"


def is_builder(user_id):
    role = get_role(user_id)
    return role in ["🏗 Строитель", "🏗 Билдер", "📦 Логист"]


def is_admin(user_id):
    return is_leader(user_id) or is_deputy(user_id) or is_officer(user_id)


def can_manage_members(user_id):
    return is_leader(user_id) or is_deputy(user_id)


def can_broadcast(user_id):
    return is_leader(user_id) or is_deputy(user_id) or is_officer(user_id)


def can_confirm_warehouse(user_id):
    return is_leader(user_id) or is_deputy(user_id) or is_builder(user_id)


def can_transfer_leadership(user_id):
    return is_leader(user_id)