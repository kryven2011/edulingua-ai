"""EduLingua AI — Database Seeding Script.

Initializes PostgreSQL with required seed data:
- School & university subjects
- Foreign languages
- Gamification achievements
- Daily quest templates
- Default superadministrator account
"""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select

from app.config import get_settings
from app.database.models.admin import Admin
from app.database.models.base import Base
from app.database.session import close_engine, get_db_session, get_engine
from app.services.education.subject_service import SubjectService
from app.services.gamification.achievement_service import AchievementService
from app.services.gamification.daily_task_service import DailyTaskService
from app.services.language.language_tutor_service import LanguageTutorService
from app.utils.security import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")


async def init_database() -> None:
    """Create all tables and seed required reference records."""
    engine = get_engine()
    settings = get_settings()

    logger.info("Creating database tables if not existing...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with get_db_session() as session:
        # 1. Seed subjects
        logger.info("Seeding school subjects...")
        subject_service = SubjectService(session)
        await subject_service.get_active_subjects()

        # 2. Seed foreign languages
        logger.info("Seeding foreign languages...")
        lang_service = LanguageTutorService(session, ai_provider=None)  # type: ignore[arg-type]
        await lang_service.get_active_languages()

        # 3. Seed achievements
        logger.info("Seeding achievements...")
        ach_service = AchievementService(session)
        await ach_service.ensure_defaults()

        # 4. Seed daily tasks
        logger.info("Seeding daily quests...")
        daily_service = DailyTaskService(session)
        await daily_service.ensure_daily_tasks()

        # 5. Seed default admin account
        admin_user = settings.admin_username
        stmt = select(Admin).where(Admin.username == admin_user)
        admin = (await session.execute(stmt)).scalar_one_or_none()
        if not admin:
            logger.info("Creating default admin account: '%s'", admin_user)
            default_pwd = "AdminSecurePassword2026!"
            new_admin = Admin(
                username=admin_user,
                password_hash=hash_password(default_pwd),
                email="admin@edulingua.ai",
                role="super_admin",
                is_active=True,
            )
            session.add(new_admin)
            await session.commit()
            logger.info("Admin created with username '%s' and default password '%s'", admin_user, default_pwd)
        else:
            await session.commit()

    await close_engine()
    logger.info("Database initialization completed successfully!")


if __name__ == "__main__":
    asyncio.run(init_database())
