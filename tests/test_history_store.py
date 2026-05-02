from app.history_store import load_previous_source_log, save_previous_source_log


def test_history_store_roundtrip(tmp_path):
    p = tmp_path / "history.json"
    payload = [{"a": 1}]
    save_previous_source_log(payload, str(p))
    loaded = load_previous_source_log(str(p))
    assert loaded == payload