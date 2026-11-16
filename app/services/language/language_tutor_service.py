"""EduLingua AI — Language Tutor Service (LinguaBot).

Handles vocabulary training, grammar lessons, conversational speaking scenarios,
writing reviews, and proficiency level tests.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.language import (
    GrammarLesson,
    Language,
    LanguageLevel,
    VocabularyWord,
)
from app.database.repositories.gamification_repo import GamificationRepository
from app.database.repositories.language_repo import LanguageRepository
from app.services.ai.prompts import (
    GRAMMAR_PROMPT,
    LEVEL_TEST_PROMPT,
    LINGUA_SYSTEM_PROMPT,
    VOCABULARY_PROMPT,
)
from app.services.ai.provider import AIProvider, AIResponse
from app.services.language.spaced_repetition import SpacedRepetitionService

logger = logging.getLogger(__name__)


class LanguageTutorService:
    """Service orchestrating foreign language education."""

    DEFAULT_LANGUAGES = [
        {"code": "en", "name_ru": "Английский", "name_uz": "Ingliz tili", "name_en": "English"},
        {"code": "ru", "name_ru": "Русский", "name_uz": "Rus tili", "name_en": "Russian"},
        {"code": "uz", "name_ru": "Узбекский", "name_uz": "O'zbek tili", "name_en": "Uzbek"},
        {"code": "de", "name_ru": "Немецкий", "name_uz": "Nemis tili", "name_en": "German"},
        {"code": "fr", "name_ru": "Французский", "name_uz": "Fransuz tili", "name_en": "French"},
        {"code": "es", "name_ru": "Испанский", "name_uz": "Ispan tili", "name_en": "Spanish"},
    ]

    def __init__(self, session: AsyncSession, ai_provider: AIProvider) -> None:
        self.session = session
        self.ai = ai_provider
        self.repo = LanguageRepository(session)
        self.gamification = GamificationRepository(session)

    async def get_active_languages(self) -> Sequence[Language]:
        """Fetch active languages, seeding defaults if empty."""
        langs = await self.repo.get_active_languages()
        if not langs:
            for l_data in self.DEFAULT_LANGUAGES:
                lang = Language(
                    code=l_data["code"],
                    name_ru=l_data["name_ru"],
                    name_uz=l_data["name_uz"],
                    name_en=l_data["name_en"],
                    is_active=True,
                )
                self.session.add(lang)
            await self.session.flush()
            langs = await self.repo.get_active_languages()
        return langs

    async def get_language_by_code(self, code: str) -> Language | None:
        """Find language by code."""
        return await self.repo.get_by_code(code)

    async def get_user_level(self, user_id: uuid.UUID, language_code: str) -> str:
        """Get user's current assessed level (default A1)."""
        lang = await self.get_language_by_code(language_code)
        if not lang:
            return "A1"
        level_obj = await self.repo.get_user_level(user_id, lang.id)
        return level_obj.level if level_obj else "A1"

    async def set_user_level(
        self, user_id: uuid.UUID, language_code: str, level: str, score: int = 100
    ) -> None:
        """Record newly determined level."""
        lang = await self.get_language_by_code(language_code)
        if lang:
            await self.repo.set_user_level(user_id, lang.id, level, score)

    async def generate_vocabulary_card(
        self, user_id: uuid.UUID, language_code: str, interface_lang: str = "ru"
    ) -> dict[str, Any]:
        """Provide a word for study (via AI generation or review queue)."""
        lang = await self.get_language_by_code(language_code)
        target_name = lang.name_en if lang else language_code

        prompt = (
            f"Generate ONE useful vocabulary word in {target_name} for an intermediate learner.\n"
            f"Format response strictly as JSON with keys: 'word', 'translation', 'pronunciation', 'example_target', 'example_translation', 'topic'.\n"
            f"The translations must be in language '{interface_lang}'."
        )

        resp = await self.ai.generate(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a vocabulary curator. Return strictly valid JSON without markdown wrapping.",
        )

        import json
        clean_text = resp.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            data = json.loads(clean_text)
        except Exception:
            data = {
                "word": "Achievement",
                "translation": "Достижение",
                "pronunciation": "/əˈtʃiːvmənt/",
                "example_target": "Passing the exam was a great achievement.",
                "example_translation": "Сдача экзамена была отличным достижением.",
                "topic": "General",
            }
        return data

    async def record_word_review(
        self,
        user_id: uuid.UUID,
        word_id: uuid.UUID,
        quality: int,  # 0 to 5
    ) -> None:
        """Apply spaced repetition update on word recall."""
        # Calculate new interval
        res = SpacedRepetitionService.calculate_next_review(quality=quality)
        await self.repo.save_or_update_word_review(
            user_id=user_id,
            word_id=word_id,
            next_review_at=res.next_review_at,
            ease_factor=res.ease_factor,
            review_count=res.review_count,
            status=res.status,
        )

        # Award XP for learning/reviewing words
        idem = f"word:{user_id}:{word_id}:{res.review_count}"
        await self.gamification.award_xp(
            user_id=user_id,
            amount=5,
            source="word_learned",
            idempotency_key=idem,
            description="Word studied",
        )

    async def start_speaking_session(
        self,
        language_code: str,
        scenario: str,
        level: str = "B1",
        interface_lang: str = "ru",
    ) -> str:
        """Initiate AI speaking partner dialogue for the chosen scenario."""
        scenario_prompts = {
            "intro": "Meeting a new person at a conference or social event.",
            "travel": "At the airport checking in luggage and asking for directions.",
            "restaurant": "Ordering dinner at a traditional local restaurant.",
            "shop": "Asking for sizes, discounts, and payment methods at a clothing store.",
            "work": "A brief job interview or business catch-up with a colleague.",
            "study": "Discussing a group project with a classmate at university.",
            "daily": "Talking about weekend plans and favorite hobbies with a friend.",
        }
        topic_desc = scenario_prompts.get(scenario, "A friendly daily conversation.")

        system_prompt = (
            f"You are an encouraging native speaking coach in {language_code}. Level of student: {level}.\n"
            f"Scenario: {topic_desc}\n"
            f"Rule 1: Always respond in {language_code}.\n"
            f"Rule 2: Keep your replies relatively short (2-3 sentences), natural, and ask an engaging open question to prompt student reply.\n"
            f"Start the dialogue now as your character in the scenario."
        )

        resp = await self.ai.generate(
            messages=[{"role": "user", "content": f"Start the conversation for scenario: {scenario}."}],
            system_prompt=system_prompt,
        )
        return resp.text

    async def reply_speaking_session(
        self,
        user_id: uuid.UUID,
        language_code: str,
        scenario: str,
        conversation_history: list[dict[str, str]],
        student_message: str,
        level: str = "B1",
        interface_lang: str = "ru",
    ) -> str:
        """Respond to student's spoken/text message, correcting mistakes constructively."""
        system_prompt = (
            f"You are an intelligent language partner and tutor in {language_code} (Student level: {level}).\n"
            f"Scenario: {scenario}.\n\n"
            f"Your tasks on EVERY response:\n"
            f"1. In a brief block marked '💡 Feedback' (translated to {interface_lang}), gently correct any grammar/vocabulary errors in the student's message and suggest a more natural native phrasing.\n"
            f"2. In character, reply naturally in {language_code} to continue the conversation, ending with a question."
        )

        messages = list(conversation_history)
        messages.append({"role": "user", "content": student_message})

        resp = await self.ai.generate(messages=messages, system_prompt=system_prompt)

        # Award XP for active speaking practice
        idem = f"speak:{user_id}:{uuid.uuid4()}"
        await self.gamification.award_xp(
            user_id=user_id,
            amount=10,
            source="lesson",
            idempotency_key=idem,
            description="Speaking practice",
        )
        return resp.text

    async def check_writing(
        self,
        user_id: uuid.UUID,
        language_code: str,
        text: str,
        interface_lang: str = "ru",
    ) -> str:
        """Perform comprehensive essay/writing analysis."""
        prompt = (
            f"Analyze the following student text written in language '{language_code}'.\n\n"
            f"Text: \"{text}\"\n\n"
            f"Please structure your review as follows (in {interface_lang}):\n"
            f"1. 📊 Estimated CEFR Level (A1-C2).\n"
            f"2. 🔍 Grammar & Spelling Corrections (quote mistakes and show corrected version).\n"
            f"3. 🌟 Vocabulary Suggestions (better synonyms and collocations).\n"
            f"4. ✍️ Improved Full Version.\n"
            f"5. 💡 Overall constructive advice."
        )

        resp = await self.ai.generate(
            messages=[{"role": "user", "content": prompt}],
            system_prompt="You are a professional language examiner and editor.",
        )

        idem = f"writing:{user_id}:{uuid.uuid4()}"
        await self.gamification.award_xp(
            user_id=user_id,
            amount=20,
            source="lesson",
            idempotency_key=idem,
            description="Writing submission review",
        )
        return resp.text
