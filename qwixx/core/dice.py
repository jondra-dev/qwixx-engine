"""
qwixx.core.dice

Models individual dice rolls and the game dice pool, handling roll generation, die removal when rows lock,
and sum calculations."""

from dataclasses import dataclass, field
import random

# Import RowColor so our dice map directly to the valid scoresheet rows
from qwixx.core.sheet import RowColor


@dataclass(frozen=True)
class DiceRoll:
    """An immutable snapshot of a single roll of all active dice.
    
    frozen=True makes instances read-only and hashable, preventing accidental modification during turn evaluation."""

    white1: int
    white2: int
    colored_dice: dict[RowColor, int] = field(default_factory=dict)

    @property
    def white_sum(self) -> int:
        """The sum of both white dice (used by all players in Phase 1)."""
        return self.white1 + self.white2

    def color_combinations(self, color: RowColor) -> list[int]:
        """Returns the possible sums for a color using either white die.
        
        Active player may pair (white1 + color) or (white2 + color).
        If both white dice have the same value, duplicates are removed."""
        if color not in self.colored_dice:
            return []

        c_val = self.colored_dice[color]
        # Using dict.fromkeys preserves insertion order while deduplicating
        return list(dict.fromkeys([self.white1 + c_val, self.white2 + c_val]))


@dataclass
class DicePool:
    """Manages the active dice in play and handles rolling mechanics."""

    # Active colored dice still in play (initially all four colors)
    active_colors: set[RowColor] = field(
        default_factory=lambda: {
            RowColor.RED,
            RowColor.YELLOW,
            RowColor.GREEN,
            RowColor.BLUE,
        }
    )

    def remove_color(self, color: RowColor) -> None:
        """Permanently removes a colored die from play when its row is locked."""
        self.active_colors.discard(color)

    def roll(self, rng: random.Random | None = None) -> DiceRoll:
        """Rolls both white dice and all active colored dice. Returns a DiceRoll of the results.
        
        Accepts an optional random.Random instance for seeded simulation rolls."""
        roller 