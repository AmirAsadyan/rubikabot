"""The Bot client: every Rubika Bot API v3 method, typed.

The client talks HTTP through a small transport object. The default
transport uses only the Python standard library, so rubikabot has zero
runtime dependencies. Tests and custom stacks can pass any object with
``post_json``, ``post_multipart`` and ``get_bytes`` methods.
"""

from __future__ import annotations

import json
import mimetypes
import os
import typing
import urllib.error
import urllib.request
import uuid

from . import enums, types
from .errors import APIError, TransportError
from .types import _dump

API_BASE = "https://botapi.rubika.ir/v3"


class UrllibTransport:
    """Default transport built on urllib from the standard library."""

    def post_json(self, url: str, payload: dict, timeout: float):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            url, data=data, method="POST",
            headers={"Content-Type": "application/json"})
        return self._open(request, timeout)

    def post_multipart(self, url: str, field_name: str, filename: str,
                       content: bytes, timeout: float):
        boundary = "rubikabot-" + uuid.uuid4().hex
        content_type = (mimetypes.guess_type(filename)[0]
                        or "application/octet-stream")
        body = b"".join([
            f"--{boundary}\r\n".encode(),
            (f'Content-Disposition: form-data; name="{field_name}"; '
             f'filename="{filename}"\r\n').encode("utf-8"),
            f"Content-Type: {content_type}\r\n\r\n".encode(),
            content,
            f"\r\n--{boundary}--\r\n".encode(),
        ])
        request = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Content-Type":
                     f"multipart/form-data; boundary={boundary}"})
        return self._open(request, timeout)

    def get_bytes(self, url: str, timeout: float) -> bytes:
        request = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as resp:
                return resp.read()
        except (urllib.error.URLError, OSError) as error:
            raise TransportError(f"download failed: {error}") from error

    @staticmethod
    def _open(request, timeout: float):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as resp:
                return resp.status, resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as error:
            raise TransportError(f"request failed: {error}") from error


def _parse_body(method: str, status: int, text: str):
    try:
        body = json.loads(text) if text else {}
    except ValueError:
        raise TransportError(
            f"{method}: response was not JSON: {text[:200]!r}")
    if status >= 400 or (isinstance(body, dict)
                         and body.get("status") == "ERROR"):
        raise APIError(method, body, status_code=status)
    if isinstance(body, dict) and "data" in body:
        return body["data"]
    return body


