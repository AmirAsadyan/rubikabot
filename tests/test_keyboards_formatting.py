import unittest

from rubikabot import KeyboardBuilder, FormattedText, make_part, utf16_len
from rubikabot.enums import ButtonType
from rubikabot.errors import ValidationError
from rubikabot.types import Button


class TestKeyboardBuilder(unittest.TestCase):
    def test_auto_ids_and_single_row(self):
        keypad = (KeyboardBuilder()
                  .button("یک").button("دو")
                  .as_keypad())
        buttons = keypad.rows[0].buttons
        self.assertEqual([b.id for b in buttons], ["1", "2"])
        self.assertTrue(keypad.resize_keyboard)

    def test_adjust_rows(self):
        builder = KeyboardBuilder()
        for label in ["a", "b", "c", "d", "e"]:
            builder.button(label)
        keypad = builder.adjust(2).as_keypad()
        self.assertEqual([len(r.buttons) for r in keypad.rows], [2, 2, 1])

    def test_explicit_rows_and_ids(self):
        keypad = (KeyboardBuilder()
                  .button("خرید", id="buy")
                  .row()
                  .button("راهنما", id="help")
                  .as_keypad())
        self.assertEqual(len(keypad.rows), 2)
        self.assertEqual(keypad.rows[0].buttons[0].id, "buy")

    def test_row_with_button_objects(self):
        keypad = (KeyboardBuilder()
                  .row(Button(id="x", type=ButtonType.SIMPLE,
                              button_text="X"))
                  .as_keypad())
        self.assertEqual(keypad.rows[0].buttons[0].id, "x")

    def test_special_button_payload(self):
        keypad = (KeyboardBuilder()
                  .button("شماره‌ام", type=ButtonType.ASK_MY_PHONE_NUMBER)
                  .as_keypad())
        self.assertEqual(str(keypad.rows[0].buttons[0].type),
                         "AskMyPhoneNumber")

    def test_adjust_rejects_zero(self):
        with self.assertRaises(ValueError):
            KeyboardBuilder().button("a").adjust(0)


class TestFormatting(unittest.TestCase):
    def test_utf16_len(self):
        self.assertEqual(utf16_len("سلام"), 4)
        self.assertEqual(utf16_len("a😀b"), 4)
        self.assertEqual(utf16_len(""), 0)

    def test_formatted_text_parts_use_utf16(self):
        msg = FormattedText().add("😀 ").bold("سلام")
        text, metadata = msg.build()
        self.assertEqual(text, "😀 سلام")
        part = metadata.meta_data_parts[0]
        self.assertEqual(str(part.type), "Bold")
        # emoji (2 units) + space (1) = bold starts at unit 3
        self.assertEqual(part.from_index, 3)
        self.assertEqual(part.length, 4)

    def test_link_part(self):
        msg = FormattedText().add("ببین: ").link("سایت", "https://x.ir")
        part = msg.metadata.meta_data_parts[0]
        self.assertEqual(part.link_url, "https://x.ir")

    def test_make_part_validation(self):
        with self.assertRaises(ValidationError):
            make_part("سلام", "Bold", 0, 99)
        with self.assertRaises(ValidationError):
            make_part("سلام", "Link", 0, 2)
        part = make_part("سلام دنیا", "Italic", 5, 4)
        self.assertEqual(part.from_index, 5)

    def test_part_limit(self):
        msg = FormattedText()
        for _ in range(30):
            msg.bold("x")
        with self.assertRaises(ValidationError):
            msg.bold("y")


if __name__ == "__main__":
    unittest.main()
