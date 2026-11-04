"""A fake transport for tests: records calls, replays canned answers.

Response bodies mirror the API envelope: {"status": "OK", "data": ...}.
"""

import json


class FakeResponse:
    def __init__(self, data, status="OK"):
        self.body = {"status": status, "data": data}
        self.status_code = 200

    def as_pair(self):
        return self.status_code, json.dumps(self.body)


class FakeTransport:
    def __init__(self):
        self.calls = []          # (method_name, payload) for post_json
        self.multipart_calls = []
        self.downloads = []
        self.responses = {
            "getMe": {"bot": {"bot_id": "42", "username": "testbot",
                              "bot_title": "Test Bot"}},
            "getChat": {"chat": {"chat_id": "c1", "chat_type": "User",
                                 "first_name": "Amir"}},
            "sendMessage": {"message_id": "m-100"},
            "sendPoll": {"message_id": "m-101"},
            "sendLocation": {"message_id": "m-102"},
            "sendContact": {"message_id": "m-103"},
            "forwardMessage": {"new_message_id": "m-200"},
            "sendFile": {"message_id": "m-104"},
            "getUpdates": {"updates": [], "next_offset_id": "off-1"},
            "getFile": {"download_url": "https://files.example/f1"},
            "requestSendFile": {"upload_url": "https://upload.example/put"},
        }
        self.upload_response = {"data": {"file_id": "file-9"}}
        self.file_bytes = b"file-bytes"

    def post_json(self, url, payload, timeout):
        method = url.rsplit("/", 1)[-1]
        self.calls.append((method, payload))
        data = self.responses.get(method, {})
        return 200, json.dumps({"status": "OK", "data": data})

    def post_multipart(self, url, field_name, filename, content, timeout):
        self.multipart_calls.append((url, field_name, filename, content))
        return 200, json.dumps(self.upload_response)

    def get_bytes(self, url, timeout):
        self.downloads.append(url)
        return self.file_bytes

    def calls_for(self, method):
        return [payload for name, payload in self.calls if name == method]
