"""EduLingua AI — Admin Panel Web Application.

Serves login and dashboard HTML interfaces.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(tags=["admin_frontend"])


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request) -> HTMLResponse:
    """Render admin authentication screen."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request) -> HTMLResponse:
    """Render admin management dashboard."""
    return templates.TemplateResponse("dashboard.html", {"request": request})
