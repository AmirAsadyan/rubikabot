"""Helpers for Rubika message formatting (the metadata model).

The API counts ``from_index`` and ``length`` in UTF-16 code units and
rejects the whole message when even one metadata part is invalid, so the
builder here tracks plain text and parts together and validates ranges
before anything is sent.
"""

from __future__ import annotations

from . import enums, types
from .errors import ValidationError

MAX_PARTS = 30


def utf16_len(text: str) -> int:
    """Length of text in UTF-16 code units. Most emoji count as 2."""
    return len(text.encode("utf-16-le")) // 2


def make_part(text: str, part_type, start: int, length: int, *,
              link_url: str | None = None,
              mention_text_user_id: str | None = None) -> types.MetadataPart:
    """Build one validated MetadataPart.

    ``start`` and ``length`` are ordinary Python character indexes into
    ``text``. They are converted to UTF-16 units for the API.
    """
    part_type = enums.MetadataType(part_type)
    if start < 0 or length <= 0 or start + length > len(text):
        raise ValidationError(
            f"metadata range start={start} length={length} is outside "
            f"the text of {len(text)} characters")
    if part_type is enums.MetadataType.LINK and not link_url:
        raise ValidationError("a Link part needs link_url")
    if part_type is enums.MetadataType.MENTION_TEXT \
            and not mention_text_user_id:
        raise ValidationError("a MentionText part needs "
                              "mention_text_user_id")
    return types.MetadataPart(
        type=part_type,
        from_index=utf16_len(text[:start]),
        length=utf16_len(text[start:start + length]),
        link_url=link_url,
        mention_text_user_id=mention_text_user_id)


class FormattedText:
    """Build a formatted message piece by piece.

    Example:
        msg = (FormattedText()
               .add("سلام ")
               .bold("دنیا")
               .add("، به بات خوش آمدی"))
        bot.send_message(chat_id, msg.text, metadata=msg.metadata)
    """

    def __init__(self):
        self._text = ""
        self._parts: list[types.MetadataPart] = []

    def add(self, text: str) -> "FormattedText":
        self._text += text
        return self

    def _styled(self, text: str, part_type, **extra) -> "FormattedText":
        start = len(self._text)
        self._text += text
        if len(self._parts) >= MAX_PARTS:
            raise ValidationError(
                f"metadata is limited to {MAX_PARTS} parts")
        self._parts.append(
            make_part(self._text, part_type, start, len(text), **extra))
        return self

    def bold(self, text: str) -> "FormattedText":
        return self._styled(text, enums.MetadataType.BOLD)

    def italic(self, text: str) -> "FormattedText":
        return self._styled(text, enums.MetadataType.ITALIC)

    def mono(self, text: str) -> "FormattedText":
        return self._styled(text, enums.MetadataType.MONO)

    def underline(self, text: str) -> "FormattedText":
        return self._styled(text, enums.MetadataType.UNDERLINE)

    def strike(self, text: str) -> "FormattedText":
        return self._styled(text, enums.MetadataType.STRIKE)

    def spoiler(self, text: str) -> "FormattedText":
        return self._styled(text, enums.MetadataType.SPOILER)

    def pre(self, text: str) -> "FormattedText":
        return self._styled(text, enums.MetadataType.PRE)

    def quote(self, text: str) -> "FormattedText":
        return self._styled(text, enums.MetadataType.QUOTE)

    def link(self, text: str, url: str) -> "FormattedText":
        return self._styled(text, enums.MetadataType.LINK, link_url=url)

    def mention(self, text: str, user_id: str) -> "FormattedText":
        """Mention a user. Only works in group chats, per the API docs."""
        return self._styled(text, enums.MetadataType.MENTION_TEXT,
                            mention_text_user_id=user_id)

    @property
    def text(self) -> str:
        return self._text

    @property
    def metadata(self) -> types.Metadata:
        return types.Metadata(meta_data_parts=list(self._parts))

    def build(self) -> tuple[str, types.Metadata]:
        return self._text, self.metadata
