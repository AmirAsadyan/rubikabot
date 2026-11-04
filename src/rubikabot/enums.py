"""Enumerations of the Rubika Bot API v3.

Values match the official documentation at https://rubika.ir/botapi/models
exactly, so members serialize to the strings the API expects.
"""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """Enum whose members are plain strings when serialized."""

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value


class ChatType(StrEnum):
    USER = "User"
    BOT = "Bot"
    GROUP = "Group"
    CHANNEL = "Channel"


class MessageSender(StrEnum):
    USER = "User"
    BOT = "Bot"


class UpdateType(StrEnum):
    NEW_MESSAGE = "NewMessage"
    UPDATED_MESSAGE = "UpdatedMessage"
    REMOVED_MESSAGE = "RemovedMessage"
    STARTED_BOT = "StartedBot"
    STOPPED_BOT = "StoppedBot"
    EVENT_DATA = "EventData"


class EventType(StrEnum):
    BOT_JOINED = "BotJoined"
    BOT_REMOVED = "BotRemoved"
    BOT_PERMISSIONS_CHANGED = "BotPermissionsChanged"


class EventJoinType(StrEnum):
    MEMBER = "Member"
    ADMIN = "Admin"


class ChatAccess(StrEnum):
    SEND_MESSAGES = "SendMessages"
    EDIT_MY_MESSAGES = "EditMyMessages"
    EDIT_ALL_MESSAGES = "EditAllMessages"
    DELETE_GLOBAL_ALL_MESSAGES = "DeleteGlobalAllMessages"
    VIEW_MEMBERS = "ViewMembers"
    BAN_MEMBER = "BanMember"


class ForwardedFromType(StrEnum):
    USER = "User"
    CHANNEL = "Channel"
    BOT = "Bot"


class ButtonType(StrEnum):
    SIMPLE = "Simple"
    SELECTION = "Selection"
    CALENDAR = "Calendar"
    NUMBER_PICKER = "NumberPicker"
    STRING_PICKER = "StringPicker"
    LOCATION = "Location"
    CAMERA_IMAGE = "CameraImage"
    CAMERA_VIDEO = "CameraVideo"
    GALLERY_IMAGE = "GalleryImage"
    GALLERY_VIDEO = "GalleryVideo"
    FILE = "File"
    AUDIO = "Audio"
    RECORD_AUDIO = "RecordAudio"
    TEXTBOX = "Textbox"
    LINK = "Link"
    ASK_MY_PHONE_NUMBER = "AskMyPhoneNumber"
    ASK_MY_LOCATION = "AskMyLocation"
    BARCODE = "Barcode"


class ButtonSelectionType(StrEnum):
    TEXT_ONLY = "TextOnly"
    TEXT_IMG_THUMBNAIL = "TextImgThu"
    TEXT_IMG_BIG = "TextImgBig"


class ButtonSelectionSearch(StrEnum):
    NONE = "None"
    LOCAL = "Local"
    API = "Api"


class ButtonSelectionGet(StrEnum):
    LOCAL = "Local"
    API = "Api"


class ButtonCalendarType(StrEnum):
    DATE_PERSIAN = "DatePersian"
    DATE_GREGORIAN = "DateGregorian"


class ButtonTextboxTypeLine(StrEnum):
    SINGLE_LINE = "SingleLine"
    MULTI_LINE = "MultiLine"


class ButtonTextboxTypeKeypad(StrEnum):
    STRING = "String"
    NUMBER = "Number"


class ButtonLocationType(StrEnum):
    PICKER = "Picker"
    VIEW = "View"


class ChatKeypadType(StrEnum):
    NONE = "None"
    NEW = "New"
    REMOVE = "Remove"


class FileType(StrEnum):
    """Upload kinds for requestSendFile, with the documented limits.

    FILE and VIDEO allow up to 50 MB, IMAGE up to 10 MB in jpg, gif, png
    or webp, VOICE and MUSIC are mp3, and GIF is a silent mp4.
    """

    FILE = "File"
    IMAGE = "Image"
    VOICE = "Voice"
    VIDEO = "Video"
    MUSIC = "Music"
    GIF = "Gif"


class MetadataType(StrEnum):
    BOLD = "Bold"
    ITALIC = "Italic"
    MONO = "Mono"
    UNDERLINE = "Underline"
    STRIKE = "Strike"
    SPOILER = "Spoiler"
    LINK = "Link"
    MENTION_TEXT = "MentionText"
    PRE = "Pre"
    QUOTE = "Quote"


class PollState(StrEnum):
    OPEN = "Open"
    CLOSED = "Closed"


class UpdateEndpointType(StrEnum):
    RECEIVE_UPDATE = "ReceiveUpdate"
    RECEIVE_INLINE_MESSAGE = "ReceiveInlineMessage"
    RECEIVE_QUERY = "ReceiveQuery"
    GET_SELECTION_ITEM = "GetSelectionItem"
    SEARCH_SELECTION_ITEMS = "SearchSelectionItems"
