import os
import pytest
import requests

@pytest.mark.skipif(not os.getenv("BOT_TOKEN"), reason="BOT_TOKEN not set")
def test_telegram_getme_smoke():
    token = os.getenv("BOT_TOKEN")
    r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
    assert r.status_code == 200, f"HTTP {r.status_code}"
    data = r.json()
    assert data.get("ok") is True, f"Telegram returned not ok: {data}"
    assert "result" in data and "username" in data["result"], f"No username in {data}"

