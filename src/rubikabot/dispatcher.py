"""Routing and dispatching: Router, Dispatcher, polling and feeding.

Example:
    bot = Bot("TOKEN")
    dp = Dispatcher(bot)
    router = Router()

    @router.message(Command("start"))
    def start(message, state):
        message.answer("سلام!")

    dp.include_router(router)
    dp.start_polling()
"""

from __future__ import annotations

import inspect
import json
import os
import time
import traceback

from . import types
from .filters import FilterContext, _ensure
from .fsm import FSMContext, MemoryStorage, storage_key


class Router:
    """A group of handlers. Split a big bot into one router per feature
    and include them all in the Dispatcher."""

    def __init__(self, name: str | None = None):
        self.name = name or "router"
        self.message_handlers: list = []
        self.edited_message_handlers: list = []
        self.removed_message_handlers: list = []
        self.started_bot_handlers: list = []
        self.stopped_bot_handlers: list = []
        self.event_handlers: list = []
        self.inline_message_handlers: list = []
        self.update_handlers: list = []

    def _register(self, store: list, filters):
        def decorator(func):
            store.append(([_ensure(f) for f in filters], func))
            return func
        return decorator

    def message(self, *filters):
        """NewMessage updates. The handler receives the Message."""
        return self._register(self.message_handlers, filters)

    def edited_message(self, *filters):
        return self._register(self.edited_message_handlers, filters)

    def removed_message(self, *filters):
        """RemovedMessage updates. The handler receives the Update."""
        return self._register(self.removed_message_handlers, filters)

    def started_bot(self, *filters):
        return self._register(self.started_bot_handlers, filters)

    def stopped_bot(self, *filters):
        return self._register(self.stopped_bot_handlers, filters)

    def event(self, *filters):
        """EventData updates (bot joined, removed, permissions changed).
        The handler receives the Update."""
        return self._register(self.event_handlers, filters)

    def inline_message(self, *filters):
        """Inline keypad taps from receiveInlineMessage. The handler
        receives the InlineMessage."""
        return self._register(self.inline_message_handlers, filters)

    def update(self, *filters):
        """Any update kind. The handler receives the Update. Checked
        after the kind specific handlers of the same router."""
        return self._register(self.update_handlers, filters)


