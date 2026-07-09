import os
import asyncio
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import TOKEN, BOT_NAME, BOT_VERSION
from handlers import (
    start,
    menu_handler,
    button_handler,
    platform_command,
    clans_command,
    create_clan_command,
)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(
            f"{BOT_NAME} v{BOT_VERSION} is running".encode()
        )

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


if not TOKEN:
    raise RuntimeError(
        "TOKEN не найден. Добавь TOKEN в Environment Variables на Render."
    )

Thread(target=run_web_server, daemon=True).start()

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("platform", platform_command))
app.add_handler(CommandHandler("clans", clans_command))
app.add_handler(CommandHandler("create_clan", create_clan_command))

app.add_handler(CallbackQueryHandler(button_handler))

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        menu_handler,
    )
)

print(f"✅ {BOT_NAME} v{BOT_VERSION} успешно запущен.")

asyncio.set_event_loop(asyncio.new_event_loop())

app.run_polling()