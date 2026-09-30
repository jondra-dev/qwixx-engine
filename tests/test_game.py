"""Unit tests for QwixxGame orchetration, turns, and game-over conditions."""

import random
import pytest

from qwixx.core.action import Action, MarkAction, PassAction
from qwixx.core.dice import DiceRoll
from qwixx.core.game import QwixxGame
from qwixx.core.sheet import RowColor, ScoreSheet
from qwixx.players.random_player import RandomPlayer
from qwixx.players.base import Player


class AlwaysPassPlayer(Player):
    """Test bot that always passes."""

    def choose_white_action(
        self,
        sheet: ScoreSheet,
        roll: DiceRoll,
        valid_actions: list[Action],
        is_active: bool,
    ) -> Action:
        return PassAction()

    def choose_color_action(
        self,
        sheet: ScoreSheet,
        roll: DiceRoll,
        valid_actions: list[Action],
    ) -> Action:
        return PassAction()


def test_game_requires_at_least_two_players() -> None:
    with pytest.raises(ValueError):
        QwixxGame(players=[RandomPlayer("Solo")])

def test_active_player_penalty_when_passing_both_phases() -> None:
    p1 = AlwaysPassPlayer("Passer1")
    p2 = AlwaysPassPlayer("Passer2")

    game = QwixxGame(players=[p1, p2])

    assert game.sheets[p1].penalties == 0
    # Turn 1: p1 is active. Passing both phases should give them a penalty.
    game.play_turn()
    assert game.sheets[p1].penalties == 1
    assert game.sheets[p2].penalties == 0

    # Turn 2: p2 is active. Passing both phases should give them a penalty.
    game.play_turn()
    assert game.sheets[p1].penalties == 1
    assert game.sheets[p2].penalties == 1

def test_full_game_simulation_completes() -> None:
    # Deterministic seed so the game completes reliably
    rng = random.Random(42)
    p1 = RandomPlayer("Bot1", rng=rng)
    p2 = RandomPlayer("Bot2", rng=rng)

    game = QwixxGame(players=[p1, p2], rng=rng)
    scores = game.play_game()

    assert game.is_game_over
    assert len(scores) == 2
    # Verify game ended either by 2 locked rows or 4 penalties
    ended_by_rows = len(game.locked_rows) >= 2
    ended_by_penalties = any(s.penalties >= 4 for s in game.sheets.values())
    assert ended_by_rows or ended_by_penalties