"""Unit tests for the Player interface and RandomPlayer behavior."""

import random
from qwixx.core.action import MarkAction, PassAction
from qwixx.core.dice import DiceRoll
from qwixx.core.sheet import RowColor, ScoreSheet
from qwixx.players.random_player import RandomPlayer


def test_random_player_picks_valid_white_action() -> None:
    # Seeded RNG for predictable testing
    rng = random.Random(1337)
    bot = RandomPlayer(name="TestBot", rng=rng)

    sheet = ScoreSheet()
    roll = DiceRoll(white1=2, white2=3)  # White sum = 5
    valid_actions: list[MarkAction | PassAction] = [
        PassAction(),
        MarkAction(RowColor.RED, 5),
        MarkAction(RowColor.YELLOW, 5),
    ]

    action = bot.choose_white_action(sheet, roll, valid_actions, is_active=True)

    # Bot must pick strictly from the provided list (a very simple test)
    assert action in valid_actions


def test_random_player_picks_valid_color_action() -> None:
    rng = random.Random(42)
    bot = RandomPlayer(name="TestBot", rng=rng)

    sheet = ScoreSheet()
    roll = DiceRoll(
        white1=1,
        white2=4,
        colored_dice={RowColor.BLUE: 3},
    )  # Blue combinations: 1+3=4, 4+3=7
    valid_actions: list[MarkAction | PassAction] = [
        PassAction(),
        MarkAction(RowColor.BLUE, 4),
        MarkAction(RowColor.BLUE, 7),
    ]

    # Same thing but for color actions. We provide a list of valid actions, the bot must pick one of them.
    action = bot.choose_color_action(sheet, roll, valid_actions)
    assert action in valid_actions