"""Typed data models of the Rubika Bot API v3.

Every model is a dataclass with ``from_dict`` and ``to_dict``. Field names
and shapes follow https://rubika.ir/botapi/models. Unknown fields sent by
the API are ignored, and fields missing from a payload stay ``None``, so a
docs or API change never breaks parsing.
"""

from __future__ import annotations

import dataclasses
import types as _stdlib_types
import typing
from dataclasses import dataclass, field
from enum import Enum

from . import enums


def _convert(hint, value):
    if value is None:
        return None
    origin = typing.get_origin(hint)
    if origin is typing.Union or origin is _stdlib_types.UnionType:
        args = [a for a in typing.get_args(hint) if a is not type(None)]
        if len(args) == 1:
            return _convert(args[0], value)
        return value
    if origin in (list, tuple):
        (item_hint,) = typing.get_args(hint) or (typing.Any,)
        if isinstance(value, list):
            return [_convert(item_hint, item) for item in value]
        return value
    if isinstance(hint, type) and issubclass(hint, APIModel):
        if isinstance(value, dict):
            return hint.from_dict(value)
        return value
    if isinstance(hint, type) and issubclass(hint, Enum):
        try:
            return hint(value)
        except ValueError:
            return value
    return value


def _dump(value):
    if isinstance(value, APIModel):
        return value.to_dict()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (list, tuple)):
        return [_dump(item) for item in value]
    if isinstance(value, dict):
        return {key: _dump(item) for key, item in value.items()}
    return value


class APIModel:
    """Base class giving dataclasses API conversion."""

    @classmethod
    def from_dict(cls, data: dict):
        if not isinstance(data, dict):
            raise TypeError(f"{cls.__name__}.from_dict expects a dict")
        hints = typing.get_type_hints(cls)
        kwargs = {}
        for f in dataclasses.fields(cls):
            if f.name in data:
                kwargs[f.name] = _convert(hints.get(f.name, typing.Any),
                                          data[f.name])
        return cls(**kwargs)

    def to_dict(self) -> dict:
        result = {}
        for f in dataclasses.fields(self):
            value = getattr(self, f.name)
            if value is None:
                continue
            result[f.name] = _dump(value)
        return result


@dataclass
class File(APIModel):
    file_id: str | None = None
    file_name: str | None = None
    size: str | None = None


@dataclass
class Location(APIModel):
    longitude: str | None = None
    latitude: str | None = None


@dataclass
class AuxData(APIModel):
    start_id: str | None = None
    button_id: str | None = None


@dataclass
class ForwardedFrom(APIModel):
    type_from: enums.ForwardedFromType | str | None = None
    message_id: str | None = None
    from_chat_id: str | None = None
    from_sender_id: str | None = None


@dataclass
class Sticker(APIModel):
    sticker_id: str | None = None
    file: File | None = None
    emoji_character: str | None = None


@dataclass
class ContactMessage(APIModel):
    phone_number: str | None = None
    first_name: str | None = None
    last_name: str | None = None


@dataclass
class PollStatus(APIModel):
    state: enums.PollState | str | None = None
    selection_index: int | None = None
    percent_vote_options: list[int] | None = None
    total_vote: int | None = None
    show_total_votes: bool | None = None


@dataclass
class Poll(APIModel):
    question: str | None = None
    options: list[str] | None = None
    poll_status: PollStatus | None = None


@dataclass
class Chat(APIModel):
    chat_id: str | None = None
    chat_type: enums.ChatType | str | None = None
    user_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None
    username: str | None = None


@dataclass
class BotInfo(APIModel):
    """The bot profile returned by getMe.

    Named BotInfo here because ``rubikabot.Bot`` is the client class.
    """

    bot_id: str | None = None
    bot_title: str | None = None
    avatar: File | None = None
    description: str | None = None
    username: str | None = None
    start_message: str | None = None
    share_url: str | None = None


@dataclass
class BotCommand(APIModel):
    command: str | None = None
    description: str | None = None


@dataclass
class ButtonSelectionItem(APIModel):
    text: str | None = None
    image_url: str | None = None
    type: enums.ButtonSelectionType | str | None = None


@dataclass
class ButtonSelection(APIModel):
    selection_id: str | None = None
    search_type: enums.ButtonSelectionSearch | str | None = None
    get_type: enums.ButtonSelectionGet | str | None = None
    items: list[ButtonSelectionItem] | None = None
    is_multi_selection: bool | None = None
    columns_count: str | None = None
    title: str | None = None


@dataclass
class ButtonCalendar(APIModel):
    default_value: str | None = None
    type: enums.ButtonCalendarType | str | None = None
    min_year: str | None = None
    max_year: str | None = None
    title: str | None = None


@dataclass
class ButtonNumberPicker(APIModel):
    min_value: str | None = None
    max_value: str | None = None
    default_value: str | None = None
    title: str | None = None


@dataclass
class ButtonStringPicker(APIModel):
    items: list[str] | None = None
    default_value: str | None = None
    title: str | None = None


@dataclass
class ButtonTextbox(APIModel):
    type_line: enums.ButtonTextboxTypeLine | str | None = None
    type_keypad: enums.ButtonTextboxTypeKeypad | str | None = None
    place_holder: str | None = None
    title: str | None = None
    default_value: str | None = None


@dataclass
class ButtonLocation(APIModel):
    default_pointer_location: Location | None = None
    default_map_location: Location | None = None
    type: enums.ButtonLocationType | str | None = None
    title: str | None = None


