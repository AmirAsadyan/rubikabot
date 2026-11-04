import unittest

from rubikabot import types
from rubikabot.enums import ButtonType, ChatType, UpdateType

UPDATE_PAYLOAD = {
    "type": "NewMessage",
    "chat_id": "b0QFtabc",
    "new_message": {
        "message_id": "204215",
        "text": "سلام",
        "time": "1643122902",
        "is_edited": False,
        "sender_type": "User",
        "sender_id": "u0QFtn",
        "aux_data": {"start_id": "ref-1", "button_id": None},
        "file": None,
    },
}

INLINE_PAYLOAD = {
    "sender_id": "u0QFtn",
    "text": "custom text",
    "location": None,
    "aux_data": {"start_id": None, "button_id": "61f6"},
    "message_id": "204216",
    "chat_id": "b0QFtabc",
}


class TestUpdateParsing(unittest.TestCase):
    def test_update_roundtrip(self):
        update = types.Update.from_dict(UPDATE_PAYLOAD)
        self.assertEqual(update.type, UpdateType.NEW_MESSAGE)
        self.assertEqual(update.chat_id, "b0QFtabc")
        message = update.message
        self.assertIsNotNone(message)
        self.assertEqual(message.text, "سلام")
        self.assertEqual(message.sender_id, "u0QFtn")
        self.assertEqual(message.start_id, "ref-1")
        self.assertIsNone(message.button_id)
        self.assertEqual(message.chat_id, "b0QFtabc")
        dumped = update.to_dict()
        self.assertEqual(dumped["type"], "NewMessage")
        self.assertEqual(dumped["new_message"]["text"], "سلام")

    def test_unknown_fields_and_enum_values_are_tolerated(self):
        payload = dict(UPDATE_PAYLOAD, future_field={"x": 1})
        payload["new_message"] = dict(UPDATE_PAYLOAD["new_message"],
                                      sender_type="SomethingNew")
        update = types.Update.from_dict(payload)
        self.assertEqual(update.new_message.sender_type, "SomethingNew")

    def test_inline_message(self):
        inline = types.InlineMessage.from_dict(INLINE_PAYLOAD)
        self.assertEqual(inline.button_id, "61f6")
        self.assertEqual(inline.chat_id, "b0QFtabc")


class TestModels(unittest.TestCase):
    def test_chat(self):
        chat = types.Chat.from_dict({
            "chat_id": "c1", "chat_type": "Group", "title": "گروه من"})
        self.assertEqual(chat.chat_type, ChatType.GROUP)
        self.assertEqual(chat.title, "گروه من")

    def test_keypad_to_dict_shape(self):
        keypad = types.Keypad(rows=[types.KeypadRow(buttons=[
            types.Button(id="1", type=ButtonType.SIMPLE,
                         button_text="یک")])], resize_keyboard=True)
        data = keypad.to_dict()
        self.assertEqual(data["rows"][0]["buttons"][0]["type"], "Simple")
        self.assertEqual(data["rows"][0]["buttons"][0]["button_text"],
                         "یک")

    def test_nested_poll_and_file(self):
        message = types.Message.from_dict({
            "message_id": "1",
            "poll": {"question": "سؤال؟", "options": ["الف", "ب"],
                     "poll_status": {"state": "Open", "total_vote": 3,
                                     "selection_index": -1,
                                     "percent_vote_options": [50, 50],
                                     "show_total_votes": True}},
            "file": {"file_id": "f1", "file_name": "a.jpg",
                     "size": "123"}})
        self.assertEqual(message.poll.options, ["الف", "ب"])
        self.assertEqual(message.poll.poll_status.total_vote, 3)
        self.assertEqual(message.file.file_name, "a.jpg")


if __name__ == "__main__":
    unittest.main()
