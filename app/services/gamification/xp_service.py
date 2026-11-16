"""EduLingua AI — XP & Leveling Gamification Service.

Calculates levels, thresholds, progress, and awards XP with idempotency guarantees.
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import UserProfile
from app.database.repositories.gamification_repo import GamificationRepository


@dataclass
class LevelInfo:
    """Detailed user level progress."""

    current_level: int
    current_xp: int
    next_level_xp: int
    xp_in_current_level: int
    xp_needed_for_next: int
    progress_percentage: float


class XPService:
    """Service managing experience points, levels, and level-ups."""

    # Level thresholds: Level 1 starts at 0 XP
    LEVEL_THRESHOLDS = [
        0,       # Level 1
        100,     # Level 2
        250,     # Level 3
        500,     # Level 4
        1000,    # Level 5
        1750,    # Level 6
        2750,    # Level 7
        4000,    # Level 8
        5500,    # Level 9
        7500,    # Level 10
        10000,   # Level 11
        13000,   # Level 12
        16500,   # Level 13
        20500,   # Level 14
        25000,   # Level 15
    ]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = GamificationRepository(session)

    @classmethod
    def calculate_level(cls, xp: int) -> int:
        """Determine level based on total XP."""
        if xp <= 0:
            return 1
        for level, threshold in enumerate(cls.LEVEL_THRESHOLDS, start=1):
            if xp < threshold:
                return level - 1
        # Above defined levels: logarithmic scaling
        extra_xp = xp - cls.LEVEL_THRESHOLDS[-1]
        extra_levels = math.floor(math.sqrt(extra_xp / 100))
        return len(cls.LEVEL_THRESHOLDS) + extra_levels

    @classmethod
    def get_threshold_for_level(cls, level: int) -> int:
        """Return minimum XP required to reach given level."""
        if level <= 1:
            return 0
        idx = level - 1
        if idx < len(cls.LEVEL_THRESHOLDS):
            return cls.LEVEL_THRESHOLDS[idx]
        extra = level - len(cls.LEVEL_THRESHOLDS)
        return cls.LEVEL_THRESHOLDS[-1] + (extra ** 2) * 100

    @classmethod
    def get_level_info(cls, current_xp: int) -> LevelInfo:
        """Compute user progress towards next level."""
        level = cls.calculate_level(current_xp)
        current_threshold = cls.get_threshold_for_level(level)
        next_threshold = cls.get_threshold_for_level(level + 1)

        level_span = max(1, next_threshold - current_threshold)
        xp_in_level = max(0, current_xp - current_threshold)
        needed = max(0, next_threshold - current_xp)
        percentage = min(100.0, max(0.0, (xp_in_level / level_span) * 100.0))

        return LevelInfo(
            current_level=level,
            current_xp=current_xp,
            next_level_xp=next_threshold,
            xp_in_current_level=xp_in_level,
            xp_needed_for_next=needed,
            progress_percentage=round(percentage, 1),
        )

    async def award_xp(
        self,
        user_id: uuid.UUID,
        amount: int,
        source: str,
        idempotency_key: str,
        description: str | None = None,
        source_id: uuid.UUID | None = None,
    ) -> tuple[int, bool, bool, int]:
        """Award XP and check for level up.
        
        Returns:
            Tuple: (new_xp, was_awarded, did_level_up, new_level)
        """
        # Fetch current profile level
        stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        profile = (await self.session.execute(stmt)).scalar_one_or_none()
        old_level = profile.level if profile else 1

        new_xp, awarded = await self.repo.award_xp(
            user_id=user_id,
            amount=amount,
            source=source,
            idempotency_key=idempotency_key,
            description=description,
            source_id=source_id,
        )

        if not awarded:
            return new_xp, False, False, old_level

        new_level = self.calculate_level(new_xp)
        leveled_up = new_level > old_level

        if leveled_up:
            upd = (
                update(UserProfile)
                .where(UserProfile.user_id == user_id)
                .values(level=new_level)
            )
            await self.session.execute(upd)

        return new_xp, True, leveled_up, new_level
