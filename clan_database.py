import requests
from datetime import datetime

from config import SUPABASE_URL, SUPABASE_KEY


REQUEST_TIMEOUT = 20


def now_date():
    return datetime.now().strftime("%d.%m.%Y")


def now_datetime():
    return datetime.now().strftime("%d.%m.%Y %H:%M")


def _require_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "Supabase не настроен. Добавь SUPABASE_URL и SUPABASE_SECRET_KEY."
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
        "tournaments": data.get("tournaments") or {},
        "honor_awards": data.get("honor_awards") or [],
    }


# ==============================
# CLANS
# ==============================

def load_clans():
    return _get(
        "clans",
        {
            "select": "*",
            "order": "id.asc",
        }
    )


def get_clan(clan_id):
    rows = _get(
        "clans",
        {
            "select": "*",
            "id": f"eq.{int(clan_id)}",
            "limit": "1",
        }
    )

    return rows[0] if rows else None


def create_clan(name, owner_id, telegram_chat_id=None, settings=None):
    row = {
        "name": name,
        "owner_id": int(owner_id),
        "telegram_chat_id": int(telegram_chat_id) if telegram_chat_id else None,
        "subscription_status": "active",
        "settings": settings or {},
    }

    return _post("clans", [row])


# ==============================
# USERS
# ==============================

def load_users(clan_id):
    rows = _get(
        "approved_users",
        {
            "select": "*",
            "clan_id": f"eq.{int(clan_id)}",
            "order": "user_id.asc",
        }
    )

    users = {}

    for row in rows:
        users[int(row["user_id"])] = default_user_data(row)

    return users


def save_users(clan_id, users):
    clan_id = int(clan_id)

    rows = []

    for user_id, data in users.items():
        user_data = default_user_data(data)

        rows.append({
            "clan_id": clan_id,
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
            "tournaments": user_data["tournaments"],
            "honor_awards": user_data["honor_awards"],
        })

    db_rows = _get(
        "approved_users",
        {
            "select": "user_id",
            "clan_id": f"eq.{clan_id}",
        }
    )

    wanted = {int(row["user_id"]) for row in rows}

    for row in db_rows:
        uid = int(row["user_id"])
        if uid not in wanted:
            _delete(
                "approved_users",
                {
                    "clan_id": f"eq.{clan_id}",
                    "user_id": f"eq.{uid}",
                }
            )

    if rows:
        _post("approved_users", rows, upsert=True)


# ==============================
# PENDING USERS
# ==============================

def load_pending_users(clan_id):
    rows = _get(
        "pending_users",
        {
            "select": "*",
            "clan_id": f"eq.{int(clan_id)}",
            "order": "user_id.asc",
        }
    )

    result = {}

    for row in rows:
        result[int(row["user_id"])] = {
            "telegram_name": row.get("telegram_name"),
            "username": row.get("username"),
            "nick": row.get("nick"),
        }

    return result


def save_pending_users(clan_id, pending_users):
    clan_id = int(clan_id)

    _delete("pending_users", {"clan_id": f"eq.{clan_id}"})

    rows = []

    for user_id, data in pending_users.items():
        rows.append({
            "clan_id": clan_id,
            "user_id": int(user_id),
            "telegram_name": data.get("telegram_name"),
            "username": data.get("username"),
            "nick": data.get("nick"),
        })

    if rows:
        _post("pending_users", rows, upsert=True)


# ==============================
# WAREHOUSE
# ==============================

def load_warehouse(clan_id):
    rows = _get(
        "warehouse",
        {
            "select": "item,amount",
            "clan_id": f"eq.{int(clan_id)}",
            "order": "item.asc",
        }
    )

    return {
        row["item"]: int(row.get("amount") or 0)
        for row in rows
    }


def save_warehouse(clan_id, warehouse):
    clan_id = int(clan_id)

    db_rows = _get(
        "warehouse",
        {
            "select": "item",
            "clan_id": f"eq.{clan_id}",
        }
    )

    wanted = set(warehouse.keys())

    for row in db_rows:
        item = row["item"]
        if item not in wanted:
            _delete(
                "warehouse",
                {
                    "clan_id": f"eq.{clan_id}",
                    "item": f"eq.{item}",
                }
            )

    rows = []

    for item, amount in warehouse.items():
        rows.append({
            "clan_id": clan_id,
            "item": item,
            "amount": int(amount or 0),
        })

    if rows:
        _post("warehouse", rows, upsert=True)


# ==============================
# WAREHOUSE REQUESTS
# ==============================

def load_warehouse_requests(clan_id):
    rows = _get(
        "warehouse_requests",
        {
            "select": "*",
            "clan_id": f"eq.{int(clan_id)}",
            "order": "id.asc",
        }
    )

    result = []

    for row in rows:
        result.append({
            "type": row.get("action") or row.get("type") or "add",
            "player_id": int(row.get("user_id") or 0),
            "player_name": row.get("username") or "Игрок",
            "item": row.get("item"),
            "amount": int(row.get("amount") or 0),
            "date": row.get("date") or row.get("created_at") or now_datetime(),
        })

    return result


