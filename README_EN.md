<div align="center">

**🌐 Language / زبان**

[![FA](https://img.shields.io/badge/FA-%D9%81%D8%A7%D8%B1%D8%B3%DB%8C-blue?style=for-the-badge)](README.md)
[![EN](https://img.shields.io/badge/EN-English-brightgreen?style=for-the-badge)](README_EN.md)

</div>

<div align="center">

# rubikabot

**A modern Python framework for building Rubika bots**

Typed models · Dispatcher & routers · Filters · FSM · Keyboard builders · Zero dependencies

[![License: MIT](https://img.shields.io/github/license/AmirAsadyan/rubikabot)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![Dependencies: none](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](pyproject.toml)
[![GitHub stars](https://img.shields.io/github/stars/AmirAsadyan/rubikabot?style=social)](https://github.com/AmirAsadyan/rubikabot/stargazers)
[![PyPI](https://img.shields.io/pypi/v/pyrubikabot)](https://pypi.org/project/pyrubikabot/)

</div>

---

[Rubika](https://rubika.ir) is one of Iran's largest messengers, and its
Bot API is simple: one POST endpoint, a token, JSON in and out. What the
API does not give you is everything around it: routing messages to
handlers, remembering where a user is in a multi-step form, building
keypad JSON by hand, counting UTF-16 units so a formatted message is not
rejected, keeping the polling cursor across restarts.

**rubikabot is that layer.** It is built on the official
[Bot API v3](https://rubika.ir/botapi) and shaped like the frameworks
Python bot developers already know (aiogram, python-telegram-bot), so a
real bot takes tens of lines, not hundreds.

```python
from rubikabot import Bot, Dispatcher, Command

bot = Bot("TOKEN")
dp = Dispatcher(bot)

@dp.message(Command("start"))
def start(message):
    message.answer("سلام! 👋")

dp.start_polling()
```

## Contents

- [Features](#features)
- [Install](#install)
- [Your first bot](#your-first-bot)
- [Handlers and routers](#handlers-and-routers)
- [Filters](#filters)
- [Keypads](#keypads)
- [Multi-step forms with FSM](#multi-step-forms-with-fsm)
- [Formatted text](#formatted-text)
- [Files, polls, locations and contacts](#files-polls-locations-and-contacts)
- [Webhooks](#webhooks)
- [Error handling and middleware](#error-handling-and-middleware)
- [API coverage](#api-coverage)
- [Testing your bot](#testing-your-bot)
- [FAQ](#faq)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Features

| Area | What you get |
|---|---|
| **Typed models** | Dataclasses for every API object (Message, Update, InlineMessage, Chat, Keypad, Button, Poll, File, Metadata and more) and every documented enum, with `from_dict` / `to_dict`, tolerant of unknown fields |
| **Bot client** | All 19 API methods as typed methods on one `Bot` object, a pluggable HTTP transport, clear `APIError` / `TransportError` exceptions, and a token that never leaks into logs or reprs |
| **Routing** | A `Dispatcher` plus any number of `Router`s, with a decorator per update kind: messages, edited and removed messages, bot start/stop, group events and inline keypad taps |
| **Filters** | `Command`, `Text`, `ButtonId`, `ChatType`, `StateFilter`, any callable, and the magic filter `F` (`F.text == "سلام"`, `F.button_id == "buy"`), all composable with `&`, `\|` and `~` |
| **FSM** | `StatesGroup` and per chat/user `FSMContext` for multi-step conversations, stored in memory or in a JSON file |
| **Keyboards** | A fluent `KeyboardBuilder` for chat keypads and inline keypads, with row layout via `adjust()` and support for every documented button type |
| **Formatting** | `FormattedText`, a builder that tracks text and metadata parts together and counts UTF-16 units correctly (emoji included), so the API's all-or-nothing metadata validation never surprises you |
| **Running** | Long polling with a persisted offset cursor, a standard library webhook server, and framework-agnostic webhook feeding for Django, FastAPI or Flask |
| **Dependencies** | **None.** Python 3.10+ and the standard library only |

## Install

Python 3.10 or newer is required. Install from PyPI:

```bash
pip install pyrubikabot
```

> Why is the install name `pyrubikabot` but the import name
> `rubikabot`? PyPI rejects the distribution name `rubikabot` as too
> similar to the existing official `rubika-bot` project (it strips
> separators when comparing names), so the PyPI distribution is
> `pyrubikabot` while the package and import stay `rubikabot`.
> Installing straight from GitHub also works:
> `pip install git+https://github.com/AmirAsadyan/rubikabot.git`

Then create a bot with **BotFather** inside Rubika and keep the token it
gives you somewhere safe: an environment variable, a secret manager, a
file outside your repo. **Never commit a token.**

```bash
export RUBIKA_BOT_TOKEN="the token from BotFather"
```

## Your first bot

A complete bot with a menu, a poll and an echo fallback:

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
def fallback(message):
    if message.button_id == "poll":
        bot.send_poll(message.chat_id, "بات را چطور دیدی؟",
                      ["عالی", "خوب", "معمولی"])
    elif message.button_id == "about":
        message.answer("من با rubikabot ساخته شده‌ام.")
    elif message.text:
        message.answer(f"گفتی: {message.text}")

dp.start_polling(offset_file=".rubika_offset.json")
```

Run it, open your bot in Rubika, send `/start`. The offset file keeps
the polling cursor, so restarting the bot does not replay old updates.

## Handlers and routers

Every update kind has its own decorator. The handler's first argument is
the event object; ask for `state`, `bot`, `command_args` or `data` by
name and the dispatcher injects them.

| Decorator | Event you receive | Fires when |
|---|---|---|
| `@dp.message(...)` | `Message` | a new message arrives, including chat keypad taps |
| `@dp.edited_message(...)` | `Message` | a message is edited |
| `@dp.removed_message(...)` | `Update` | a message is removed |
| `@dp.started_bot(...)` / `@dp.stopped_bot(...)` | `Update` | a user starts or blocks the bot |
| `@dp.event(...)` | `Update` | the bot is added to or removed from a group, or its permissions change |
| `@dp.inline_message(...)` | `InlineMessage` | an inline keypad button is tapped |
| `@dp.update(...)` | `Update` | any update, after the kind-specific handlers |

Handlers run in registration order and the first match wins, so put
specific handlers before catch-alls. For anything bigger than one file,
split handlers into routers, one per feature, and include them:

```python
from rubikabot import Router

shop = Router("shop")

@shop.message(Command("shop"))
def open_shop(message):
    message.answer("فروشگاه باز شد.")

dp.include_router(shop)
```

Messages are bound to their chat and bot, so they can answer themselves:
`message.answer(...)`, `message.reply(...)`, `message.edit_text(...)`,
`message.delete()`. Inline messages can `answer(...)`,
`edit_text(...)` and `edit_keypad(...)` the message they belong to.

## Filters

Filters decide which handler an event goes to. They run in order, they
combine, and any plain callable taking a filter context works too.

```python
from rubikabot import ButtonId, Command, F, StateFilter, Text

@dp.message(Command("start", "help"))          # /start or /help
@dp.message(Text(equals="سلام"))               # exact text
@dp.message(Text(contains="کتاب"))             # substring
@dp.message(ButtonId("buy"))                   # a keypad tap by id
@dp.message(F.text.startswith("قیمت"))         # magic filter
@dp.message(F.sender_id.in_(["u1", "u2"]))     # admins only
@dp.message(Text(contains="کتاب") & ~Text(contains="قدیمی"))
```

A command handler can take the rest of the command line as
`command_args`: `/start ref-9` gives `command_args == "ref-9"`, which
pairs with the deep-link value in `message.start_id`.

## Keypads

Rubika has two kinds of keypads, and rubikabot handles both:

- A **chat keypad** replaces the user's keyboard. Its taps arrive as
  normal messages whose `aux_data.button_id` you can read as
  `message.button_id`, so they are handled with `@dp.message`.
- An **inline keypad** sits under a message. Its taps arrive separately
  as `InlineMessage` events and are handled with `@dp.inline_message`.

Build either one with the same builder:

```python
confirm = (KeyboardBuilder()
           .button("تأیید ✅", id="confirm")
           .button("انصراف", id="cancel")
           .adjust(2)
           .as_keypad())

message.answer("مطمئنی؟", inline_keypad=confirm)
```

```python
@dp.inline_message(F.button_id == "confirm")
def confirmed(inline):
    inline.edit_text("انجام شد ✅")
```

Buttons without an explicit `id` get sequential ids (`"1"`, `"2"`, ...).
In real flows give stable ids, because handlers match on them. Every
documented button type is available through the `type` argument and its
payload model: `Selection`, `Calendar` (Persian or Gregorian),
`NumberPicker`, `StringPicker`, `Location`,
`AskMyPhoneNumber`, `AskMyLocation`, `CameraImage`, `GalleryVideo`,
`File`, `Link`, `Barcode` and more.

To remove a chat keypad later, call `bot.edit_chat_keypad(chat_id)`
with no keypad.

## Multi-step forms with FSM

Rubika has no session concept, so rubikabot keeps one state and one data
dict per (chat, user) pair:

```python
from rubikabot import Router, State, StatesGroup, StateFilter

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

@router.message(StateFilter(Register.age))
def get_age(message, state):
    data = state.get_data()
    state.clear()
    message.answer(f"تمام شد {data['name']}، {message.text} ساله.")

dp.include_router(router)
```

State lives in memory by default. Pass a `FileStorage("fsm.json")` to
the `Dispatcher` to survive restarts, or implement the small storage
interface yourself for a database.

## Formatted text

Formatted messages are sent as plain text plus *metadata parts*: a type
(Bold, Italic, Link, MentionText, ...), a start index and a length. Two
rules make this easy to get wrong: indexes count **UTF-16 code units**
(most emoji count as 2), and **one invalid part rejects the whole
message**. `FormattedText` tracks both sides together so you cannot
drift:

```python
from rubikabot import FormattedText

msg = (FormattedText()
       .add("سلام ")
       .bold("دنیا")
       .add("! ادامه خبر در ")
       .link("سایت ما", "https://example.ir"))

bot.send_message(chat_id, msg.text, metadata=msg.metadata)
```

Available styles: `bold`, `italic`, `mono`, `underline`, `strike`,
`spoiler`, `pre`, `quote`, `link(text, url)` and
`mention(text, user_id)`. Mentions only work in group chats, per the API
docs. The builder enforces the API's limit of 30 parts and raises
`ValidationError` locally, before any request is made.

## Files, polls, locations and contacts

```python
from rubikabot.enums import FileType

# Upload once (two API steps, handled for you), then send by file_id
file_id = bot.upload_file("photo.jpg", FileType.IMAGE)
bot.send_file(chat_id, file_id, text="این هم عکس")

# Or both in one call
bot.send_uploaded_file(chat_id, "report.pdf", FileType.FILE)

# Download what a user sent you
data = bot.download_file(message.file.file_id)   # bytes

bot.send_poll(chat_id, "نظرت؟", ["موافق", "مخالف"])
bot.send_location(chat_id, "35.6892", "51.3890")   # Tehran
bot.send_contact(chat_id, "پشتیبانی", "روبیکابات", "09000000000")
```

Documented upload limits: generic files and mp4 video up to **50 MB**,
images (jpg, gif, png, webp) up to **10 MB**, voice and music as mp3,
and a Gif as a **silent mp4**.

Group moderation is two calls, and never applies to the owner or
admins:

```python
bot.ban_chat_member(chat_id, user_id)
bot.unban_chat_member(chat_id, user_id)
```

## Webhooks

Polling is the easiest way to run a bot. For production, webhooks push
updates to you the moment they happen. Rubika connects only to public
HTTPS addresses, and each update kind gets its own endpoint:

```python
from rubikabot import serve

bot.register_webhooks("https://your.public.domain")
serve(dp, port=8080)   # put your HTTPS reverse proxy in front of this
```

Already running Django, FastAPI or Flask? Skip the built-in server and
feed payloads from your own views:

```python
dp.handle_webhook_payload("update", request_body)   # receiveUpdate
dp.handle_webhook_payload("inline", request_body)   # receiveInlineMessage
```

| | Polling | Webhook |
|---|---|---|
| Setup | none, works anywhere | public domain + HTTPS |
| Latency | seconds, by interval | instant |
| Best for | development, small bots, no server | production |

## Error handling and middleware

API failures raise `APIError` with the method name, the decoded payload
and the HTTP status; network and parsing failures raise
`TransportError`. Inside handlers, register an error handler instead of
letting the polling loop print tracebacks:

```python
@dp.errors
def on_error(event, error):
    print("handler failed:", error)
    return True   # mark handled
```

Middleware wraps every matched handler and is the right place for
logging, timing, rate limits or an admin gate:

```python
@dp.middleware
def log_calls(handler, event, data):
    print("update from", getattr(event, "chat_id", "?"))
    return handler(event, data)
```

## API coverage

All 19 methods of Bot API v3, as methods of `Bot`:

| API method | rubikabot |
|---|---|
| `getMe` | `bot.get_me()` → `BotInfo` |
| `sendMessage` | `bot.send_message(chat_id, text, ...)` → message_id |
| `sendPoll` | `bot.send_poll(chat_id, question, options)` |
| `sendLocation` | `bot.send_location(chat_id, latitude, longitude)` |
| `sendContact` | `bot.send_contact(chat_id, first_name, last_name, phone_number)` |
| `getChat` | `bot.get_chat(chat_id)` → `Chat` |
| `getUpdates` | `bot.get_updates(offset_id, limit)` → `UpdatesPage` |
| `forwardMessage` | `bot.forward_message(from_chat_id, message_id, to_chat_id)` |
| `editMessageText` | `bot.edit_message_text(chat_id, message_id, text)` |
| `editMessageKeypad` | `bot.edit_message_keypad(chat_id, message_id, keypad)` |
| `deleteMessage` | `bot.delete_message(chat_id, message_id)` |
| `setCommands` | `bot.set_commands([BotCommand(...)])` |
| `updateBotEndpoints` | `bot.update_bot_endpoints(url, type)` or `bot.register_webhooks(base_url)` |
| `editChatKeypad` | `bot.edit_chat_keypad(chat_id, keypad_or_None)` |
| `getFile` | `bot.get_file(file_id)` → download URL |
| `sendFile` | `bot.send_file(chat_id, file_id, text=None)` |
| `requestSendFile` | handled inside `bot.upload_file(path, file_type)` |
| `banChatMember` | `bot.ban_chat_member(chat_id, user_id)` |
| `unbanChatMember` | `bot.unban_chat_member(chat_id, user_id)` |

Anything the typed methods do not cover is one call away with
`bot.api_call("methodName", **params)`, and the HTTP transport is
replaceable: pass any object with `post_json`, `post_multipart` and
`get_bytes` to `Bot(token, transport=...)`.

## Testing your bot

Handlers are plain functions, so they test well without a network or a
token: build a `Bot` on a fake transport, feed update dicts into the
dispatcher, and assert on the calls the fake recorded. The library's own
suite in [tests/](tests) does exactly this for every feature; copy its
`fake_transport.py` as a starting point.

```bash
python -m unittest discover -s tests -v
```

## FAQ

**Where do I get a token?**
From **BotFather** inside Rubika. Create the bot there and keep the
token secret.

**Is this the `rubika_bot` package from the official examples?**
No. The official docs' examples import a thin function-based package
(PyPI `rubika-bot`, import name `rubika_bot`) where you pass the token
into every call. rubikabot (one word, import name `rubikabot`) is the
framework layer on top of the same API: a `Bot` object, typed models,
routing, FSM and builders. Do not mix the two import names.

**The docs say polling uses `start_id`, but the library uses
`offset_id`. Why?**
Because the docs contradict themselves. The overview page mentions
`start_id` for polling; the methods page defines `getUpdates` with
`offset_id` in and `next_offset_id` out, which is what the live API
accepts, so the library follows the methods page. (`start_id` is a real
field, but it lives in `aux_data` and means the deep-link value a user
entered the bot with. Read it as `message.start_id`.)

**Can I use rubikabot with Django or FastAPI?**
Yes. Create one `Bot` and one `Dispatcher` in your project, register
webhooks to your own URLs, and call `dp.handle_webhook_payload(...)`
from your views. The FSM storage interface is small enough to back with
your database.

**Does rubikabot support async?**
Version 0.1 is synchronous by design: the API is plain HTTP and sync
keeps the code and the mental model simple. The transport interface is
the seam where an async client can land later without breaking handler
code.

## Roadmap

- Async client with the same handler API
- More storage backends for FSM (SQLite, Redis)
- Selection-item endpoints (`GetSelectionItem`, `SearchSelectionItems`)
  helpers

## Contributing

Issues and pull requests are welcome. Please read
[CONTRIBUTING.md](CONTRIBUTING.md) first: field names follow the
official docs (methods page wins), runtime dependencies stay at zero,
and every behaviour change needs an offline test.

## License

MIT. See [LICENSE](LICENSE).

<div align="center">

Made for the Rubika developer community · [Official Bot API docs](https://rubika.ir/botapi)

</div>
