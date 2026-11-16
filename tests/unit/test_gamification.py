"""Unit tests for gamification, XP progression, and level thresholds."""

from app.services.gamification.xp_service import XPService


def test_level_calculation_base():
    assert XPService.calculate_level(0) == 1
    assert XPService.calculate_level(50) == 1
    assert XPService.calculate_level(100) == 2
    assert XPService.calculate_level(249) == 2
    assert XPService.calculate_level(250) == 3
    assert XPService.calculate_level(1000) == 5


def test_level_info_progress_percentage():
    # At 50 XP (Level 1 requires 0, Level 2 requires 100), progress is 50%
    info = XPService.get_level_info(50)
    assert info.current_level == 1
    assert info.current_xp == 50
    assert info.next_level_xp == 100
    assert info.progress_percentage == 50.0
    assert info.xp_needed_for_next == 50


def test_level_info_higher():
    # At 250 XP (Level 3), next is Level 4 (500 XP). Span = 250 XP.
    # At 375 XP, progress should be 50% of Level 3
    info = XPService.get_level_info(375)
    assert info.current_level == 3
    assert info.progress_percentage == 50.0