def save_warehouse_requests(clan_id, warehouse_requests):
    clan_id = int(clan_id)

    _delete("warehouse_requests", {"clan_id": f"eq.{clan_id}"})

    rows = []

    for req in warehouse_requests:
        rows.append({
            "clan_id": clan_id,
            "user_id": int(req.get("player_id") or req.get("user_id") or 0),
            "username": req.get("player_name") or req.get("username") or "Игрок",
            "action": req.get("type") or req.get("action") or "add",
            "item": req.get("item"),
            "amount": int(req.get("amount") or 0),
            "date": req.get("date") or now_datetime(),
        })

    if rows:
        _post("warehouse_requests", rows)


# ==============================
# HISTORY / LOGS
# ==============================

def load_warehouse_history(clan_id):
    rows = _get(
        "warehouse_history",
        {
            "select": "*",
            "clan_id": f"eq.{int(clan_id)}",
            "order": "id.asc",
        }
    )

    result = []

    for row in rows:
        if row.get("text"):
            result.append({
                "date": row.get("date") or now_datetime(),
                "text": row.get("text"),
                "user_id": row.get("user_id"),
                "username": row.get("username"),
                "action": row.get("action"),
                "item": row.get("item"),
                "amount": row.get("amount"),
            })

    return result


def save_warehouse_history(clan_id, warehouse_history):
    clan_id = int(clan_id)

    _delete("warehouse_history", {"clan_id": f"eq.{clan_id}"})

    rows = []

    for item in warehouse_history[-1000:]:
        rows.append({
            "clan_id": clan_id,
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


def load_clan_log(clan_id):
    rows = _get(
        "clan_log",
        {
            "select": "date,text",
            "clan_id": f"eq.{int(clan_id)}",
            "order": "id.asc",
        }
    )

    return [
        {
            "date": row.get("date"),
            "text": row.get("text"),
        }
        for row in rows
    ]


def save_clan_log(clan_id, clan_log):
    clan_id = int(clan_id)

    _delete("clan_log", {"clan_id": f"eq.{clan_id}"})

    rows = []

    for item in clan_log[-1000:]:
        rows.append({
            "clan_id": clan_id,
            "date": item.get("date") or now_datetime(),
            "text": item.get("text", ""),
        })

    if rows:
        _post("clan_log", rows)


# ==============================
# TOURNAMENTS
# ==============================

def load_tournament_history(clan_id):
    rows = _get(
        "tournaments",
        {
            "select": "*",
            "clan_id": f"eq.{int(clan_id)}",
            "order": "id.desc",
            "limit": "100",
        }
    )

    result = []

    for row in rows:
        result.append({
            "id": row.get("id"),
            "mode": row.get("mode"),
            "participants": row.get("participants") or [],
            "winners": row.get("winners") or [],
            "bracket": row.get("bracket") or {},
            "created_by": row.get("created_by"),
            "created_by_name": row.get("created_by_name"),
            "date": row.get("date"),
            "status": row.get("status") or "finished",
        })

    return result


def save_tournament_record(
    clan_id,
    mode,
    participants,
    winners,
    created_by,
    created_by_name,
    bracket=None,
    status="finished",
):
    row = {
        "clan_id": int(clan_id),
        "mode": mode,
        "participants": participants or [],
        "winners": winners or [],
        "bracket": bracket or {},
        "created_by": int(created_by),
        "created_by_name": created_by_name,
        "date": now_datetime(),
        "status": status,
    }

    _post("tournaments", [row])


# ==============================
# CLASS WRAPPER
# ==============================

class ClanDatabase:
    def __init__(self, clan_id):
        self.clan_id = int(clan_id)

    def load_users(self):
        return load_users(self.clan_id)

    def save_users(self, users):
        return save_users(self.clan_id, users)

    def load_pending_users(self):
        return load_pending_users(self.clan_id)

    def save_pending_users(self, pending_users):
        return save_pending_users(self.clan_id, pending_users)

    def load_warehouse(self):
        return load_warehouse(self.clan_id)

    def save_warehouse(self, warehouse):
        return save_warehouse(self.clan_id, warehouse)

    def load_warehouse_requests(self):
        return load_warehouse_requests(self.clan_id)

    def save_warehouse_requests(self, requests):
        return save_warehouse_requests(self.clan_id, requests)

    def load_warehouse_history(self):
        return load_warehouse_history(self.clan_id)

    def save_warehouse_history(self, history):
        return save_warehouse_history(self.clan_id, history)

    def load_clan_log(self):
        return load_clan_log(self.clan_id)

    def save_clan_log(self, clan_log):
        return save_clan_log(self.clan_id, clan_log)

    def load_tournament_history(self):
        return load_tournament_history(self.clan_id)

    def save_tournament_record(
        self,
        mode,
        participants,
        winners,
        created_by,
        created_by_name,
        bracket=None,
        status="finished",
    ):
        return save_tournament_record(
            self.clan_id,
            mode,
            participants,
            winners,
            created_by,
            created_by_name,
            bracket,
            status,
        )