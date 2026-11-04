import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fake_transport import FakeTransport

from rubikabot import Bot, types
from rubikabot.enums import FileType
from rubikabot.errors import APIError, TransportError


class ErrorTransport:
    def post_json(self, url, payload, timeout):
        return 200, json.dumps({"status": "ERROR",
                                "data": {"error": "bad token"}})

    def post_multipart(self, url, field_name, filename, content, timeout):
        return 500, "server error"

    def get_bytes(self, url, timeout):
        raise TransportError("no network")


class TestBotClient(unittest.TestCase):
    def setUp(self):
        self.transport = FakeTransport()
        self.bot = Bot("TEST-TOKEN", transport=self.transport)

    def test_token_never_in_repr(self):
        self.assertNotIn("TEST-TOKEN", repr(self.bot))

    def test_get_me(self):
        me = self.bot.get_me()
        self.assertIsInstance(me, types.BotInfo)
        self.assertEqual(me.username, "testbot")
        method, payload = self.transport.calls[-1]
        self.assertEqual(method, "getMe")

    def test_get_chat_unwraps(self):
        chat = self.bot.get_chat("c1")
        self.assertEqual(chat.first_name, "Amir")
        self.assertEqual(str(chat.chat_type), "User")

    def test_send_message_payload_and_return(self):
        message_id = self.bot.send_message("c1", "سلام",
                                           disable_notification=True)
        self.assertEqual(message_id, "m-100")
        payload = self.transport.calls_for("sendMessage")[-1]
        self.assertEqual(payload, {"chat_id": "c1", "text": "سلام",
                                   "disable_notification": True})

    def test_none_params_are_not_sent(self):
        self.bot.send_message("c1", "hi")
        payload = self.transport.calls_for("sendMessage")[-1]
        self.assertNotIn("inline_keypad", payload)
        self.assertNotIn("reply_to_message_id", payload)

    def test_keypad_object_is_serialized(self):
        keypad = types.Keypad(rows=[types.KeypadRow(buttons=[
            types.Button(id="1", type="Simple", button_text="یک")])])
        self.bot.send_message("c1", "hi", inline_keypad=keypad)
        payload = self.transport.calls_for("sendMessage")[-1]
        self.assertEqual(
            payload["inline_keypad"]["rows"][0]["buttons"][0]["id"], "1")

    def test_get_updates_page(self):
        page = self.bot.get_updates(limit=5)
        self.assertEqual(page.updates, [])
        self.assertEqual(page.next_offset_id, "off-1")
        payload = self.transport.calls_for("getUpdates")[-1]
        self.assertEqual(payload["limit"], 5)

    def test_forward_message_returns_new_id(self):
        self.assertEqual(
            self.bot.forward_message("a", "1", "b"), "m-200")

    def test_set_commands_with_objects(self):
        self.bot.set_commands(
            [types.BotCommand(command="start", description="شروع")])
        payload = self.transport.calls_for("setCommands")[-1]
        self.assertEqual(payload["bot_commands"][0]["command"], "start")

    def test_register_webhooks_registers_two_endpoints(self):
        self.bot.register_webhooks("https://bot.example.com/")
        calls = self.transport.calls_for("updateBotEndpoints")
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]["url"],
                         "https://bot.example.com/receiveUpdate")
        self.assertEqual(calls[0]["type"], "ReceiveUpdate")
        self.assertEqual(calls[1]["type"], "ReceiveInlineMessage")

    def test_upload_and_send_file_flow(self):
        with tempfile.NamedTemporaryFile("wb", suffix=".jpg",
                                         delete=False) as handle:
            handle.write(b"\xff\xd8jpeg")
            path = handle.name
        try:
            file_id = self.bot.upload_file(path, FileType.IMAGE)
            self.assertEqual(file_id, "file-9")
            upload_call = self.transport.multipart_calls[-1]
            self.assertEqual(upload_call[0], "https://upload.example/put")
            self.assertEqual(upload_call[1], "file")
            message_id = self.bot.send_file("c1", file_id, text="عکس")
            self.assertEqual(message_id, "m-104")
        finally:
            os.unlink(path)

    def test_download_file(self):
        self.assertEqual(self.bot.download_file("f1"), b"file-bytes")
        self.assertEqual(self.transport.downloads,
                         ["https://files.example/f1"])

    def test_edit_chat_keypad_remove(self):
        self.bot.edit_chat_keypad("c1")
        payload = self.transport.calls_for("editChatKeypad")[-1]
        self.assertEqual(payload["chat_keypad_type"], "Remove")

    def test_error_status_raises_api_error(self):
        bot = Bot("BAD", transport=ErrorTransport())
        with self.assertRaises(APIError):
            bot.get_me()


if __name__ == "__main__":
    unittest.main()
