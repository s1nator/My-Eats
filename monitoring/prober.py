"""Independent HTTP/JSON availability probe; Python standard library only."""
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen

TARGET = os.getenv("PROBE_URL", "http://backend:8000/api/v1/menu")
INTERVAL = float(os.getenv("PROBE_INTERVAL", "5"))
TIMEOUT = float(os.getenv("PROBE_TIMEOUT", "2"))
state = None
lock = threading.Lock()


def probe():
    global state
    while True:
        started = time.monotonic()
        try:
            with urlopen(TARGET, timeout=TIMEOUT) as response:
                ok = response.status == 200 and isinstance(json.load(response), list)
        except Exception:
            ok = False
        with lock:
            state = int(ok)
        time.sleep(max(0, INTERVAL - (time.monotonic() - started)))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/metrics":
            self.send_error(404)
            return
        with lock:
            value = state
        if value is None:
            self.send_error(503, "First probe has not finished")
            return
        body = ("# HELP my_eats_probe_success HTTP 200 and valid menu JSON\n"
                "# TYPE my_eats_probe_success gauge\n"
                f"my_eats_probe_success {value}\n").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    threading.Thread(target=probe, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", 8001), Handler).serve_forever()
