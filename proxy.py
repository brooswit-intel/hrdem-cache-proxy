"""Entrypoint: loopback-only byte-range cache proxy for Canada HRDEM 2m.

Run: python3 proxy.py
Env overrides: HRDEM_CACHE_UPSTREAM, HRDEM_CACHE_PORT, HRDEM_CACHE_DB
"""
import os

from range_cache_proxy import run_server
from source import SOURCE

if __name__ == "__main__":
    port = int(os.environ.get("HRDEM_CACHE_PORT", "8102"))
    db = os.environ.get("HRDEM_CACHE_DB", "hrdem-cache.sqlite3")
    server, proxy = run_server(SOURCE, db, port)
    print(f"hrdem cache proxy on http://127.0.0.1:{port} -> upstream {proxy.upstream_base}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        proxy.close()