class Bot:
    """A Rubika bot. Create one with the token from BotFather.

    Example:
        bot = Bot("TOKEN")
        me = bot.get_me()
        bot.send_message(chat_id, "سلام")
    """

    def __init__(self, token: str, transport=None, timeout: float = 30.0,
                 api_base: str = API_BASE):
        if not token:
            raise ValueError("Bot token is empty")
        self.token = token
        self.transport = transport or UrllibTransport()
        self.timeout = timeout
        self.api_base = api_base.rstrip("/")

    def __repr__(self):  # never leak the token
        return f"Bot(api_base={self.api_base!r})"

    def close(self):
        close = getattr(self.transport, "close", None)
        if callable(close):
            close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # -- raw call ------------------------------------------------------
    def api_call(self, method: str, **params):
        """Call any API method and return its ``data`` payload."""
        payload = {key: _dump(value) for key, value in params.items()
                   if value is not None}
        url = f"{self.api_base}/{self.token}/{method}"
        status, text = self.transport.post_json(url, payload, self.timeout)
        return _parse_body(method, status, text)

    # -- bot and chat --------------------------------------------------
    def get_me(self) -> types.BotInfo:
        data = self.api_call("getMe")
        if isinstance(data, dict) and "bot" in data:
            data = data["bot"]
        return types.BotInfo.from_dict(data)

    def get_chat(self, chat_id: str) -> types.Chat:
        data = self.api_call("getChat", chat_id=chat_id)
        if isinstance(data, dict) and "chat" in data:
            data = data["chat"]
        return types.Chat.from_dict(data)

    def set_commands(self, commands) -> typing.Any:
        """commands: BotCommand objects or plain dicts."""
        prepared = [
            cmd.to_dict() if isinstance(cmd, types.APIModel) else cmd
            for cmd in commands]
        return self.api_call("setCommands", bot_commands=prepared)

    # -- receiving -----------------------------------------------------
    def get_updates(self, offset_id: str | None = None,
                    limit: int = 100) -> types.UpdatesPage:
        data = self.api_call("getUpdates", offset_id=offset_id, limit=limit)
        if isinstance(data, dict):
            return types.UpdatesPage.from_dict(data)
        return types.UpdatesPage()

    def update_bot_endpoints(self, url: str,
                             endpoint_type) -> typing.Any:
        return self.api_call("updateBotEndpoints", url=url,
                             type=endpoint_type)

    def register_webhooks(self, base_url: str) -> None:
        """Register the two main endpoints under a public HTTPS base.

        receiveUpdate goes to ``{base_url}/receiveUpdate`` and
        receiveInlineMessage to ``{base_url}/receiveInlineMessage``.
        """
        base = base_url.rstrip("/")
        self.update_bot_endpoints(
            f"{base}/receiveUpdate", enums.UpdateEndpointType.RECEIVE_UPDATE)
        self.update_bot_endpoints(
            f"{base}/receiveInlineMessage",
            enums.UpdateEndpointType.RECEIVE_INLINE_MESSAGE)

    # -- sending ---------------------------------------------------------
    def send_message(self, chat_id: str, text: str, *,
                     chat_keypad=None, inline_keypad=None,
                     chat_keypad_type=None, disable_notification=None,
                     reply_to_message_id=None, metadata=None) -> str | None:
        """Send a message. Returns the new message_id."""
        data = self.api_call(
            "sendMessage", chat_id=chat_id, text=text,
            chat_keypad=chat_keypad, inline_keypad=inline_keypad,
            chat_keypad_type=chat_keypad_type,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id, metadata=metadata)
        return data.get("message_id") if isinstance(data, dict) else None

    def send_poll(self, chat_id: str, question: str,
                  options: list[str]) -> str | None:
        data = self.api_call("sendPoll", chat_id=chat_id, question=question,
                             options=options)
        return data.get("message_id") if isinstance(data, dict) else None

    def send_location(self, chat_id: str, latitude: str, longitude: str,
                      **kwargs) -> str | None:
        data = self.api_call("sendLocation", chat_id=chat_id,
                             latitude=latitude, longitude=longitude,
                             **kwargs)
        return data.get("message_id") if isinstance(data, dict) else None

    def send_contact(self, chat_id: str, first_name: str, last_name: str,
                     phone_number: str, **kwargs) -> str | None:
        data = self.api_call("sendContact", chat_id=chat_id,
                             first_name=first_name, last_name=last_name,
                             phone_number=phone_number, **kwargs)
        return data.get("message_id") if isinstance(data, dict) else None

    def forward_message(self, from_chat_id: str, message_id: str,
                        to_chat_id: str,
                        disable_notification: bool = False) -> str | None:
        data = self.api_call(
            "forwardMessage", from_chat_id=from_chat_id,
            message_id=message_id, to_chat_id=to_chat_id,
            disable_notification=disable_notification)
        return data.get("new_message_id") if isinstance(data, dict) else None

    def edit_message_text(self, chat_id: str, message_id: str, text: str):
        return self.api_call("editMessageText", chat_id=chat_id,
                             message_id=message_id, text=text)

    def edit_message_keypad(self, chat_id: str, message_id: str,
                            inline_keypad):
        return self.api_call("editMessageKeypad", chat_id=chat_id,
                             message_id=message_id,
                             inline_keypad=inline_keypad)

    def delete_message(self, chat_id: str, message_id: str):
        return self.api_call("deleteMessage", chat_id=chat_id,
                             message_id=message_id)

    def edit_chat_keypad(self, chat_id: str, chat_keypad=None):
        """Set a new chat keypad, or remove it when chat_keypad is None."""
        if chat_keypad is None:
            return self.api_call("editChatKeypad", chat_id=chat_id,
                                 chat_keypad_type=enums.ChatKeypadType.REMOVE)
        return self.api_call("editChatKeypad", chat_id=chat_id,
                             chat_keypad_type=enums.ChatKeypadType.NEW,
                             chat_keypad=chat_keypad)

    # -- files -----------------------------------------------------------
    def get_file(self, file_id: str) -> str | None:
        """Return the download URL for a file."""
        data = self.api_call("getFile", file_id=file_id)
        return data.get("download_url") if isinstance(data, dict) else None

    def download_file(self, file_id: str) -> bytes:
        url = self.get_file(file_id)
        if not url:
            raise APIError("getFile", {"file_id": file_id})
        return self.transport.get_bytes(url, self.timeout)

    def request_send_file(self, file_type) -> str | None:
        """First upload step. Returns the upload URL."""
        data = self.api_call("requestSendFile", type=file_type)
        return data.get("upload_url") if isinstance(data, dict) else None

    def upload_file(self, path: str, file_type) -> str:
        """Upload a local file in two steps. Returns its file_id."""
        upload_url = self.request_send_file(file_type)
        if not upload_url:
            raise APIError("requestSendFile", {"type": str(file_type)})
        with open(path, "rb") as handle:
            content = handle.read()
        status, text = self.transport.post_multipart(
            upload_url, "file", os.path.basename(path), content,
            self.timeout)
        data = _parse_body("uploadFile", status, text)
        file_id = data.get("file_id") if isinstance(data, dict) else None
        if not file_id:
            raise APIError("uploadFile", data, status_code=status)
        return file_id

    def send_file(self, chat_id: str, file_id: str, text: str | None = None,
                  **kwargs) -> str | None:
        data = self.api_call("sendFile", chat_id=chat_id, file_id=file_id,
                             text=text, **kwargs)
        return data.get("message_id") if isinstance(data, dict) else None

    def send_uploaded_file(self, chat_id: str, path: str, file_type,
                           text: str | None = None, **kwargs) -> str | None:
        """Upload a local file and send it in one call."""
        file_id = self.upload_file(path, file_type)
        return self.send_file(chat_id, file_id, text=text, **kwargs)

    # -- moderation --------------------------------------------------------
    def ban_chat_member(self, chat_id: str, user_id: str):
        return self.api_call("banChatMember", chat_id=chat_id,
                             user_id=user_id)

    def unban_chat_member(self, chat_id: str, user_id: str):
        return self.api_call("unbanChatMember", chat_id=chat_id,
                             user_id=user_id)
