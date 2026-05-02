from pathlib import Path
import app.run_lock as run_lock


def test_run_lock_cycle(tmp_path, monkeypatch):
    monkeypatch.setattr(run_lock, "LOCK_PATH", tmp_path / ".run.lock")
    run_lock.acquire_run_lock()
    assert run_lock.LOCK_PATH.exists()
    run_lock.release_run_lock()
    assert not run_lock.LOCK_PATH.exists()