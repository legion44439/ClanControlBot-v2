# ClanControlBot v2

Telegram-бот для управления кланом с постоянным хранением данных в Supabase PostgreSQL.

## Настройка Supabase

1. Открой Supabase → SQL Editor.
2. Выполни файл `migrations/001_supabase_schema.sql`.
3. В Supabase возьми:
   - Project URL
   - Secret key

## Render Environment Variables

Добавь в Render → Service → Environment:

```text
TOKEN=токен_telegram_бота
LEADER_ID=7816223649
SUPABASE_URL=https://твой-проект.supabase.co
SUPABASE_SECRET_KEY=твой_новый_secret_key
```

Важно: после того как ключ был отправлен в чат, лучше создать новый Secret key в Supabase и использовать его.

## Запуск

```bash
pip install -r requirements.txt
python main.py
```

## Что хранится в Supabase

- пользователи клана;
- заявки на вступление;
- склад;
- заявки склада;
- история склада;
- журнал клана.
