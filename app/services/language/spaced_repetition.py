"""EduLingua AI — SuperMemo-2 (SM-2) Spaced Repetition Algorithm.

Calculates optimal review intervals for vocabulary retention.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import math


@dataclass
class ReviewResult:
    """Calculated parameters for the next review."""

    next_review_at: datetime
    ease_factor: float
    review_count: int
    interval_days: int
    status: str  # "learning", "review", "mastered"


class SpacedRepetitionService:
    """Implementation of standard SM-2 algorithm."""

    MIN_EASE_FACTOR = 1.3
    DEFAULT_EASE_FACTOR = 2.5

    @classmethod
    def calculate_next_review(
        cls,
        quality: int,  # 0 to 5
        current_ease_factor: float = 2.5,
        review_count: int = 0,
        current_interval: int = 1,
    ) -> ReviewResult:
        """Calculate next review date based on user recall quality.
        
        Args:
            quality: 0 (blackout) to 5 (perfect recall).
            current_ease_factor: Current difficulty multiplier.
            review_count: Number of consecutive successful reviews.
            current_interval: Previous interval in days.
        """
        quality = max(0, min(5, quality))
        ef = max(
            cls.MIN_EASE_FACTOR,
            current_ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
        )

        if quality < 3:
            # Failed recall -> start over
            new_review_count = 0
            interval_days = 1
            status = "learning"
        else:
            # Successful recall
            new_review_count = review_count + 1
            if new_review_count == 1:
                interval_days = 1
                status = "learning"
            elif new_review_count == 2:
                interval_days = 6
                status = "review"
            else:
                interval_days = math.ceil(current_interval * ef)
                status = "mastered" if new_review_count >= 5 else "review"

        next_date = datetime.utcnow() + timedelta(days=interval_days)

        return ReviewResult(
            next_review_at=next_date,
            ease_factor=round(ef, 2),
            review_count=new_review_count,
            interval_days=interval_days,
            status=status,
        )
