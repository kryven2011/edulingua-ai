"""Unit tests for security utilities."""

from datetime import timedelta

from app.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
    verify_webhook_secret,
)


def test_webhook_secret_verification():
    secret = "super_secure_secret_token_123"
    assert verify_webhook_secret(secret, secret) is True
    assert verify_webhook_secret("wrong_token", secret) is False
    assert verify_webhook_secret("", secret) is False


def test_password_hashing():
    raw = "MySecretPass2026!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPass", hashed) is False


def test_jwt_access_token():
    secret = "jwt_test_secret_key_999"
    payload = {"sub": "user-uuid-123", "role": "admin"}
    token = create_access_token(payload, secret_key=secret, expires_delta=timedelta(minutes=15))

    decoded = decode_access_token(token, secret_key=secret)
    assert decoded is not None
    assert decoded["sub"] == "user-uuid-123"
    assert decoded["role"] == "admin"

    # Decoding with wrong secret fails
    wrong_decoded = decode_access_token(token, secret_key="wrong_secret")
    assert wrong_decoded is None
