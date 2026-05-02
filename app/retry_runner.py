import time
from typing import Callable, TypeVar

T = TypeVar("T")


def run_with_retries(
    func: Callable[[], T],
    attempts: int = 3,
    delays_seconds: list[int] | None = None,
) -> T:
    if delays_seconds is None:
        delays_seconds = [0, 600, 900]

    last_exc = None
    for idx in range(attempts):
        try:
            return func()
        except Exception as exc:
            last_exc = exc
            if idx < attempts - 1:
                time.sleep(delays_seconds[idx])
    raise last_exc