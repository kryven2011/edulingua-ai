"""Unit tests for SuperMemo-2 spaced repetition algorithm."""

from app.services.language.spaced_repetition import SpacedRepetitionService


def test_sm2_first_repetition_perfect():
    # Quality 5 (perfect recall)
    res = SpacedRepetitionService.calculate_next_review(quality=5)
    assert res.review_count == 1
    assert res.interval_days == 1
    assert res.status == "learning"
    assert res.ease_factor >= 2.5


def test_sm2_second_repetition():
    res = SpacedRepetitionService.calculate_next_review(
        quality=5,
        current_ease_factor=2.6,
        review_count=1,
        current_interval=1,
    )
    assert res.review_count == 2
    assert res.interval_days == 6
    assert res.status == "review"


def test_sm2_failed_recall_resets():
    # Quality 1 (total blackout)
    res = SpacedRepetitionService.calculate_next_review(
        quality=1,
        current_ease_factor=2.5,
        review_count=4,
        current_interval=15,
    )
    assert res.review_count == 0
    assert res.interval_days == 1
    assert res.status == "learning"
    assert res.ease_factor < 2.5
