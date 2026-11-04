"""A two step registration form with FSM state kept in a JSON file.

    export RUBIKA_BOT_TOKEN=your-token
    python examples/form_bot.py
"""

import os

from rubikabot import Bot, Command, Dispatcher, FileStorage, State, \
    StateFilter, StatesGroup

bot = Bot(os.environ["RUBIKA_BOT_TOKEN"])
dp = Dispatcher(bot, storage=FileStorage(".rubikabot_fsm.json"))


class Register(StatesGroup):
    name = State()
    age = State()


@dp.message(Command("register"))
def begin(message, state):
    state.set_state(Register.name)
    message.answer("اسمت چیست؟ (برای لغو /cancel بفرست)")


@dp.message(Command("cancel"))
def cancel(message, state):
    state.clear()
    message.answer("لغو شد.")


@dp.message(StateFilter(Register.name))
def get_name(message, state):
    state.update_data(name=message.text)
    state.set_state(Register.age)
    message.answer(f"خوش آمدی {message.text}! چند سالته؟")


@dp.message(StateFilter(Register.age))
def get_age(message, state):
    if not (message.text or "").strip().isdigit():
        message.answer("سن را با عدد بفرست.")
        return
    data = state.get_data()
    state.clear()
    message.answer(f"ثبت شد: {data['name']}، {message.text} ساله ✅")


if __name__ == "__main__":
    dp.start_polling(offset_file=".rubika_offset.json")
