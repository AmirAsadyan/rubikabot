<div dir="rtl" align="center">

# روبیکابات (rubikabot)

**فریم‌ورک مدرن پایتون برای ساخت بات‌های روبیکا**

مدل‌های تایپ‌دار · دیسپچر و روتر · فیلترها · FSM · سازنده کی‌پد · بدون هیچ وابستگی

[![License: MIT](https://img.shields.io/github/license/AmirAsadyan/rubikabot)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![Dependencies: none](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](pyproject.toml)
[![GitHub stars](https://img.shields.io/github/stars/AmirAsadyan/rubikabot?style=social)](https://github.com/AmirAsadyan/rubikabot/stargazers)

[English](README.md) · **فارسی**

</div>

<div dir="rtl">

روبیکا یکی از بزرگ‌ترین پیام‌رسان‌های ایران است و API باتش ساده است: یک
آدرس POST، یک توکن، و JSON در ورودی و خروجی. اما API همه چیزهای دوروبرش
را به شما نمی‌دهد: رساندن هر پیام به هندلر درست، یادآوری اینکه کاربر در
کدام مرحله یک فرم چندمرحله‌ای است، ساختن JSON کی‌پد با دست، شمردن
واحدهای UTF-16 تا یک پیام فرمت‌دار رد نشود، نگه‌داشتن کرسر پولینگ بین
ری‌استارت‌ها.

**روبیکابات دقیقاً همین لایه است.** بر پایه
[API رسمی بات روبیکا نسخه ۳](https://rubika.ir/botapi) ساخته شده و شکلش
مثل فریم‌ورک‌هایی است که توسعه‌دهنده‌های بات پایتون از قبل می‌شناسند
(aiogram و python-telegram-bot)، تا یک بات واقعی ده‌ها خط شود، نه صدها خط.

</div>

```python
from rubikabot import Bot, Dispatcher, Command

bot = Bot("TOKEN")
dp = Dispatcher(bot)

@dp.message(Command("start"))
def start(message):
    message.answer("سلام! 👋")

dp.start_polling()
```

<div dir="rtl">

## فهرست

- [امکانات](#امکانات)
- [نصب](#نصب)
- [اولین بات شما](#اولین-بات-شما)
- [هندلرها و روترها](#هندلرها-و-روترها)
- [فیلترها](#فیلترها)
- [کی‌پدها](#کیپدها)
- [فرم‌های چندمرحله‌ای با FSM](#فرمهای-چندمرحلهای-با-fsm)
- [متن فرمت‌دار](#متن-فرمتدار)
- [فایل، نظرسنجی، موقعیت و مخاطب](#فایل-نظرسنجی-موقعیت-و-مخاطب)
- [وب‌هوک](#وبهوک)
- [مدیریت خطا و میدل‌ویر](#مدیریت-خطا-و-میدلویر)
- [پوشش API](#پوشش-api)
- [تست‌کردن بات](#تستکردن-بات)
- [سؤالات پرتکرار](#سؤالات-پرتکرار)
- [نقشه راه](#نقشه-راه)
- [مشارکت](#مشارکت)
- [مجوز](#مجوز)

## امکانات

| بخش | چه چیزی می‌گیرید |
|---|---|
| **مدل‌های تایپ‌دار** | دیتاکلس برای همه اشیای API (Message ،Update ،InlineMessage ،Chat ،Keypad ،Button ،Poll ،File ،Metadata و بیشتر) و همه اینام‌های مستند، با `from_dict` و `to_dict` و سازگار با فیلدهای ناشناخته آینده |
| **کلاینت بات** | هر ۱۹ متد API به‌صورت متد تایپ‌دار روی یک آبجکت `Bot`، ترانسپورت HTTP قابل تعویض، خطاهای واضح `APIError` و `TransportError`، و توکنی که هرگز در لاگ یا repr چاپ نمی‌شود |
| **مسیریابی** | یک `Dispatcher` و هر تعداد `Router`، با دکوراتور جدا برای هر نوع آپدیت: پیام، ویرایش و حذف پیام، شروع و بلاک بات، رویدادهای گروه و کلیک کی‌پد اینلاین |
| **فیلترها** | ‏`Command` ،`Text` ،`ButtonId` ،`ChatType` ،`StateFilter`، هر تابع ساده، و فیلتر جادویی `F` (مثل `F.text == "سلام"`)، همه قابل ترکیب با `&` و `\|` و `~` |
| **FSM** | ‏`StatesGroup` و `FSMContext` جدا برای هر (چت، کاربر) برای گفتگوهای چندمرحله‌ای، در حافظه یا در فایل JSON |
| **کیبورد** | سازنده روان `KeyboardBuilder` برای کی‌پد چت و اینلاین، چیدمان سطری با `adjust()` و پشتیبانی از همه انواع دکمه مستند |
| **فرمت‌بندی** | ‏`FormattedText`: سازنده‌ای که متن و قطعه‌های متادیتا را با هم نگه می‌دارد و واحدهای UTF-16 را درست می‌شمارد (اموجی‌ها هم)، تا اعتبارسنجی همه‌یا‌هیچ متادیتای API غافلگیرتان نکند |
| **اجرا** | پولینگ با ذخیره کرسر آفست روی دیسک، سرور وب‌هوک با کتابخانه استاندارد، و تغذیه وب‌هوک در هر فریم‌ورک (Django ،FastAPI ،Flask) |
| **وابستگی** | **هیچ.** فقط پایتون 3.10 به بالا و کتابخانه استاندارد |

## نصب

پایتون 3.10 یا جدیدتر لازم است. تا انتشار اول روی PyPI، نصب از گیت‌هاب:

</div>

```bash
pip install git+https://github.com/AmirAsadyan/rubikabot.git
```

<div dir="rtl">

> به‌محض انتشار پکیج روی PyPI، دستور `pip install rubikabot` هم کار
> می‌کند. این نام برای همین پروژه است.

بعد با **BotFather** داخل روبیکا یک بات بسازید و توکنی که می‌دهد را جای
امنی نگه دارید: متغیر محیطی، سیکرت‌منیجر، یا فایلی بیرون از ریپو.
**توکن را هرگز کامیت نکنید.**

</div>

```bash
export RUBIKA_BOT_TOKEN="توکنی که از BotFather گرفتید"
```

<div dir="rtl">

## اولین بات شما

یک بات کامل با منو، نظرسنجی و اکوی پیش‌فرض:

</div>

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

<div dir="rtl">

اجرا کنید، بات را در روبیکا باز کنید و `/start` بفرستید. فایل آفست کرسر
پولینگ را نگه می‌دارد، پس ری‌استارت بات آپدیت‌های قدیمی را دوباره پخش
نمی‌کند.

## هندلرها و روترها

هر نوع آپدیت دکوراتور خودش را دارد. آرگومان اول هندلر آبجکت رویداد است؛
`state` ،`bot` ،`command_args` یا `data` را اگر در امضای تابع بنویسید،
دیسپچر خودش تزریق می‌کند.

| دکوراتور | رویدادی که می‌گیرید | کی اجرا می‌شود |
|---|---|---|
| ‏`@dp.message(...)` | ‏`Message` | پیام جدید رسید، از جمله کلیک روی کی‌پد چت |
| ‏`@dp.edited_message(...)` | ‏`Message` | پیامی ویرایش شد |
| ‏`@dp.removed_message(...)` | ‏`Update` | پیامی حذف شد |
| ‏`@dp.started_bot(...)` و `@dp.stopped_bot(...)` | ‏`Update` | کاربر بات را شروع یا بلاک کرد |
| ‏`@dp.event(...)` | ‏`Update` | بات به گروه اضافه یا حذف شد، یا دسترسی‌هایش عوض شد |
| ‏`@dp.inline_message(...)` | ‏`InlineMessage` | روی دکمه کی‌پد اینلاین کلیک شد |
| ‏`@dp.update(...)` | ‏`Update` | هر آپدیتی، بعد از هندلرهای مخصوص خودش |

هندلرها به ترتیب ثبت اجرا می‌شوند و اولی که بخورد برنده است؛ پس هندلرهای
خاص را قبل از هندلرهای کلی بگذارید. برای پروژه‌های بزرگ‌تر از یک فایل،
هندلرها را در روترها جدا کنید، یکی برای هر قابلیت:

</div>

```python
from rubikabot import Router

shop = Router("shop")

@shop.message(Command("shop"))
def open_shop(message):
    message.answer("فروشگاه باز شد.")

dp.include_router(shop)
```

<div dir="rtl">

پیام‌ها به چت و بات خودشان وصل‌اند و خودشان می‌توانند جواب بدهند:
`message.answer(...)` ،`message.reply(...)` ،`message.edit_text(...)` و
`message.delete()`. پیام‌های اینلاین هم روی پیام متعلق به خودشان
`answer(...)` ،`edit_text(...)` و `edit_keypad(...)` دارند.

## فیلترها

فیلترها تصمیم می‌گیرند هر رویداد به کدام هندلر برسد. به ترتیب اجرا
می‌شوند، با هم ترکیب می‌شوند، و هر تابع ساده‌ای که کانتکست فیلتر بگیرد
هم کار می‌کند.

</div>

```python
from rubikabot import ButtonId, Command, F, StateFilter, Text

@dp.message(Command("start", "help"))          # ‏/start یا /help
@dp.message(Text(equals="سلام"))               # متن دقیق
@dp.message(Text(contains="کتاب"))             # شامل زیریرشته
@dp.message(ButtonId("buy"))                   # کلیک کی‌پد با آیدی
@dp.message(F.text.startswith("قیمت"))         # فیلتر جادویی
@dp.message(F.sender_id.in_(["u1", "u2"]))     # فقط ادمین‌ها
@dp.message(Text(contains="کتاب") & ~Text(contains="قدیمی"))
```

<div dir="rtl">

هندلر کامند می‌تواند ادامه خط فرمان را با اسم `command_args` بگیرد:
برای `/start ref-9` مقدار `command_args` برابر `"ref-9"` است؛ همان مقداری
که برای دیپ‌لینک در `message.start_id` هم می‌آید.

## کی‌پدها

روبیکا دو جور کی‌پد دارد و روبیکابات هر دو را پوشش می‌دهد:

- **کی‌پد چت** جای کیبورد کاربر را می‌گیرد. کلیک‌هایش مثل پیام عادی
  می‌رسند و آیدی دکمه از `message.button_id` خوانده می‌شود؛ پس با
  `@dp.message` هندل می‌شوند.
- **کی‌پد اینلاین** زیر یک پیام می‌نشیند. کلیک‌هایش جدا و به‌صورت
  رویداد `InlineMessage` می‌رسند و با `@dp.inline_message` هندل
  می‌شوند.

هر دو را با یک سازنده بسازید:

</div>

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

<div dir="rtl">

دکمه‌های بدون `id` آیدی ترتیبی می‌گیرند (`"1"` ،`"2"` و …). در فلوی واقعی
آیدی ثابت بدهید، چون هندلرها روی همان‌ها مچ می‌شوند. همه انواع دکمه مستند
از راه آرگومان `type` و مدل پی‌لودشان در دسترس‌اند: `Selection` ،`Calendar`
(جلالی یا میلادی)، `NumberPicker` ،`StringPicker` ،`Location`،
`AskMyPhoneNumber` ،`AskMyLocation` ،`CameraImage` ،`GalleryVideo`،
`File` ،`Link` ،`Barcode` و بیشتر.

برای حذف کی‌پد چت در ادامه، `bot.edit_chat_keypad(chat_id)` را بدون
کی‌پد صدا بزنید.

## فرم‌های چندمرحله‌ای با FSM

روبیکا مفهوم سشن ندارد، پس روبیکابات برای هر جفت (چت، کاربر) یک وضعیت و
یک دیکشنری دیتا نگه می‌دارد:

</div>

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

<div dir="rtl">

وضعیت پیش‌فرض در حافظه است. برای بقا بین ری‌استارت‌ها به `Dispatcher`
یک `FileStorage("fsm.json")` بدهید، یا اینترفیس کوچک ذخیره‌سازی را
خودتان برای دیتابیس پیاده کنید.

## متن فرمت‌دار

پیام فرمت‌دار یعنی متن ساده به‌همراه **قطعه‌های متادیتا**: یک نوع
(Bold ،Italic ،Link ،MentionText و …)، یک اندیس شروع و یک طول. دو قانون
این کار را خطاپذیر می‌کند: اندیس‌ها **واحد UTF-16** می‌شمارند (بیشتر
اموجی‌ها ۲ واحدند) و **یک قطعه نامعتبر کل پیام را رد می‌کند**.
`FormattedText` هر دو طرف را با هم نگه می‌دارد تا از هم جا نمانند:

</div>

```python
from rubikabot import FormattedText

msg = (FormattedText()
       .add("سلام ")
       .bold("دنیا")
       .add("! ادامه خبر در ")
       .link("سایت ما", "https://example.ir"))

bot.send_message(chat_id, msg.text, metadata=msg.metadata)
```

<div dir="rtl">

استایل‌های موجود: `bold` ،`italic` ،`mono` ،`underline` ،`strike`،
`spoiler` ،`pre` ،`quote` ،`link(text, url)` و
`mention(text, user_id)`. منشن طبق مستندات API فقط در چت‌های گروهی کار
می‌کند. سازنده سقف ۳۰ قطعه API را هم لوکال اعمال می‌کند و قبل از هر
درخواستی `ValidationError` می‌دهد.

## فایل، نظرسنجی، موقعیت و مخاطب

</div>

```python
from rubikabot.enums import FileType

# یک بار آپلود (دو مرحله API، خودکار انجام می‌شود)، بعد ارسال با file_id
file_id = bot.upload_file("photo.jpg", FileType.IMAGE)
bot.send_file(chat_id, file_id, text="این هم عکس")

# یا هر دو در یک صدا
bot.send_uploaded_file(chat_id, "report.pdf", FileType.FILE)

# دانلود چیزی که کاربر فرستاده
data = bot.download_file(message.file.file_id)   # بایت

bot.send_poll(chat_id, "نظرت؟", ["موافق", "مخالف"])
bot.send_location(chat_id, "35.6892", "51.3890")   # تهران
bot.send_contact(chat_id, "پشتیبانی", "روبیکابات", "09000000000")
```

<div dir="rtl">

سقف‌های مستند آپلود: فایل عمومی و ویدیوی mp4 تا **۵۰ مگابایت**، تصویر
(jpg ،gif ،png ،webp) تا **۱۰ مگابایت**، ویس و موزیک به صورت mp3، و Gif
به‌صورت **mp4 بی‌صدا**.

مدیریت گروه دو صداست و روی مالک و ادمین‌ها اعمال نمی‌شود:

</div>

```python
bot.ban_chat_member(chat_id, user_id)
bot.unban_chat_member(chat_id, user_id)
```

<div dir="rtl">

## وب‌هوک

پولینگ راحت‌ترین راه اجرای بات است. برای پروداکشن، وب‌هوک آپدیت را همان
لحظه به شما می‌رساند. روبیکا فقط به آدرس‌های عمومی HTTPS وصل می‌شود و
هر نوع آپدیت اندپوینت خودش را می‌گیرد:

</div>

```python
from rubikabot import serve

bot.register_webhooks("https://your.public.domain")
serve(dp, port=8080)   # پروکسی HTTPS خود را جلوی این بگذارید
```

<div dir="rtl">

از قبل Django یا FastAPI یا Flask دارید؟ سرور داخلی را کنار بگذارید و
پی‌لودها را از ویوهای خودتان بدهید:

</div>

```python
dp.handle_webhook_payload("update", request_body)   # receiveUpdate
dp.handle_webhook_payload("inline", request_body)   # receiveInlineMessage
```

<div dir="rtl">

| | پولینگ | وب‌هوک |
|---|---|---|
| راه‌اندازی | هیچ، همه‌جا کار می‌کند | دامنه عمومی + HTTPS |
| تأخیر | چند ثانیه، به فاصله پولینگ | فوری |
| مناسب برای | توسعه، بات‌های کوچک، بدون سرور | پروداکشن |

## مدیریت خطا و میدل‌ویر

خطای API، `APIError` می‌دهد با نام متد، پی‌لود دیکودشده و کد وضعیت
HTTP؛ خطای شبکه و پارس، `TransportError`. داخل هندلرها، به‌جای تریس‌بک در
حلقه پولینگ، هندلر خطا ثبت کنید:

</div>

```python
@dp.errors
def on_error(event, error):
    print("handler failed:", error)
    return True   # خطا هندل شد
```

<div dir="rtl">

میدل‌ویر دور همه هندلرهای مچ‌شده می‌پیچد و جای درست لاگ، زمان‌گیری،
ریت‌لیمیت یا گیت ادمین است:

</div>

```python
@dp.middleware
def log_calls(handler, event, data):
    print("update from", getattr(event, "chat_id", "?"))
    return handler(event, data)
```

<div dir="rtl">

## پوشش API

هر ۱۹ متد API نسخه ۳، به‌صورت متد روی `Bot`:

| متد API | در روبیکابات |
|---|---|
| ‏`getMe` | ‏`bot.get_me()` ← ‏`BotInfo` |
| ‏`sendMessage` | ‏`bot.send_message(chat_id, text, ...)` ← آیدی پیام |
| ‏`sendPoll` | ‏`bot.send_poll(chat_id, question, options)` |
| ‏`sendLocation` | ‏`bot.send_location(chat_id, latitude, longitude)` |
| ‏`sendContact` | ‏`bot.send_contact(chat_id, first_name, last_name, phone_number)` |
| ‏`getChat` | ‏`bot.get_chat(chat_id)` ← ‏`Chat` |
| ‏`getUpdates` | ‏`bot.get_updates(offset_id, limit)` ← ‏`UpdatesPage` |
| ‏`forwardMessage` | ‏`bot.forward_message(from_chat_id, message_id, to_chat_id)` |
| ‏`editMessageText` | ‏`bot.edit_message_text(chat_id, message_id, text)` |
| ‏`editMessageKeypad` | ‏`bot.edit_message_keypad(chat_id, message_id, keypad)` |
| ‏`deleteMessage` | ‏`bot.delete_message(chat_id, message_id)` |
| ‏`setCommands` | ‏`bot.set_commands([BotCommand(...)])` |
| ‏`updateBotEndpoints` | ‏`bot.update_bot_endpoints(url, type)` یا `bot.register_webhooks(base_url)` |
| ‏`editChatKeypad` | ‏`bot.edit_chat_keypad(chat_id, keypad_or_None)` |
| ‏`getFile` | ‏`bot.get_file(file_id)` ← آدرس دانلود |
| ‏`sendFile` | ‏`bot.send_file(chat_id, file_id, text=None)` |
| ‏`requestSendFile` | داخل `bot.upload_file(path, file_type)` انجام می‌شود |
| ‏`banChatMember` | ‏`bot.ban_chat_member(chat_id, user_id)` |
| ‏`unbanChatMember` | ‏`bot.unban_chat_member(chat_id, user_id)` |

هر چیزی که متدهای تایپ‌دار پوشش ندهند، یک صدا فاصله دارد:
`bot.api_call("methodName", **params)`. ترانسپورت HTTP هم قابل تعویض
است: هر آبجکتی با `post_json` و `post_multipart` و `get_bytes` را به
`Bot(token, transport=...)` بدهید.

## تست‌کردن بات

هندلرها تابع‌های ساده‌اند و بدون شبکه و توکن خوب تست می‌شوند: یک `Bot`
روی ترانسپورت فیک بسازید، دیکت‌های آپدیت را به دیسپچر بدهید و روی صداهایی
که فیک ضبط کرده اسرت کنید. سوئیت خود کتابخانه در [tests/](tests) دقیقاً
همین کار را برای همه امکانات می‌کند؛ فایل `fake_transport.py` آن نقطه
شروع خوبی است.

</div>

```bash
python -m unittest discover -s tests -v
```

<div dir="rtl">

## سؤالات پرتکرار

**توکن را از کجا بگیرم؟**
از **BotFather** داخل روبیکا. بات را آنجا بسازید و توکن را محرمانه نگه
دارید.

**این همان پکیج `rubika_bot` مثال‌های رسمی است؟**
نه. مثال‌های مستندات رسمی از یک پکیج تابعیِ نازک ایمپورت می‌کنند (روی
PyPI با نام `rubika-bot` و اسم ایمپورت `rubika_bot`) که در آن توکن را
داخل هر صدا پاس می‌دهید. روبیکابات (یک کلمه، اسم ایمپورت `rubikabot`)
لایه فریم‌ورکی روی همان API است: آبجکت `Bot`، مدل‌های تایپ‌دار، مسیریابی،
FSM و سازنده‌ها. دو اسم ایمپورت را با هم قاطی نکنید.

**مستندات می‌گوید پولینگ با `start_id` است، ولی کتابخانه `offset_id`
استفاده می‌کند؛ چرا؟**
چون مستندات با خودش تناقض دارد. صفحه معرفی برای پولینگ از `start_id`
می‌گوید؛ صفحه متدها `getUpdates` را با `offset_id` در ورودی و
`next_offset_id` در خروجی تعریف می‌کند و API زنده همان را قبول می‌کند،
پس کتابخانه صفحه متدها را دنبال می‌کند. (`start_id` فیلد واقعی است، ولی
داخل `aux_data` زندگی می‌کند و یعنی مقدار دیپ‌لینکی که کاربر با آن وارد
بات شده؛ آن را از `message.start_id` بخوانید.)

**با Django یا FastAPI هم می‌شود استفاده کرد؟**
بله. یک `Bot` و یک `Dispatcher` در پروژه‌تان بسازید، وب‌هوک‌ها را روی
آدرس‌های خودتان ثبت کنید و از ویوها `dp.handle_webhook_payload(...)` را
صدا بزنید. اینترفیس ذخیره‌سازی FSM آن‌قدر کوچک است که با دیتابیس خودتان
هم پشتش می‌نشیند.

**روبیکابات async هم دارد؟**
نسخه ۰٫۱ عمداً سنکرون است: API، HTTP ساده است و سنکرون‌بودن کد و مدل
ذهنی را ساده نگه می‌دارد. اینترفیس ترانسپورت همان درزی است که بعداً
کلاینت async بدون شکستن کد هندلرها می‌تواند رویش بنشیند.

## نقشه راه

- انتشار روی PyPI (‏`pip install rubikabot`)
- کلاینت async با همان API هندلرها
- بک‌اندهای بیشتر برای FSM (SQLite ،Redis)
- هلپر برای اندپوینت‌های آیتم انتخاب (`GetSelectionItem` ،`SearchSelectionItems`)

## مشارکت

ایشو و پول‌ریکوئست خوش‌آمد است. اول [CONTRIBUTING.md](CONTRIBUTING.md)
را بخوانید: نام فیلدها تابع مستندات رسمی‌اند (صفحه متدها برنده است)،
وابستگی ران‌تایم صفر می‌ماند، و هر تغییر رفتاری یک تست آفلاین می‌خواهد.

## مجوز

MIT. متن کامل در [LICENSE](LICENSE).

</div>

<div dir="rtl" align="center">

ساخته‌شده برای جامعه توسعه‌دهنده‌های روبیکا · [مستندات رسمی Bot API](https://rubika.ir/botapi)

</div>