class Dispatcher:
    def __init__(self, bot, storage=None):
        self.bot = bot
        self.storage = storage if storage is not None else MemoryStorage()
        self._default_router = Router("default")
        self.routers: list[Router] = [self._default_router]
        self._middlewares: list = []
        self._error_handlers: list = []

    # The dispatcher's own decorators act on its default router.
    def message(self, *filters):
        return self._default_router.message(*filters)

    def edited_message(self, *filters):
        return self._default_router.edited_message(*filters)

    def removed_message(self, *filters):
        return self._default_router.removed_message(*filters)

    def started_bot(self, *filters):
        return self._default_router.started_bot(*filters)

    def stopped_bot(self, *filters):
        return self._default_router.stopped_bot(*filters)

    def event(self, *filters):
        return self._default_router.event(*filters)

    def inline_message(self, *filters):
        return self._default_router.inline_message(*filters)

    def update(self, *filters):
        return self._default_router.update(*filters)

    def include_router(self, *routers: Router):
        for router in routers:
            if router is not self._default_router:
                self.routers.append(router)
        return self

    def middleware(self, func=None):
        """Register a middleware: fn(handler, event, data) -> result.

        Middlewares wrap the matched handler in registration order. A
        middleware that never calls handler(event, data) stops handling.
        """
        if func is None:
            def decorator(inner):
                self._middlewares.append(inner)
                return inner
            return decorator
        self._middlewares.append(func)
        return func

    def errors(self, func=None):
        """Register an error handler: fn(event, exception) -> bool.

        Return True to mark the error handled. Unhandled errors are
        re-raised in feed_update and logged and skipped while polling.
        """
        if func is None:
            def decorator(inner):
                self._error_handlers.append(inner)
                return inner
            return decorator
        self._error_handlers.append(func)
        return func

    # -- internals ------------------------------------------------------
    def _fsm(self, chat_id, user_id) -> FSMContext:
        return FSMContext(self.storage, storage_key(chat_id, user_id))

    def _call_handler(self, func, event, state: FSMContext, data: dict):
        def invoke(evt, d):
            kwargs = {}
            params = inspect.signature(func).parameters
            available = {
                "state": state,
                "bot": self.bot,
                "dp": self,
                "data": d,
                "command": d.get("command"),
                "command_args": d.get("command_args", ""),
            }
            for name in params:
                if name in available:
                    kwargs[name] = available[name]
            return func(evt, **kwargs)

        handler = invoke
        for middleware in reversed(self._middlewares):
            next_handler = handler

            def wrapped(evt, d, mw=middleware, nxt=next_handler):
                return mw(nxt, evt, d)
            handler = wrapped
        return handler(event, data)

    def _run_handlers(self, stores, event, chat_id, user_id) -> bool:
        state = self._fsm(chat_id, user_id)
        for store in stores:
            for filters, func in store:
                ctx = FilterContext(event=event,
                                    state=state.get_state(), data={})
                try:
                    if all(f(ctx) for f in filters):
                        self._call_handler(func, event, state, ctx.data)
                        return True
                except Exception as error:
                    if not self._handle_error(event, error):
                        raise
                    return True
        return False

    def _handle_error(self, event, error) -> bool:
        for handler in self._error_handlers:
            try:
                if handler(event, error):
                    return True
            except Exception:
                traceback.print_exc()
        return False

    # -- feeding ----------------------------------------------------------
    def feed_update(self, raw) -> bool:
        """Feed one update (dict or Update). Returns True when a handler
        ran."""
        update = raw if isinstance(raw, types.Update) \
            else types.Update.from_dict(raw.get("update", raw)
                                        if isinstance(raw, dict) else raw)
        message = update.message
        if message is not None:
            message.bind(self.bot)
            user_id = message.sender_id
        else:
            user_id = None

        kind = str(update.type.value if hasattr(update.type, "value")
                   else update.type)
        stores_by_kind = {
            "NewMessage": lambda r: [r.message_handlers],
            "UpdatedMessage": lambda r: [r.edited_message_handlers],
            "RemovedMessage": lambda r: [r.removed_message_handlers],
            "StartedBot": lambda r: [r.started_bot_handlers],
            "StoppedBot": lambda r: [r.stopped_bot_handlers],
            "EventData": lambda r: [r.event_handlers],
        }
        event = message if kind in ("NewMessage", "UpdatedMessage") \
            and message is not None else update

        picker = stores_by_kind.get(kind)
        stores = []
        for router in self.routers:
            if picker:
                stores.extend(picker(router))
            stores.append(router.update_handlers)
        return self._run_handlers(stores, event, update.chat_id, user_id)

    def feed_inline_message(self, raw) -> bool:
        """Feed one receiveInlineMessage payload (dict or InlineMessage).
        """
        inline = raw if isinstance(raw, types.InlineMessage) else \
            types.InlineMessage.from_dict(
                raw.get("inline_message", raw)
                if isinstance(raw, dict) else raw)
        inline.bind(self.bot)
        stores = [router.inline_message_handlers for router in self.routers]
        return self._run_handlers(stores, inline, inline.chat_id,
                                  inline.sender_id)

    def handle_webhook_payload(self, kind: str, payload: dict) -> bool:
        """Route a webhook body. kind is "update" or "inline"."""
        if kind == "update":
            return self.feed_update(payload)
        if kind == "inline":
            return self.feed_inline_message(payload)
        raise ValueError(f"unknown webhook kind: {kind}")

    # -- polling -----------------------------------------------------------
    def start_polling(self, *, interval: float = 1.0, limit: int = 100,
                      offset_file: str | None = None,
                      skip_errors: bool = True):
        """Run getUpdates in a loop and feed every update.

        The next_offset_id cursor is kept in memory and, when offset_file
        is given, persisted there so restarts do not replay updates.
        Blocks until KeyboardInterrupt.
        """
        offset_id = None
        if offset_file and os.path.exists(offset_file):
            with open(offset_file, encoding="utf-8") as handle:
                offset_id = json.load(handle).get("next_offset_id")
        try:
            while True:
                try:
                    page = self.bot.get_updates(offset_id=offset_id,
                                                limit=limit)
                except Exception as error:
                    if not skip_errors:
                        raise
                    print("getUpdates failed:", error)
                    time.sleep(max(interval, 3.0))
                    continue
                for update in page.updates:
                    try:
                        self.feed_update(update)
                    except Exception:
                        traceback.print_exc()
                if page.next_offset_id:
                    offset_id = page.next_offset_id
                    if offset_file:
                        tmp = offset_file + ".tmp"
                        with open(tmp, "w", encoding="utf-8") as handle:
                            json.dump({"next_offset_id": offset_id},
                                      handle)
                        os.replace(tmp, offset_file)
                time.sleep(interval)
        except KeyboardInterrupt:
            pass
