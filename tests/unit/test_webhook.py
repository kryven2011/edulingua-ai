"""Unit tests for Telegram Webhook security and queue ingestion."""

from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app

# Provide dummy test settings
TEST_SECRET = "test_webhook_secret_key_12345"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
    monkeypatch.setenv("WEBHOOK_BASE_URL", "https://test.domain.com")
    monkeypatch.setenv("WEBHOOK_SECRET", TEST_SECRET)
    return TestClient(app)


def test_webhook_rejects_missing_secret(client):
    """Webhook must return 403 when secret header is missing."""
    resp = client.post("/telegram/webhook", json={"update_id": 100})
    assert resp.status_code == 403


def test_webhook_rejects_invalid_secret(client):
    """Webhook must return 403 when secret header is incorrect."""
    headers = {"X-Telegram-Bot-Api-Secret-Token": "invalid_secret"}
    resp = client.post("/telegram/webhook", json={"update_id": 100}, headers=headers)
    assert resp.status_code == 403


@patch("app.api.webhook.get_redis_client")
def test_webhook_accepts_valid_update(mock_redis_getter, client):
    """Webhook returns fast 200 and pushes to queue on valid secret."""
    mock_redis = AsyncMock()
    mock_redis.set.return_value = True  # New update_id
    mock_redis.rpush.return_value = 1
    mock_redis_getter.return_value = mock_redis

    headers = {"X-Telegram-Bot-Api-Secret-Token": TEST_SECRET}
    payload = {
        "update_id": 999123,
        "message": {
            "message_id": 1,
            "from": {"id": 1234567, "is_bot": False, "first_name": "Alex"},
            "chat": {"id": 1234567, "type": "private"},
            "text": "/start",
        },
    }

    resp = client.post("/telegram/webhook", json=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.text == "ok"


@patch("app.api.webhook.get_redis_client")
def test_webhook_idempotency_duplicate_update(mock_redis_getter, client):
    """Webhook drops already seen update_id without re-enqueueing."""
    mock_redis = AsyncMock()
    mock_redis.set.return_value = False  # Already seen update_id
    mock_redis_getter.return_value = mock_redis

    headers = {"X-Telegram-Bot-Api-Secret-Token": TEST_SECRET}
    payload = {"update_id": 999123, "message": {"text": "hi"}}

    resp = client.post("/telegram/webhook", json=payload, headers=headers)
    assert resp.status_code == 200
    # Should NOT have called rpush because it's duplicate
    mock_redis.rpush.assert_not_called()
