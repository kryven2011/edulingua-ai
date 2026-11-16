"""EduLingua AI — FSM States.

All finite state machine state groups for bot conversation flows.
"""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """User multi-step onboarding and registration flow."""

    choosing_language = State()
    entering_name = State()
    choosing_goal = State()
    choosing_learning_language = State()
    choosing_level = State()


class LanguageSelection(StatesGroup):
    """Initial language selection flow."""

    choosing = State()


class EduAIStates(StatesGroup):
    """EduAI tutor interaction states."""

    selecting_subject = State()
    asking_question = State()
    waiting_response = State()
    checking_answer = State()


class LinguaStates(StatesGroup):
    """LinguaBot language-learning states."""

    selecting_language = State()
    level_test = State()
    vocabulary = State()
    grammar = State()
    speaking = State()
    writing = State()
    listening = State()


class SettingsStates(StatesGroup):
    """Settings menu states."""

    main = State()
    changing_language = State()
    changing_learning_lang = State()
    confirm_reset = State()


class AdminStates(StatesGroup):
    """Admin management states."""

    broadcast_message = State()
    manage_user = State()
