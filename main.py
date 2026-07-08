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

from config import TOKEN
from handlers import start, menu_handler, button_handler


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ClanControl Bot is running")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


if not TOKEN:
    raise RuntimeError("TOKEN не найден. Добавь TOKEN в Environment Variables на Render.")

Thread(target=run_web_server, daemon=True).start()

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

print("✅ ClanControl Bot запущен...")

asyncio.set_event_loop(asyncio.new_event_loop())
app.run_polling()