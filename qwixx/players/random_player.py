"""qwixx.players.random_player

A baseline bot that makes decisions by picking uniformly at random from 
all currently available legal actions."""

import random

from qwixx.players.base import Player
from qwixx.core.action import Action
from qwixx.core.dice import DiceRoll
from qwixx.core.sheet import ScoreSheet

class RandomPlayer(Player):
    """A baseline bot that selects uniformly at random from legal actions."""

    def __init__(self, name: str = "RandomBot", rng: random.Random | None = None) -> None:
        super().__init__(name=name)
        # Optional custom RNG allows for reproducible bot decisions in testing.
        self._rng = rng if rng is not None else random.Random()

    def choose_white_action(
        self,
        sheet: ScoreSheet,
        roll: DiceRoll,
        valid_actions: list[Action],
        is_active: bool,
    ) -> Action:
        """Picks a random action from the list of valid white moves."""
        return self._rng.choice(valid_actions)

    def choose_color_action(
        self,
        sheet: ScoreSheet,
        roll: DiceRoll,
        valid_actions: list[Action],
    ) -> Action:
        """Picks a random action from the list of valid color moves."""
        return self._rng.choice(valid_actions)