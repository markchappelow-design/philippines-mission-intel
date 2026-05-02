from pathlib import Path


LOCK_PATH = Path("output/.run.lock")


def acquire_run_lock() -> None:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    if LOCK_PATH.exists():
        raise RuntimeError("Run lock already present. Another execution may still be active.")
    LOCK_PATH.write_text("locked", encoding="utf-8")


def release_run_lock() -> None:
    if LOCK_PATH.exists():
        LOCK_PATH.unlink()