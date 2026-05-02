from app.retry_runner import run_with_retries


def test_run_with_retries_success():
    calls = {"count": 0}

    def flaky():
        calls["count"] += 1
        if calls["count"] < 2:
            raise RuntimeError("temporary")
        return "ok"

    result = run_with_retries(flaky, attempts=2, delays_seconds=[0, 0])
    assert result == "ok"