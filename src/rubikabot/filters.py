"""Filters that decide which handler an event goes to.

A filter is any callable taking a FilterContext and returning a bool.
Filters combine with ``&``, ``|`` and ``~``.

The magic filter ``F`` builds a filter from an attribute path:

    F.text == "سلام"
    F.button_id == "buy"
    F.sender_id.in_(["u1", "u2"])
    F.text.startswith("قیمت")

Attributes resolve against the message (or inline message): text,
button_id, start_id, sender_id, chat_id, message_id and anything else the
model carries.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import enums
from .fsm import State


@dataclass
class FilterContext:
    """Everything a filter may look at."""

    event: object
    state: str | None = None
    data: dict = field(default_factory=dict)


def resolve_attr(event, path: str):
    current = event
    for part in path.split("."):
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)
    return current


class Filter:
    def __call__(self, ctx: FilterContext) -> bool:
        raise NotImplementedError

    def __and__(self, other):
        return _And(self, _ensure(other))

    def __or__(self, other):
        return _Or(self, _ensure(other))

    def __invert__(self):
        return _Not(self)


def _ensure(value) -> Filter:
    if isinstance(value, Filter):
        return value
    if callable(value):
        return _Callable(value)
    raise TypeError(f"not a filter: {value!r}")


class _Callable(Filter):
    def __init__(self, func):
        self.func = func

    def __call__(self, ctx):
        return bool(self.func(ctx))


class _And(Filter):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def __call__(self, ctx):
        return self.left(ctx) and self.right(ctx)


class _Or(Filter):
    def __init__(self, left, right):
        self.left, self.right = left, right

    def __call__(self, ctx):
        return self.left(ctx) or self.right(ctx)


class _Not(Filter):
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, ctx):
        return not self.inner(ctx)


class Command(Filter):
    """Match a command message such as /start or /start with arguments.

    The matched command name and the rest of the text are stored in
    ctx.data as ``command`` and ``command_args`` for the dispatcher to
    pass to the handler.
    """

    def __init__(self, *names: str):
        self.names = {name.lstrip("/").lower() for name in names}

    def __call__(self, ctx):
        text = (resolve_attr(ctx.event, "text") or "").strip()
        if not text.startswith("/"):
            return False
        head, _, rest = text[1:].partition(" ")
        command = head.split("@")[0].lower()
        if command not in self.names:
            return False
        ctx.data["command"] = command
        ctx.data["command_args"] = rest.strip()
        return True


class CommandStart(Command):
    """Shortcut for Command("start")."""

    def __init__(self):
        super().__init__("start")


class Text(Filter):
    """Match message text. Give exactly one matching rule."""

    def __init__(self, *, equals=None, contains=None, startswith=None,
                 endswith=None, ignore_case: bool = True):
        rules = [equals is not None, contains is not None,
                 startswith is not None, endswith is not None]
        if sum(rules) != 1:
            raise ValueError("give exactly one of equals, contains, "
                             "startswith, endswith")
        self.equals = equals
        self.contains = contains
        self.startswith = startswith
        self.endswith = endswith
        self.ignore_case = ignore_case

    def _norm(self, value):
        if value is None:
            return ""
        return value.lower() if self.ignore_case else value

    def __call__(self, ctx):
        text = self._norm(resolve_attr(ctx.event, "text"))
        if self.equals is not None:
            return text == self._norm(self.equals)
        if self.contains is not None:
            return self._norm(self.contains) in text
        if self.startswith is not None:
            return text.startswith(self._norm(self.startswith))
        return text.endswith(self._norm(self.endswith))


class ButtonId(Filter):
    """Match a keypad tap by button id (chat keypad or inline)."""

    def __init__(self, *ids: str):
        self.ids = set(ids)

    def __call__(self, ctx):
        return resolve_attr(ctx.event, "button_id") in self.ids


class ChatType(Filter):
    """Match updates coming from one kind of chat.

    The Message model carries no chat type, so this filter reads the
    ``chat_type`` value the dispatcher places in ctx.data when it can.
    Bots that need it strictly should call bot.get_chat in a middleware.
    """

    def __init__(self, *types):
        self.types = {t.value if isinstance(t, enums.ChatType) else t
                      for t in types}

    def __call__(self, ctx):
        return ctx.data.get("chat_type") in self.types


class StateFilter(Filter):
    """Match the current FSM state.

    StateFilter(None) matches when no state is set. Pass a State, a
    StatesGroup (matches any of its states) or a full state name.
    """

    def __init__(self, *states):
        self.expected: set[str | None] = set()
        for state in states:
            if state is None:
                self.expected.add(None)
            elif isinstance(state, State):
                self.expected.add(state.full_name)
            elif isinstance(state, type):  # a StatesGroup subclass
                for member in state.all_states():
                    self.expected.add(member.full_name)
            else:
                self.expected.add(str(state))

    def __call__(self, ctx):
        return ctx.state in self.expected


class _MagicFilter(Filter):
    def __init__(self, path: str, check):
        self.path = path
        self.check = check

    def __call__(self, ctx):
        return bool(self.check(resolve_attr(ctx.event, self.path)))


class _MagicPath:
    def __init__(self, path: str):
        self.path = path

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return _MagicPath(f"{self.path}.{name}" if self.path else name)

    def __eq__(self, other):
        return _MagicFilter(self.path, lambda value: value == other)

    def __ne__(self, other):
        return _MagicFilter(self.path, lambda value: value != other)

    def in_(self, values):
        values = list(values)
        return _MagicFilter(self.path, lambda value: value in values)

    def startswith(self, prefix):
        return _MagicFilter(
            self.path,
            lambda value: isinstance(value, str)
            and value.startswith(prefix))

    def endswith(self, suffix):
        return _MagicFilter(
            self.path,
            lambda value: isinstance(value, str)
            and value.endswith(suffix))

    def contains(self, needle):
        return _MagicFilter(
            self.path,
            lambda value: value is not None and needle in value)

    def is_(self, other):
        return _MagicFilter(self.path, lambda value: value is other)


class _MagicRoot(_MagicPath):
    def __init__(self):
        super().__init__("")


#: Magic filter root. F.text, F.button_id, F.aux_data.button_id, ...
F = _MagicRoot()
