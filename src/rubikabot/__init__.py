"""rubikabot: a modern Python framework for Rubika bots.

Built on the official Rubika Bot API v3 (https://rubika.ir/botapi) with
typed models, a Bot client with zero runtime dependencies, a
dispatcher/router system with filters and FSM, keyboard builders and
text formatting helpers.

Quick start:
    from rubikabot import Bot, Dispatcher, Command

    bot = Bot("TOKEN")
    dp = Dispatcher(bot)

    @dp.message(Command("start"))
    def start(message):
        message.answer("سلام!")

    dp.start_polling()
"""

from . import enums, types
from .client import API_BASE, Bot
from .dispatcher import Dispatcher, Router
from .errors import APIError, RubikaBotError, TransportError, \
    ValidationError
from .filters import F, ButtonId, ChatType, Command, CommandStart, \
    Filter, StateFilter, Text
from .formatting import FormattedText, make_part, utf16_len
from .fsm import FSMContext, FileStorage, MemoryStorage, State, \
    StatesGroup
from .keyboards import KeyboardBuilder, keypad_from_rows
from .types import (AuxData, BotCommand, BotInfo, Button, Chat,
                    ContactMessage, Event, File, InlineMessage, Keypad,
                    KeypadRow, Location, Message, Metadata, MetadataPart,
                    Poll, Sticker, Update, UpdatesPage)
from .webhook import serve

__version__ = "0.1.0"

__all__ = [
    "API_BASE",
    "APIError",
    "AuxData",
    "Bot",
    "BotCommand",
    "BotInfo",
    "Button",
    "ButtonId",
    "Chat",
    "ChatType",
    "Command",
    "CommandStart",
    "ContactMessage",
    "Dispatcher",
    "Event",
    "F",
    "FSMContext",
    "File",
    "FileStorage",
    "Filter",
    "FormattedText",
    "InlineMessage",
    "KeyboardBuilder",
    "Keypad",
    "KeypadRow",
    "Location",
    "MemoryStorage",
    "Message",
    "Metadata",
    "MetadataPart",
    "Poll",
    "Router",
    "RubikaBotError",
    "State",
    "StateFilter",
    "StatesGroup",
    "Sticker",
    "Text",
    "TransportError",
    "Update",
    "UpdatesPage",
    "ValidationError",
    "__version__",
    "enums",
    "keypad_from_rows",
    "make_part",
    "serve",
    "types",
    "utf16_len",
]
