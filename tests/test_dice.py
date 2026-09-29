"""Unit tests for dice rolling, combination calculation, and die removal."""

import random
from qwixx.core.dice import DicePool, DiceRoll
from qwixx.core.sheet import RowColor


def test_dice_roll_sums() -> None:
    # Construct a deterministic roll directly
    roll = DiceRoll(
        white1=2,
        white2=5,
        colored_dice={
            RowColor.RED: 4,
            RowColor.BLUE: 6,
        }
    )

    # White sum: 2 + 5 = 7
    assert roll.white_sum == 7

    # Red sums: 2 + 4 = 6, 5 + 4 = 9
    assert roll.color_combinations(RowColor.RED) == [6, 9]

    # Blue sums: 2 + 6 = 8, 5 + 6 = 11
    assert roll.color_combinations(RowColor.BLUE) == [8, 11]

    # Yellow was not rolled (locked/removed)
    assert roll.color_combinations(RowColor.YELLOW) == []


def test_dice_roll_deduplication() -> None:
    #If both white dice are identical, we should only get 1 combination per color
    roll = DiceRoll(
        white1=3,
        white2=3,
        colored_dice={
            RowColor.GREEN: 4,
        }
    )

    # Green sums: 3 + 4 = 7 (only one unique combination). Should NOT return [7, 7]
    assert roll.color_combinations(RowColor.GREEN) == [7]


def test_dice_pool_remove_color() -> None:
    pool = DicePool()
    assert RowColor.RED in pool.active_colors

    pool.remove_color(RowColor.RED)
    assert RowColor.RED not in pool.active_colors

    # Discarding a color already removed should not raise an error
    pool.remove_color(RowColor.RED)

    # Rolling should only roll the 3 remaining colors
    roll: DiceRoll = pool.roll()
    assert RowColor.RED not in roll.colored_dice
    assert len(roll.colored_dice) == 3


def test_seeded_reproducibility() -> None:
    pool = DicePool()
    rng1 = random.Random(42)
    rng2 = random.Random(42)

    roll1 = pool.roll(rng=rng1)
    roll2 = pool.roll(rng=rng2)

    assert roll1 == roll2  # Same seed should produce identical rolls