"""Unit tests for Qwixx sheet logic, scoring, and row locking."""

import pytest
from qwixx.core.sheet import Row, RowColor, ScoreSheet


def test_row_left_to_right_progression() -> None:
    red_row = Row(color=RowColor.RED, ascending=True)
    
    # First mark
    assert red_row.can_mark(4)
    red_row.mark(4)

    # Cannot mark numbers left of red 4 (or 4 itself)
    assert not red_row.can_mark(2)
    assert not red_row.can_mark(4)

    # Can mark numbers to the right of red 4
    assert red_row.can_mark(7)
    red_row.mark(7)
    assert red_row.marked_numbers == [4, 7]


def test_descending_row_progression() -> None:
    blue_row = Row(color=RowColor.BLUE, ascending=False)

    assert blue_row.can_mark(10)
    blue_row.mark(10)

    # Descending row: numbers to the right are smaller
    assert not blue_row.can_mark(11)
    assert blue_row.can_mark(8)


def test_locking_requires_minimum_marks() -> None:
    red_row = Row(color=RowColor.RED, ascending=True)

    # Mark 4 numbers
    for num in [2, 3, 4, 5]:
        red_row.mark(num)

    # 4 marks cannot lock row
    assert not red_row.can_mark(12)

    # Mark 5th number
    red_row.mark(6)
    assert red_row.can_mark(12)  # Now can mark the lock number

    locked = red_row.mark(12)
    assert locked is True
    assert red_row.is_locked is True
    assert red_row.has_lock_bonus is True  # This sheet triggered the lock

    # 6 numbers + 1 lock bonus = 7 marks, scoring 28 points
    assert red_row.mark_count == 7
    assert red_row.score() == 28


def test_external_lock_prevents_marks_without_bonus() -> None:
    green_row = Row(color=RowColor.GREEN, ascending=False)
    green_row.mark(11)
    green_row.mark(9)

    # Opponent locks green
    green_row.external_lock()

    assert green_row.is_locked is True
    assert green_row.has_lock_bonus is False  # This sheet did not trigger the lock
    assert not green_row.can_mark(8) # Cannot mark after external lock

    # Still scores the 2 marks made before the lock (3 points)
    assert green_row.mark_count == 2
    assert green_row.score() == 3


def test_scoresheet_penalties_and_total() -> None:
    sheet = ScoreSheet()

    # Red: mark 2,3 -> 2 marks (3 pts)
    sheet.rows[RowColor.RED].mark(2)
    sheet.rows[RowColor.RED].mark(3)

    # Green: mark 12, 11, 10 -> 3 marks (6 pts)
    sheet.rows[RowColor.GREEN].mark(12)
    sheet.rows[RowColor.GREEN].mark(11)
    sheet.rows[RowColor.GREEN].mark(10)

    # 2 penalties -> -10 pts (5 pts each)
    sheet.add_penalty()
    sheet.add_penalty()

    # Expected: 3 + 6 - 10 = -1
    assert sheet.total_score() == -1