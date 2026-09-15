"""Entrypoint for the UPR-RANK judge worker process.

The worker is started in Sprint 3 when the Redis queue consumer is
implemented. Until then this module waits so the container stays alive.
"""

import time


def main() -> None:  # pragma: no cover - replaced in Sprint 3
    """Keep the worker container alive until the consumer is implemented."""
    print("[worker] waiting for judge consumer (Sprint 3)")
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()