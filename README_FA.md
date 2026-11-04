# روبیکابات (rubikabot)

یک فریم‌ورک مدرن پایتون برای ساخت بات‌های [روبیکا](https://rubika.ir)، با
الهام از aiogram و python-telegram-bot، بر پایه API رسمی بات روبیکا
نسخه ۳.

## چرا یک کتابخانه دیگر؟

مثال‌های رسمی داکیومنت روبیکا از یک پکیج کوچک تابعی استفاده می‌کنند:
توکن را به تک‌تک فراخوانی‌ها می‌دهی، با دیکشنری خام کار می‌کنی و حلقه
دریافت آپدیت، مسیریابی پیام‌ها، نگه‌داری وضعیت گفتگو و ساخت JSON
کی‌پدها همه با خودت است. روبیکابات همان لایه‌ای را می‌دهد که یک بات
واقعی لازم دارد:

- **مدل‌های تایپ‌دار** برای همه اشیای API و Enumها، با `from_dict` و
  `to_dict`
- **کلاینت `Bot`** با پوشش هر ۱۹ متد API و ترانسپورت HTTP قابل تعویض
- **دیسپچر و روتر** با دکوراتور برای هر نوع آپدیت و فیلترهای قابل ترکیب،
  از جمله فیلتر جادویی (`F.text == "سلام"`)
- **ماشین حالت (FSM)** با گروه وضعیت و ذخیره‌سازی به‌ازای هر چت و کاربر،
  در حافظه یا فایل JSON
- **سازنده کی‌پد** برای کی‌پد چت و کی‌پد شیشه‌ای (Inline)
- **قالب‌بندی متن** با رعایت قواعد متادیتای UTF-16 روبیکا؛ API با یک
  متادیتای نامعتبر کل پیام را رد می‌کند
- **اجرا با Polling و Webhook**، به‌همراه یک سرور وب‌هوک با کتابخانه
  استاندارد پایتون
- **بدون هیچ وابستگی خارجی.** فقط پایتون ۳٫۱۰ به بالا

## نصب

```bash
pip install rubikabot
```

تا قبل از انتشار روی PyPI، از گیت‌هاب نصب کن:

```bash
pip install git+https://github.com/AmirAsadyan/rubikabot.git
```

## شروع سریع

اول با BotFather در روبیکا یک بات بساز و توکن را امن نگه دار:

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
    elif message.text:
        message.answer(f"گفتی: {message.text}")

dp.start_polling(offset_file=".rubika_offset.json")
```

## فرم چندمرحله‌ای با FSM

```python
from rubikabot import Router, State, StatesGroup, StateFilter

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
```

نمونه کامل در [examples/form_bot.py](examples/form_bot.py) است.

## نکات مهم API که کتابخانه رعایت می‌کند

- کرسر Polling طبق صفحه متدهای داک `offset_id` و `next_offset_id` است،
  نه `start_id` که صفحه معرفی نوشته. مقدار `start_id` واقعی داخل
  `aux_data` است و یعنی پارامتر لینک ورود کاربر به بات.
- نام متد ثبت وب‌هوک `updateBotEndpoints` (جمع) است.
- آپلود فایل دو مرحله‌ای است: `requestSendFile` آدرس آپلود می‌دهد و بعد
  فایل با multipart به همان آدرس می‌رود. هر دو مرحله داخل
  `bot.upload_file(...)` انجام می‌شود.
- سقف فایل: فایل عمومی و ویدیو ۵۰ مگابایت، عکس ۱۰ مگابایت، گیف mp4
  بدون صدا.

## پوشش API

هر ۱۹ متد Bot API v3: ‏`getMe`، ‏`sendMessage`، ‏`sendPoll`،
‏`sendLocation`، ‏`sendContact`، ‏`getChat`، ‏`getUpdates`،
‏`forwardMessage`، ‏`editMessageText`، ‏`editMessageKeypad`،
‏`deleteMessage`، ‏`setCommands`، ‏`updateBotEndpoints`،
‏`editChatKeypad`، ‏`getFile`، ‏`sendFile`، ‏`requestSendFile`،
‏`banChatMember` و ‏`unbanChatMember`.

## توسعه و تست

```bash
python -m unittest discover -s tests -v
```

کل تست‌ها آفلاین و با ترانسپورت جعلی اجرا می‌شوند؛ نه توکن لازم است نه
شبکه.

## مجوز

MIT. فایل [LICENSE](LICENSE) را ببین.
