"""The smallest useful rubikabot bot: says hello and echoes text.

    export RUBIKA_BOT_TOKEN=your-token
    python examples/echo_bot.py
"""

import os

from rubikabot import Bot, Command, Dispatcher

bot = Bot(os.environ["RUBIKA_BOT_TOKEN"])
dp = Dispatcher(bot)


@dp.message(Command("start"))
def start(message):
    message.answer("سلام! هر چه بفرستی همان را برمی‌گردانم.")


@dp.message()
def echo(message):
    if message.text:
        message.answer(f"گفتی: {message.text}")


if __name__ == "__main__":
    print("bot is running, press Ctrl+C to stop")
    dp.start_polling(offset_file=".rubika_offset.json")
