"""Fluent builders for chat keypads and inline keypads.

Example:
    builder = KeyboardBuilder()
    builder.button("خرید", id="buy")
    builder.button("راهنما", id="help")
    builder.adjust(2)
    keypad = builder.as_keypad()

Buttons without an explicit id get sequential ids ("1", "2", ...), which
keeps small bots terse. Give stable explicit ids in real flows, because
handlers match on them.
"""

from __future__ import annotations

from . import enums, types


class KeyboardBuilder:
    def __init__(self):
        self._rows: list[list[types.Button]] = []
        self._pending: list[types.Button] = []
        self._next_id = 1

    def button(self, text: str, *, id: str | None = None,
               type: enums.ButtonType | str = enums.ButtonType.SIMPLE,
               **payload) -> "KeyboardBuilder":
        """Add one button to the current row. Payload keys match the
        Button model, for example button_textbox=... or
        button_calendar=... . Start a new row with row()."""
        if id is None:
            id = str(self._next_id)
            self._next_id += 1
        self._pending.append(
            types.Button(id=str(id), type=type, button_text=text,
                         **payload))
        return self

    def row(self, *buttons: types.Button) -> "KeyboardBuilder":
        """Close the current row. Any Button objects passed are appended
        as a complete row of their own."""
        if self._pending:
            self._rows.append(self._pending)
            self._pending = []
        if buttons:
            self._rows.append(list(buttons))
        return self

    def adjust(self, *sizes: int) -> "KeyboardBuilder":
        """Regroup every button added so far into rows of the given
        sizes. The last size repeats, so adjust(2) makes rows of two."""
        if not sizes or any(size <= 0 for size in sizes):
            raise ValueError("adjust sizes must be positive")
        flat = self._flat()
        rows: list[list[types.Button]] = []
        index = 0
        step = 0
        while index < len(flat):
            size = sizes[min(step, len(sizes) - 1)]
            rows.append(flat[index:index + size])
            index += size
            step += 1
        self._rows = rows
        self._pending = []
        return self

    def _flat(self) -> list[types.Button]:
        flat = [btn for row in self._rows for btn in row]
        flat.extend(self._pending)
        return flat

    def as_keypad(self, resize_keyboard: bool = True,
                  one_time_keyboard: bool = False) -> types.Keypad:
        rows = [list(row) for row in self._rows]
        if self._pending:
            rows.append(list(self._pending))
        return types.Keypad(
            rows=[types.KeypadRow(buttons=row) for row in rows],
            resize_keyboard=resize_keyboard,
            one_time_keyboard=one_time_keyboard)

    def as_dict(self, **kwargs) -> dict:
        return self.as_keypad(**kwargs).to_dict()


def keypad_from_rows(rows: list[list[types.Button]],
                     **kwargs) -> types.Keypad:
    """Build a Keypad directly from rows of Button objects."""
    return types.Keypad(
        rows=[types.KeypadRow(buttons=list(row)) for row in rows], **kwargs)
