#!/usr/bin/env python3
from __future__ import annotations

import signal
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection
from urllib.parse import urlparse

URL: str = "http://127.0.0.1:30080"
HOST: str = urlparse(URL).hostname or "127.0.0.1"
PORT: int = urlparse(URL).port or 80
PATH: str = "/"
CONCURRENCY: int = 3
DURATION_SECONDS: float = 60
TIMEOUT_SECONDS: float = 5
REQUEST_DELAY_SECONDS: float = 0.05

def worker(stop: threading.Event, lock: threading.Lock, stats: Counter[str]) -> None:
    while not stop.is_set():
        conn = HTTPConnection(HOST, PORT, timeout=TIMEOUT_SECONDS)
        try:
            print(f"[send] GET {PATH}", flush=True)
            conn.request("GET", PATH, headers={"Connection": "close"})
            res = conn.getresponse()
            res.read()
            print(f"[ok] {res.status}", flush=True)
            with lock:
                stats["ok"] += 1
        except Exception as e:
            print(f"[err] {type(e).__name__}", flush=True)
            with lock:
                stats[type(e).__name__] += 1
            time.sleep(0.05)
        finally:
            conn.close()
        time.sleep(REQUEST_DELAY_SECONDS)

def main() -> None:
    stop: threading.Event = threading.Event()
    lock: threading.Lock = threading.Lock()
    stats: Counter[str] = Counter()

    def stop_now(*_: object) -> None:
        print("\n[stop] stopping...", flush=True)
        stop.set()

    signal.signal(signal.SIGINT, stop_now)
    signal.signal(signal.SIGTERM, stop_now)
    print(f"[run] {URL}{PATH} x{CONCURRENCY} for {DURATION_SECONDS}s ({REQUEST_DELAY_SECONDS}s pause)", flush=True)

    with ThreadPoolExecutor(CONCURRENCY) as pool:
        for _ in range(CONCURRENCY):
            pool.submit(worker, stop, lock, stats)

        deadline: float = time.monotonic() + DURATION_SECONDS
        while time.monotonic() < deadline and not stop.is_set():
            time.sleep(0.25)

        stop.set()

    ok: int = stats.pop("ok", 0)
    errors: int = sum(stats.values())
    print(f"[done] ok={ok} errors={errors}", flush=True)
    if errors:
        print("[errors] " + ", ".join(f"{name}:{count}" for name, count in sorted(stats.items())), flush=True)

if __name__ == "__main__":
    main()
