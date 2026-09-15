#!/usr/bin/env bash
set -e

echo "[entrypoint] waiting for database to be ready..."
python - <<'PY'
import os
import sys
import time

import psycopg2
from psycopg2 import OperationalError

dsn = os.environ.get(
    "DATABASE_URL",
    "postgresql://upr_rank:upr_rank@postgres:5432/upr_rank",
)

for _ in range(60):
    try:
        psycopg2.connect(dsn)
        break
    except OperationalError:
        time.sleep(1)
else:
    print("[entrypoint] database not reachable after 60s", file=sys.stderr)
    sys.exit(1)
PY

echo "[entrypoint] database is ready"
exec uvicorn src.main:app --host 0.0.0.0 --port 8000