"""Webhook mode: register endpoints once, then serve.

    export RUBIKA_BOT_TOKEN=your-token
    python examples/webhook_bot.py https://your.public.domain

Put the built in server (127.0.0.1:8080) behind an HTTPS reverse proxy.
Rubika connects only to public secure addresses. In your own Django,
FastAPI or Flask app, skip serve() and call
dp.handle_webhook_payload("update", body) from your views instead.
"""

import os
import sys

from rubikabot import Bot, Command, Dispatcher, serve

bot = Bot(os.environ["RUBIKA_BOT_TOKEN"])
dp = Dispatcher(bot)


@dp.message(Command("start"))
def start(message):
    message.answer("سلام! این بات در حالت وب‌هوک کار می‌کند.")


@dp.message()
def echo(message):
    if message.text:
        message.answer(f"گفتی: {message.text}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: webhook_bot.py https://your.domain")
    bot.register_webhooks(sys.argv[1])
    print("webhooks registered")
    serve(dp, port=8080)
