"""
Unit tests for HumanCLIPlayer prompt parsing and input validation."""

import pytest

from qwixx.core.action import MarkAction, PassAction
from qwixx.core.dice import DiceRoll
from qwixx.core.sheet import RowColor, ScoreSheet
from qwixx.players.human_player import HumanCLIPlayer

# MonkeyPatch (part of pytest) lets us simulate user input via stdin
def test_human_player_selects_valid_choice(monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate user typing "1" then pressing Enter
    monkeypatch.setattr("builtins.input", lambda _: "1")

    player = HumanCLIPlayer("Tester")
    sheet = ScoreSheet()
    roll = DiceRoll(white1=2, white2=3) # White sum = 5
    valid_actions: list[PassAction | MarkAction] = [PassAction(), MarkAction(RowColor.RED, 5)]

    chosen = player.choose_white_action(sheet, roll, valid_actions, is_active=True)
    assert chosen == MarkAction(RowColor.RED, 5)

def test_human_player_recovers_from_invalid_input(monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate user entering invalid inputs before a valid index: "abc" -> "99" -> "0"
    inputs = iter(["abc", "99", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    player = HumanCLIPlayer("Tester")
    sheet = ScoreSheet()
    roll = DiceRoll(white1=1, white2=1) # White sum = 2
    valid_actions: list[PassAction | MarkAction] = [PassAction()]

    chosen = player.choose_color_action(sheet, roll, valid_actions)
    assert chosen == PassAction()

