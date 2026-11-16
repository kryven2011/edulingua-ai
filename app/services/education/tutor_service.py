"""EduLingua AI — AI Tutor Service (EduAI).

Orchestrates pedagogical dialogues, step-by-step problem solving, photo analysis,
and adaptive explanation modes.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.education import StudySession
from app.database.repositories.education_repo import EducationRepository
from app.database.repositories.gamification_repo import GamificationRepository
from app.services.ai.prompts import EDUAI_SYSTEM_PROMPT, IMAGE_ANALYSIS_PROMPT
from app.services.ai.provider import AIProvider, AIResponse

logger = logging.getLogger(__name__)


class AITutorService:
    """Service providing intelligent tutoring for school and university subjects."""

    def __init__(
        self,
        session: AsyncSession,
        ai_provider: AIProvider,
    ) -> None:
        self.session = session
        self.ai = ai_provider
        self.repo = EducationRepository(session)
        self.gamification = GamificationRepository(session)

    def _format_system_prompt(self, subject: str, level: str = "школьный", lang: str = "ru") -> str:
        """Format base prompt with subject context."""
        return EDUAI_SYSTEM_PROMPT.format(
            subject=subject,
            level=level,
            language=lang,
        )

    async def ask_question(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        question_text: str,
        lang: str = "ru",
    ) -> str:
        """Process student question with full teacher methodology."""
        subject = await self.repo.get_subject_by_code(subject_code)
        subject_id = subject.id if subject else uuid.uuid4()
        subject_name = subject.name_ru if subject else subject_code

        # Start or get active session
        study_session = await self.repo.create_study_session(
            user_id=user_id,
            subject_id=subject_id,
            session_type="question",
        )

        # Record user message
        await self.repo.save_message(
            session_id=study_session.id,
            user_id=user_id,
            role="user",
            content=question_text,
            message_type="text",
        )

        # Fetch recent messages for context
        history = await self.repo.get_recent_messages(study_session.id, limit=6)
        formatted_messages = [
            {"role": m.role, "content": m.content}
            for m in history
        ]

        system_prompt = self._format_system_prompt(subject=subject_name, lang=lang)
        ai_resp: AIResponse = await self.ai.generate(
            messages=formatted_messages,
            system_prompt=system_prompt,
        )

        # Save AI reply
        await self.repo.save_message(
            session_id=study_session.id,
            user_id=user_id,
            role="assistant",
            content=ai_resp.text,
            tokens_used=ai_resp.tokens_used,
        )

        # Award small XP for inquiry
        idem_key = f"edu_q:{study_session.id}:{user_id}"
        await self.gamification.award_xp(
            user_id=user_id,
            amount=10,
            source="lesson",
            idempotency_key=idem_key,
            description=f"Inquiry in {subject_name}",
        )

        return ai_resp.text

    async def analyze_photo_problem(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        lang: str = "ru",
    ) -> str:
        """Extract problem statement from photo and provide step-by-step guidance."""
        subject = await self.repo.get_subject_by_code(subject_code)
        subject_id = subject.id if subject else uuid.uuid4()
        subject_name = subject.name_ru if subject else subject_code

        study_session = await self.repo.create_study_session(
            user_id=user_id,
            subject_id=subject_id,
            session_type="photo_task",
        )

        prompt = (
            f"Внимательно распознай задачу на изображении по предмету '{subject_name}'.\n"
            f"1. Выпиши чётко условие задачи.\n"
            f"2. Объясни тему и физический/математический смысл.\n"
            f"3. Приведи нужные формулы.\n"
            f"4. Разбери решение по шагам.\n"
            f"5. Дай итоговый ответ и задай контрольный вопрос ученику.\n"
            f"Язык ответа: {lang}."
        )

        ai_resp: AIResponse = await self.ai.analyze_image(
            image_data=image_bytes,
            prompt=prompt,
            mime_type=mime_type,
        )

        await self.repo.save_message(
            session_id=study_session.id,
            user_id=user_id,
            role="user",
            content="[Фотография задачи]",
            message_type="image",
        )
        await self.repo.save_message(
            session_id=study_session.id,
            user_id=user_id,
            role="assistant",
            content=ai_resp.text,
            tokens_used=ai_resp.tokens_used,
        )

        # Award XP for solving problem
        idem_key = f"edu_photo:{study_session.id}:{user_id}"
        await self.gamification.award_xp(
            user_id=user_id,
            amount=15,
            source="lesson",
            idempotency_key=idem_key,
            description=f"Photo problem solved in {subject_name}",
        )

        return ai_resp.text

    async def explain_simpler(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        lang: str = "ru",
    ) -> str:
        """Mode: 'Explain simpler' based on the last session context."""
        subject = await self.repo.get_subject_by_code(subject_code)
        subject_id = subject.id if subject else None
        session = await self.repo.get_active_session(user_id, subject_id)
        if not session:
            return "Сначала задайте вопрос или пришлите задачу, чтобы я мог объяснить её проще!"

        history = await self.repo.get_recent_messages(session.id, limit=4)
        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({
            "role": "user",
            "content": "Пожалуйста, объясни этот материал ещё проще, на жизненных примерах и аналогиях, будто мне 10 лет.",
        })

        ai_resp = await self.ai.generate(
            messages=messages,
            system_prompt="Ты дружелюбный и терпеливый учитель. Объясняй максимально просто, с яркими аналогиями.",
        )
        await self.repo.save_message(
            session_id=session.id,
            user_id=user_id,
            role="assistant",
            content=ai_resp.text,
            tokens_used=ai_resp.tokens_used,
        )
        return ai_resp.text

    async def show_another_method(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        lang: str = "ru",
    ) -> str:
        """Mode: 'Show another solving method'."""
        subject = await self.repo.get_subject_by_code(subject_code)
        subject_id = subject.id if subject else None
        session = await self.repo.get_active_session(user_id, subject_id)
        if not session:
            return "Сначала отправьте задачу, чтобы я показал альтернативный способ решения."

        history = await self.repo.get_recent_messages(session.id, limit=4)
        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({
            "role": "user",
            "content": "Покажи совершенно другой, альтернативный способ решения этой задачи (например, графический, аналитический или метод подстановки).",
        })

        ai_resp = await self.ai.generate(
            messages=messages,
            system_prompt="Покажи альтернативное решение задачи с подробным сравнением эффективности методов.",
        )
        await self.repo.save_message(
            session_id=session.id,
            user_id=user_id,
            role="assistant",
            content=ai_resp.text,
            tokens_used=ai_resp.tokens_used,
        )
        return ai_resp.text

    async def give_hint(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        lang: str = "ru",
    ) -> str:
        """Mode: 'Give a hint' (does not reveal full solution)."""
        subject = await self.repo.get_subject_by_code(subject_code)
        subject_id = subject.id if subject else None
        session = await self.repo.get_active_session(user_id, subject_id)
        if not session:
            return "Сначала задайте вопрос или отправьте задачу!"

        history = await self.repo.get_recent_messages(session.id, limit=4)
        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({
            "role": "user",
            "content": "Не давай готовый ответ! Дай только тонкую наводящую подсказку или подскажи первый шаг, чтобы я догадался сам.",
        })

        ai_resp = await self.ai.generate(
            messages=messages,
            system_prompt="Дай только подсказку или наводящий вопрос, развивающий мышление ученика. Не решай задачу за него.",
        )
        await self.repo.save_message(
            session_id=session.id,
            user_id=user_id,
            role="assistant",
            content=ai_resp.text,
            tokens_used=ai_resp.tokens_used,
        )
        return ai_resp.text

    async def check_student_answer(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        answer_text: str,
        lang: str = "ru",
    ) -> str:
        """Verify student's answer with detailed feedback."""
        subject = await self.repo.get_subject_by_code(subject_code)
        subject_id = subject.id if subject else None
        session = await self.repo.get_active_session(user_id, subject_id)
        if not session:
            return "Сначала выберите задачу для проверки!"

        history = await self.repo.get_recent_messages(session.id, limit=4)
        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({
            "role": "user",
            "content": f"Вот мой ответ или моё решение: '{answer_text}'. Проверь его пожалуйста, укажи на ошибки, если они есть, и оцени правильность.",
        })

        ai_resp = await self.ai.generate(
            messages=messages,
            system_prompt="Проверь ответ ученика. Если правильно — похвали и закрепи успех. Если есть ошибка — деликатно покажи, где произошёл сбой логики.",
        )
        await self.repo.save_message(
            session_id=session.id,
            user_id=user_id,
            role="assistant",
            content=ai_resp.text,
            tokens_used=ai_resp.tokens_used,
        )
        # Award XP for checking/trying
        idem = f"check:{session.id}:{uuid.uuid4()}"
        await self.gamification.award_xp(user_id, 15, "quiz", idem, "Answer check")
        return ai_resp.text

    async def generate_similar_task(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        lang: str = "ru",
    ) -> str:
        """Generate a practice task similar to the current one."""
        subject = await self.repo.get_subject_by_code(subject_code)
        subject_id = subject.id if subject else None
        session = await self.repo.get_active_session(user_id, subject_id)
        if not session:
            return "Сначала решите задачу, чтобы я подобрал похожую для закрепления!"

        history = await self.repo.get_recent_messages(session.id, limit=4)
        messages = [{"role": m.role, "content": m.content} for m in history]
        messages.append({
            "role": "user",
            "content": "Сгенерируй похожую задачу на эту же формулу/правило с другими числовыми значениями для самостоятельного решения.",
        })

        ai_resp = await self.ai.generate(
            messages=messages,
            system_prompt="Сгенерируй аналогичную задачу с новыми данными. Предложи ученику решить её и прислать ответ.",
        )
        await self.repo.save_message(
            session_id=session.id,
            user_id=user_id,
            role="assistant",
            content=ai_resp.text,
            tokens_used=ai_resp.tokens_used,
        )
        return ai_resp.text
