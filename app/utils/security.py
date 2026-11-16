"""EduLingua AI — Security Utilities.

Webhook verification, password hashing, and JWT token management.
"""

from __future__ import annotations

import hmac
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# ── Password hashing ────────────────────────────────────────────

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*."""
    return _pwd_ctx.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify *password* against a bcrypt *hashed* value."""
    return _pwd_ctx.verify(password, hashed)


# ── Webhook secret verification ─────────────────────────────────


def verify_webhook_secret(request_token: str | None, expected_token: str | None) -> bool:
    """Constant-time comparison of webhook secret tokens.

    Prevents timing attacks on webhook authentication.
    """
    if request_token is None or expected_token is None:
        return False

    request_token = str(request_token)
    expected_token = str(expected_token)
    if not request_token or not expected_token:
        return False

    return hmac.compare_digest(request_token, expected_token)


# ── JWT tokens ───────────────────────────────────────────────────

_JWT_ALGORITHM = "HS256"


def create_access_token(
    data: dict[str, Any],
    secret_key: str | None = None,
    *,
    expires_delta: timedelta | None = None,
    secret: str | None = None,
    expires: timedelta | None = None,
) -> str:
    """Create a signed JWT access token.

    Supports both ``secret_key``/``expires_delta`` and legacy ``secret``/``expires``
    parameter names for compatibility across the codebase.
    """
    resolved_secret = secret_key if secret_key is not None else secret
    if resolved_secret is None:
        raise ValueError("A JWT secret must be provided")

    resolved_delta = expires_delta if expires_delta is not None else expires
    payload = data.copy()
    expire = datetime.now(UTC) + (resolved_delta or timedelta(minutes=60))
    payload["exp"] = expire
    return jwt.encode(payload, resolved_secret, algorithm=_JWT_ALGORITHM)


def decode_access_token(
    token: str,
    secret_key: str | None = None,
    *,
    secret: str | None = None,
) -> dict[str, Any] | None:
    """Decode and verify a JWT access token.

    Returns the payload dict on success, or ``None`` if the token is
    invalid or expired.
    """
    resolved_secret = secret_key if secret_key is not None else secret
    if resolved_secret is None:
        return None

    try:
        return jwt.decode(token, resolved_secret, algorithms=[_JWT_ALGORITHM])
    except JWTError:
        logger.debug("JWT decode failed (token rejected)")
        return None
