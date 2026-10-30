"""Generate real API requests: python3 monitoring/demo.py normal|error|delay [seconds]."""
import concurrent.futures
import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

mode = sys.argv[1] if len(sys.argv) > 1 else "normal"
if mode not in {"normal", "error", "delay"}:
    raise SystemExit("Expected normal|error|delay")
duration = float(sys.argv[2]) if len(sys.argv) > 2 else 45
base = "http://localhost:8000/api/v1"
try:
    with urlopen("http://localhost:8000/health", timeout=3) as response:
        if json.load(response).get("mode") != "slo-demo":
            raise SystemExit("Refusing to write demo data: backend is not in SLO demo mode")
except (HTTPError, URLError, TimeoutError, ConnectionError) as error:
    raise SystemExit(f"Demo backend unavailable: {error}")


def request(path, data=None, fault=None):
    headers = {"Content-Type": "application/json"}
    if fault:
        headers["X-Demo-Fault"] = fault
    req = Request(base + path, data=json.dumps(data).encode() if data is not None else None,
                  headers=headers)
    try:
        with urlopen(req, timeout=3) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError, ConnectionError):
        return None


item = request("/menu", {"title": "SLO demo", "price": "100.00", "category": "demo"})
if not item:
    raise SystemExit("Backend/DB unavailable: cannot create demo menu item")
order = {"customer_name": "SLO demo", "customer_phone": "demo",
         "delivery_address": "demo", "items": [{"menu_item_id": item["id"], "quantity": 1}]}


def worker():
    until = time.monotonic() + duration
    while time.monotonic() < until:
        request("/menu", fault=mode if mode != "normal" else None)
        payload = dict(order)
        # Business failure is a genuine 404 counted by the existing order metric.
        if mode == "error":
            payload["items"] = [{"menu_item_id": 2147483647, "quantity": 1}]
        request("/orders", payload, fault="delay" if mode == "delay" else None)
        time.sleep(0.2)


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(lambda _: worker(), range(4)))
print(f"Completed {mode}: {duration:g}s, 4 workers")
