"""Chat keypad and inline keypad demo.

    export RUBIKA_BOT_TOKEN=your-token
    python examples/keypads_bot.py
"""

import os

from rubikabot import Bot, ButtonId, Command, Dispatcher, F, \
    KeyboardBuilder

bot = Bot(os.environ["RUBIKA_BOT_TOKEN"])
dp = Dispatcher(bot)

MENU = (KeyboardBuilder()
        .button("ساخت نظرسنجی", id="poll")
        .button("موقعیت ما", id="place")
        .adjust(2)
        .as_keypad())

CONFIRM = (KeyboardBuilder()
           .button("تأیید", id="confirm")
           .button("انصراف", id="cancel")
           .adjust(2)
           .as_keypad())


@dp.message(Command("start"))
def start(message):
    message.answer("یک گزینه را انتخاب کن.",
                   chat_keypad_type="New", chat_keypad=MENU)


@dp.message(ButtonId("poll"))
def poll(message):
    bot.send_poll(message.chat_id, "این بات را چطور دیدی؟",
                  ["عالی", "خوب", "معمولی"])


@dp.message(ButtonId("place"))
def place(message):
    message.answer("حذف حسابت را تأیید می‌کنی؟", inline_keypad=CONFIRM)


@dp.inline_message(F.button_id == "confirm")
def confirmed(inline):
    inline.edit_text("انجام شد ✅")


@dp.inline_message(F.button_id == "cancel")
def cancelled(inline):
    inline.edit_text("لغو شد.")


if __name__ == "__main__":
    dp.start_polling(offset_file=".rubika_offset.json")
