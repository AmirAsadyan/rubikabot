"""A small webhook server on the Python standard library.

    bot = Bot("TOKEN")
    dp = Dispatcher(bot)
    ...
    bot.register_webhooks("https://your.public.domain")
    serve(dp, port=8080)

The server answers POST /receiveUpdate and POST /receiveInlineMessage,
always replies 200 with an empty JSON object (the platform may pause
delivery to endpoints that error), and logs handler exceptions instead of
failing the request. Put it behind an HTTPS reverse proxy in production:
Rubika connects only to secure public addresses.

For a web framework you already run, skip serve() and call
``dp.handle_webhook_payload("update", body)`` or
``dp.handle_webhook_payload("inline", body)`` from your own view.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


def make_handler(dispatcher):
    class RubikaWebhookHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                body = {}
            try:
                if self.path.startswith("/receiveInlineMessage"):
                    dispatcher.handle_webhook_payload("inline", body)
                elif self.path.startswith("/receiveUpdate"):
                    dispatcher.handle_webhook_payload("update", body)
            except Exception as error:  # still answer 200
                print("webhook handler failed:", error)
            payload = b"{}"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            payload = b"ok"
            self.send_response(200)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    return RubikaWebhookHandler


def serve(dispatcher, host: str = "127.0.0.1", port: int = 8080):
    """Serve the dispatcher webhooks. Blocks until KeyboardInterrupt."""
    server = HTTPServer((host, port), make_handler(dispatcher))
    print(f"rubikabot webhook listening on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
