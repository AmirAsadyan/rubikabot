# rubikabot

A modern Python framework for building [Rubika](https://rubika.ir) bots,
in the spirit of aiogram and python-telegram-bot, built on the official
Rubika Bot API v3.

🇮🇷 **Persian README: [README_FA.md](README_FA.md)**

## Why another library?

The official examples use a small function based package: you pass the
token into every call, work with raw dicts, and write your own polling
loop, routing, sessions and keyboard JSON. rubikabot gives you the layer
real bots need:

- **Typed models** for every API object and enum, with `from_dict` and
  `to_dict`
- **A `Bot` client** covering all 19 API methods, with a pluggable HTTP
  transport
- **Dispatcher and routers** with per kind decorators and composable
  filters, including a magic filter (`F.text == "سلام"`)
- **FSM** with state groups and per chat/user storage, in memory or in a
  JSON file
- **Keyboard builders** for chat keypads and inline keypads
- **Formatted text** helpers that handle the API's UTF-16 metadata rules,
  which reject a whole message over one bad part
- **Polling and webhook** runners, including a standard library webhook
  server
- **Zero runtime dependencies.** Python 3.10+, standard library only

## Install

```bash
pip install rubikabot
```

Until the first PyPI release lands, install from GitHub:

```bash
pip install git+https://github.com/AmirAsadyan/rubikabot.git
```

## Quick start

Create a bot with **BotFather** in Rubika, keep the token safe, then:

```python
import os
from rubikabot import Bot, Dispatcher, Command, KeyboardBuilder

bot = Bot(os.environ["RUBIKA_BOT_TOKEN"])
dp = Dispatcher(bot)

menu = (KeyboardBuilder()
        .button("ساخت نظرسنجی", id="poll")
        .button("درباره", id="about")
        .adjust(2)
        .as_keypad())

@dp.message(Command("start"))
def start(message):
    message.answer("سلام! یک گزینه را انتخاب کن.",
                   chat_keypad_type="New", chat_keypad=menu)

@dp.message()
def echo(message):
    if message.button_id == "poll":
        bot.send_poll(message.chat_id, "بات را چطور دیدی؟",
                      ["عالی", "خوب", "معمولی"])
    elif message.button_id == "about":
        message.answer("من با rubikabot ساخته شده‌ام.")
    elif message.text:
        message.answer(f"گفتی: {message.text}")

dp.start_polling(offset_file=".rubika_offset.json")
```

## A form with FSM

```python
from rubikabot import Router, State, StatesGroup, StateFilter, Text

router = Router()

class Register(StatesGroup):
    name = State()
    age = State()

@router.message(Command("register"))
def begin(message, state):
    state.set_state(Register.name)
    message.answer("اسمت چیست؟")

@router.message(StateFilter(Register.name))
def get_name(message, state):
    state.update_data(name=message.text)
    state.set_state(Register.age)
    message.answer("چند سالته؟")

@router.message(StateFilter(Register.age), Text())
def get_age(message, state):
    data = state.get_data()
    state.clear()
    message.answer(f"تمام شد {data['name']}، {message.text} ساله.")

dp.include_router(router)
```

## Inline keypads

Inline taps arrive separately from normal messages and are handled with
their own decorator:

```python
from rubikabot import F

@dp.inline_message(F.button_id == "confirm")
def confirm(inline):
    inline.edit_text("تأیید شد ✅")
```

## Files

```python
file_id = bot.upload_file("photo.jpg", "Image")   # two steps, handled
bot.send_file(chat_id, file_id, text="این هم عکس")
data = bot.download_file(incoming_file_id)        # bytes
```

Upload limits from the API docs: generic files and mp4 video up to
50 MB, images (jpg, gif, png, webp) up to 10 MB, voice and music as mp3,
and a Gif as a silent mp4.

## Webhooks

```python
from rubikabot import serve

bot.register_webhooks("https://your.public.domain")
serve(dp, port=8080)   # behind your HTTPS reverse proxy
```

Or call `dp.handle_webhook_payload("update", body)` and
`dp.handle_webhook_payload("inline", body)` from your own Django,
FastAPI or Flask views.

## Examples

- [examples/echo_bot.py](examples/echo_bot.py) - the smallest useful bot
- [examples/keypads_bot.py](examples/keypads_bot.py) - chat and inline
  keypads
- [examples/form_bot.py](examples/form_bot.py) - a registration form
  with FSM
- [examples/webhook_bot.py](examples/webhook_bot.py) - webhook mode

## Development

```bash
git clone https://github.com/AmirAsadyan/rubikabot.git
cd rubikabot
python -m unittest discover -s tests -v
```

The whole test suite runs offline against a fake transport. No token and
no network needed.

## API coverage

All 19 methods of Bot API v3: `getMe`, `sendMessage`, `sendPoll`,
`sendLocation`, `sendContact`, `getChat`, `getUpdates`, `forwardMessage`,
`editMessageText`, `editMessageKeypad`, `deleteMessage`, `setCommands`,
`updateBotEndpoints`, `editChatKeypad`, `getFile`, `sendFile`,
`requestSendFile`, `banChatMember`, `unbanChatMember`.

Field names and shapes follow the official docs at
https://rubika.ir/botapi. Places where the docs contradict themselves
(for example the polling cursor, named `start_id` on the overview page
but `offset_id` / `next_offset_id` on the methods page) follow the
methods page, which is what the live API accepts.

## License

MIT. See [LICENSE](LICENSE).
