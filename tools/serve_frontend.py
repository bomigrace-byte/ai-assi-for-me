"""Local frontend preview with a same-origin proxy to the deployed Backend."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


FRONTEND = Path(__file__).resolve().parents[1] / "frontend"
BACKEND = os.getenv("PREVIEW_BACKEND_URL", "https://ai-assi-for-me.onrender.com").rstrip("/")
READ_PATHS = ("/api/data", "/api/export", "/api/conversations")
FORWARDED_HEADERS = ("Content-Type", "X-Session-Token", "X-Admin-Key")
MAX_BODY_BYTES = 64 * 1024


class PreviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if self._matches(path, READ_PATHS):
            self._proxy("GET")
            return
        super().do_GET()

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path in {"/api/chat", "/api/conversations", "/api/data"}:
            self._proxy("POST")
        else:
            self._method_not_allowed()

    def do_PUT(self):
        if self.path.startswith("/api/data/") and self.path != "/api/data/sync/github":
            self._proxy("PUT")
        else:
            self._method_not_allowed()

    def do_DELETE(self):
        if self.path.startswith("/api/conversations/") or self.path.startswith("/api/data/"):
            self._proxy("DELETE")
        else:
            self._method_not_allowed()

    @staticmethod
    def _matches(path, allowed_paths):
        return any(path == allowed or path.startswith(allowed + "/") for allowed in allowed_paths)

    def _proxy(self, method):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._forward(400, "application/json", b'{"detail":"Invalid content length"}')
            return
        if length < 0 or length > MAX_BODY_BYTES:
            self._forward(413, "application/json", b'{"detail":"Request too large"}')
            return
        body = self.rfile.read(length) if length else None
        headers = {name: self.headers[name] for name in FORWARDED_HEADERS if name in self.headers}
        request = Request(BACKEND + self.path, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=60) as response:
                self._forward(response.status, response.headers.get("Content-Type", "application/json"), response.read())
        except HTTPError as error:
            self._forward(error.code, error.headers.get("Content-Type", "application/json"), error.read())
        except (URLError, TimeoutError) as error:
            self._forward(502, "text/plain; charset=utf-8", f"Backend unavailable: {error}".encode())

    def _method_not_allowed(self):
        self._forward(405, "application/json", b'{"detail":"Method not available in local preview"}')

    def _forward(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 3000), partial(PreviewHandler, directory=str(FRONTEND)))
    print("Frontend preview: http://127.0.0.1:3000/ (Backend proxy)", flush=True)
    server.serve_forever()
