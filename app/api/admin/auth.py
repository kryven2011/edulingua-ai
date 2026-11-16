"""EduLingua AI — Admin Authentication Endpoint.

Provides JWT issuance for web dashboard access.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.config import get_settings
from app.database.models.admin import Admin
from app.database.session import get_db_session
from app.utils.security import create_access_token, verify_password

router = APIRouter(tags=["admin_auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


@router.post("/api/admin/login", response_model=LoginResponse)
async def admin_login(payload: LoginRequest) -> LoginResponse:
    """Authenticate administrator and return access JWT."""
    settings = get_settings()

    async with get_db_session() as session:
        stmt = select(Admin).where(
            Admin.username == payload.username,
            Admin.is_active == True,  # noqa: E712
        )
        admin = (await session.execute(stmt)).scalar_one_or_none()

        if not admin or not verify_password(payload.password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        token = create_access_token(
            data={"sub": str(admin.id), "username": admin.username, "role": admin.role},
            secret_key=settings.admin_secret_key.get_secret_value(),
            expires_delta=timedelta(minutes=settings.admin_token_expire_minutes),
        )

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            role=admin.role,
        )
