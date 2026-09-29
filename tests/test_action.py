"""Unit tests for action representation and legal move generation."""

from qwixx.core.action import (
    MarkAction, PassAction, get_legal_color_actions, get_legal_white_actions
)
from qwixx.core.dice import DiceRoll
from qwixx.core.sheet import RowColor, ScoreSheet


def test_legal_white_actions() -> None:
    sheet = ScoreSheet()
    # White dice sum to 4
    roll = DiceRoll(white1=1, white2=3)

    legal = get_legal_white_actions(sheet, roll)

    # Ascending rows (Red, Yellow) can mark 4
    # Descending rows (Green, Blue) can also mark 4 (would be stupid but legal)
    # Plus the PassAction -> 5 legal actions total
    assert PassAction() in legal
    assert MarkAction(color=RowColor.RED, number=4) in legal
    assert MarkAction(color=RowColor.YELLOW, number=4) in legal
    assert MarkAction(color=RowColor.GREEN, number=4) in legal
    assert MarkAction(color=RowColor.BLUE, number=4) in legal
    assert len(legal) == 5


def test_legal_white_actions_respects_monotonicity() -> None:
    sheet = ScoreSheet()
    # If Red is already marked up to 6, 4 is no longer legal on Red
    sheet.rows[RowColor.RED].mark(6)

    roll = DiceRoll(white1=2, white2=2) # White sum = 4
    legal = get_legal_white_actions(sheet, roll)

    assert MarkAction(RowColor.RED, 4) not in legal
    assert MarkAction(RowColor.YELLOW, 4) in legal


def test_legal_color_actions_active_player() -> None:
    sheet = ScoreSheet()
    # White diceL 2 and 4. Red die: 3.
    # Red combinations: 2+3=5, 4+3=7
    roll = DiceRoll(
        white1=2,
        white2=4,
        colored_dice={RowColor.RED: 3},
    )

    legal = get_legal_color_actions(sheet, roll)

    assert PassAction() in legal
    assert MarkAction(RowColor.RED, 5) in legal
    assert MarkAction(RowColor.RED, 7) in legal
    # Blue, Yellow, Green were not rolled, so no actions for them
    assert len(legal) == 3