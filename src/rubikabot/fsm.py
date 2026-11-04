"""Finite state machine support: states, storage and context.

Rubika gives bots no session layer, so rubikabot keeps one state and one
data dict per (chat, user) pair, in memory by default or in a JSON file
with FileStorage.

Example:
    class Form(StatesGroup):
        name = State()
        age = State()

    @router.message(Command("register"))
    def start(message, state):
        state.set_state(Form.name)
        message.answer("اسمت چیست؟")
"""

from __future__ import annotations

import json
import os
import threading


class State:
    def __init__(self):
        self._group_name: str | None = None
        self._name: str | None = None

    def _bind(self, group_name: str, name: str):
        self._group_name = group_name
        self._name = name

    @property
    def full_name(self) -> str:
        if self._group_name is None:
            raise RuntimeError("this State is not part of a StatesGroup")
        return f"{self._group_name}:{self._name}"

    def __repr__(self):
        try:
            return f"State({self.full_name})"
        except RuntimeError:
            return "State(<unbound>)"

    def __eq__(self, other):
        if isinstance(other, State):
            return self.full_name == other.full_name
        if isinstance(other, str):
            return self.full_name == other
        return NotImplemented

    def __hash__(self):
        return hash(self.full_name)


class StatesGroup:
    """Base class that binds the State attributes of a subclass."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name, value in list(vars(cls).items()):
            if isinstance(value, State):
                value._bind(cls.__name__, name)

    @classmethod
    def all_states(cls) -> list[State]:
        return [value for value in vars(cls).values()
                if isinstance(value, State)]


class MemoryStorage:
    """In process storage. Data is lost when the process stops."""

    def __init__(self):
        self._states: dict[str, str | None] = {}
        self._data: dict[str, dict] = {}
        self._lock = threading.Lock()

    def get_state(self, key: str) -> str | None:
        with self._lock:
            return self._states.get(key)

    def set_state(self, key: str, state: str | None):
        with self._lock:
            self._states[key] = state

    def get_data(self, key: str) -> dict:
        with self._lock:
            return dict(self._data.get(key, {}))

    def set_data(self, key: str, data: dict):
        with self._lock:
            self._data[key] = dict(data)

    def clear(self, key: str):
        with self._lock:
            self._states.pop(key, None)
            self._data.pop(key, None)


class FileStorage(MemoryStorage):
    """MemoryStorage that persists states and data to a JSON file."""

    def __init__(self, path: str):
        super().__init__()
        self.path = path
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle:
                saved = json.load(handle)
            self._states = saved.get("states", {})
            self._data = saved.get("data", {})

    def _save(self):
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump({"states": self._states, "data": self._data},
                      handle, ensure_ascii=False)
        os.replace(tmp, self.path)

    def set_state(self, key: str, state: str | None):
        super().set_state(key, state)
        self._save()

    def set_data(self, key: str, data: dict):
        super().set_data(key, data)
        self._save()

    def clear(self, key: str):
        super().clear(key)
        self._save()


def storage_key(chat_id, user_id) -> str:
    return f"{chat_id}:{user_id}"


class FSMContext:
    """Per (chat, user) state and data, passed to handlers as ``state``."""

    def __init__(self, storage, key: str):
        self._storage = storage
        self.key = key

    def get_state(self) -> str | None:
        return self._storage.get_state(self.key)

    def set_state(self, state: State | str | None):
        if isinstance(state, State):
            state = state.full_name
        self._storage.set_state(self.key, state)

    def get_data(self) -> dict:
        return self._storage.get_data(self.key)

    def update_data(self, **kwargs) -> dict:
        data = self._storage.get_data(self.key)
        data.update(kwargs)
        self._storage.set_data(self.key, data)
        return data

    def set_data(self, data: dict):
        self._storage.set_data(self.key, data)

    def clear(self):
        """Drop both the state and the stored data."""
        self._storage.clear(self.key)

    def finish(self):
        """Alias of clear(), familiar from other bot frameworks."""
        self.clear()
