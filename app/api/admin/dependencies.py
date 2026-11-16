"""EduLingua AI — Admin Authentication Dependencies.

Validates JWT access tokens and enforces administrative RBAC.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from app.config import get_settings
from app.database.models.admin import Admin
from app.database.session import get_db_session
from app.utils.security import decode_access_token

security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Admin:
    """Verify bearer JWT token and return authenticated Admin instance."""
    token = credentials.credentials
    settings = get_settings()

    payload = decode_access_token(
        token=token,
        secret_key=settings.admin_secret_key.get_secret_value(),
    )
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin access token",
        )

    admin_id_str = payload.get("sub")
    if not admin_id_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    async with get_db_session() as session:
        stmt = select(Admin).where(
            Admin.id == uuid.UUID(admin_id_str),
            Admin.is_active == True,  # noqa: E712
        )
        admin = (await session.execute(stmt)).scalar_one_or_none()
        if not admin:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin account disabled or deleted")
        return admin
