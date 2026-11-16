"""EduLingua AI — Subject Service.

Manages school subjects for EduAI.
"""

from __future__ import annotations

from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.education import Subject
from app.database.repositories.education_repo import EducationRepository


class SubjectService:
    """Service for managing school subjects."""

    DEFAULT_SUBJECTS = [
        {"code": "math", "name_ru": "Математика", "name_uz": "Matematika", "name_en": "Mathematics", "icon": "📐", "sort_order": 1},
        {"code": "algebra", "name_ru": "Алгебра", "name_uz": "Algebra", "name_en": "Algebra", "icon": "📊", "sort_order": 2},
        {"code": "geometry", "name_ru": "Геометрия", "name_uz": "Geometriya", "name_en": "Geometry", "icon": "📏", "sort_order": 3},
        {"code": "physics", "name_ru": "Физика", "name_uz": "Fizika", "name_en": "Physics", "icon": "⚛️", "sort_order": 4},
        {"code": "chemistry", "name_ru": "Химия", "name_uz": "Kimyo", "name_en": "Chemistry", "icon": "🧪", "sort_order": 5},
        {"code": "biology", "name_ru": "Биология", "name_uz": "Biologiya", "name_en": "Biology", "icon": "🧬", "sort_order": 6},
        {"code": "history", "name_ru": "История", "name_uz": "Tarix", "name_en": "History", "icon": "📜", "sort_order": 7},
        {"code": "geography", "name_ru": "География", "name_uz": "Geografiya", "name_en": "Geography", "icon": "🌍", "sort_order": 8},
        {"code": "informatics", "name_ru": "Информатика", "name_uz": "Informatika", "name_en": "Computer Science", "icon": "💻", "sort_order": 9},
        {"code": "literature", "name_ru": "Литература", "name_uz": "Adabiyot", "name_en": "Literature", "icon": "📖", "sort_order": 10},
        {"code": "russian_lang", "name_ru": "Русский язык", "name_uz": "Rus tili", "name_en": "Russian Language", "icon": "🇷🇺", "sort_order": 11},
        {"code": "english_lang", "name_ru": "Английский язык", "name_uz": "Ingliz tili", "name_en": "English Language", "icon": "🇬🇧", "sort_order": 12},
    ]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = EducationRepository(session)

    async def get_active_subjects(self) -> Sequence[Subject]:
        """Fetch all active subjects."""
        subjects = await self.repo.get_active_subjects()
        if not subjects:
            # Seed default subjects if empty
            for s_data in self.DEFAULT_SUBJECTS:
                subject = Subject(
                    code=s_data["code"],
                    name_ru=s_data["name_ru"],
                    name_uz=s_data["name_uz"],
                    name_en=s_data["name_en"],
                    icon=s_data["icon"],
                    sort_order=s_data["sort_order"],
                    is_active=True,
                )
                self.session.add(subject)
            await self.session.flush()
            subjects = await self.repo.get_active_subjects()
        return subjects

    async def get_subject_by_code(self, code: str) -> Subject | None:
        """Find subject by code."""
        return await self.repo.get_subject_by_code(code)