@dataclass
class Button(APIModel):
    id: str | None = None
    type: enums.ButtonType | str | None = None
    button_text: str | None = None
    button_selection: ButtonSelection | None = None
    button_calendar: ButtonCalendar | None = None
    button_number_picker: ButtonNumberPicker | None = None
    button_string_picker: ButtonStringPicker | None = None
    button_location: ButtonLocation | None = None
    button_textbox: ButtonTextbox | None = None


@dataclass
class KeypadRow(APIModel):
    buttons: list[Button] = field(default_factory=list)


@dataclass
class Keypad(APIModel):
    rows: list[KeypadRow] = field(default_factory=list)
    resize_keyboard: bool | None = None
    one_time_keyboard: bool | None = None


@dataclass
class MetadataPart(APIModel):
    type: enums.MetadataType | str | None = None
    from_index: int | None = None
    length: int | None = None
    link_url: str | None = None
    mention_text_user_id: str | None = None


@dataclass
class Metadata(APIModel):
    meta_data_parts: list[MetadataPart] = field(default_factory=list)


@dataclass
class Message(APIModel):
    message_id: str | None = None
    text: str | None = None
    time: int | str | None = None
    is_edited: bool | None = None
    sender_type: enums.MessageSender | str | None = None
    sender_id: str | None = None
    aux_data: AuxData | None = None
    file: File | None = None
    reply_to_message_id: str | None = None
    forwarded_from: ForwardedFrom | None = None
    forwarded_no_link: str | None = None
    location: Location | None = None
    sticker: Sticker | None = None
    contact_message: ContactMessage | None = None
    poll: Poll | None = None
    # Not an API field of Message itself. The dispatcher fills it from the
    # enclosing Update so handlers can answer without tracking chat ids.
    chat_id: str | None = field(default=None, repr=False)

    _bot = None  # bound by the dispatcher or by Bot helpers, not a field

    @property
    def button_id(self) -> str | None:
        """Id of the keypad button that produced this message, if any."""
        return self.aux_data.button_id if self.aux_data else None

    @property
    def start_id(self) -> str | None:
        """Deep link value the user entered the bot with, if any."""
        return self.aux_data.start_id if self.aux_data else None

    def _require_bot(self):
        if self._bot is None or self.chat_id is None:
            raise RuntimeError(
                "this Message is not bound to a Bot and a chat. Handle it "
                "through a Dispatcher or set chat_id and bind a bot with "
                "message.bind(bot, chat_id) first")
        return self._bot

    def bind(self, bot, chat_id: str | None = None):
        self._bot = bot
        if chat_id is not None:
            self.chat_id = chat_id
        return self

    def answer(self, text: str, **kwargs):
        """Send a new message to this message's chat."""
        return self._require_bot().send_message(self.chat_id, text, **kwargs)

    def reply(self, text: str, **kwargs):
        """Send a message that replies to this message."""
        kwargs.setdefault("reply_to_message_id", self.message_id)
        return self.answer(text, **kwargs)

    def edit_text(self, text: str):
        return self._require_bot().edit_message_text(
            self.chat_id, self.message_id, text)

    def delete(self):
        return self._require_bot().delete_message(
            self.chat_id, self.message_id)


@dataclass
class Event(APIModel):
    type: enums.EventType | str | None = None
    access_list: list[enums.ChatAccess | str] | None = None
    join_type: enums.EventJoinType | str | None = None


@dataclass
class Update(APIModel):
    type: enums.UpdateType | str | None = None
    chat_id: str | None = None
    removed_message_id: str | None = None
    new_message: Message | None = None
    updated_message: Message | None = None
    event_data: Event | None = None

    @property
    def message(self) -> Message | None:
        """The new or edited message of this update, bound to its chat."""
        msg = self.new_message or self.updated_message
        if msg is not None and msg.chat_id is None:
            msg.chat_id = self.chat_id
        return msg


@dataclass
class InlineMessage(APIModel):
    sender_id: str | None = None
    text: str | None = None
    file: File | None = None
    location: Location | None = None
    aux_data: AuxData | None = None
    message_id: str | None = None
    chat_id: str | None = None

    _bot = None

    @property
    def button_id(self) -> str | None:
        return self.aux_data.button_id if self.aux_data else None

    @property
    def start_id(self) -> str | None:
        return self.aux_data.start_id if self.aux_data else None

    def bind(self, bot):
        self._bot = bot
        return self

    def answer(self, text: str, **kwargs):
        """Send a new message to the chat this inline tap came from."""
        if self._bot is None:
            raise RuntimeError("this InlineMessage is not bound to a Bot")
        return self._bot.send_message(self.chat_id, text, **kwargs)

    def edit_text(self, text: str):
        if self._bot is None:
            raise RuntimeError("this InlineMessage is not bound to a Bot")
        return self._bot.edit_message_text(
            self.chat_id, self.message_id, text)

    def edit_keypad(self, inline_keypad):
        if self._bot is None:
            raise RuntimeError("this InlineMessage is not bound to a Bot")
        return self._bot.edit_message_keypad(
            self.chat_id, self.message_id, inline_keypad)


@dataclass
class MessageTextUpdate(APIModel):
    """Returned toward the platform from a receiveInlineMessage answer."""

    message_id: str | None = None
    text: str | None = None


@dataclass
class MessageKeypadUpdate(APIModel):
    message_id: str | None = None
    inline_keypad: Keypad | None = None


@dataclass
class UpdatesPage(APIModel):
    """One page of getUpdates results."""

    updates: list[Update] = field(default_factory=list)
    next_offset_id: str | None = None
