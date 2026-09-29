"""qwixx.core.action

Defines the discrete actions a player can take (marking a number or passing) and provides 
generator functiosn to determine all legal moves for a given roll."""

from dataclasses import dataclass

from qwixx.core.dice import DiceRoll
from qwixx.core.sheet import RowColor, ScoreSheet


@dataclass(frozen=True)
class PassAction:
    """Represents a player choosing to not mark any number during a phase.
    
    frozen=True makes it immutable and hashable."""

    def __repr__(self) -> str:
        return "Pass"


@dataclass(frozen=True)
class MarkAction:
    """Represents a player marking a specific number on a colored row."""

    color: RowColor
    number: int

    def __repr__(self) -> str:
        return f"Mark {self.color.value} {self.number}"

# Type alias: Any valid move in Qwixx is either a MarkAction or a PassAction.
# This gives us strict static typing across player decisions and AI algorithms.
Action = MarkAction | PassAction


def get_legal_white_actions(sheet: ScoreSheet, roll: DiceRoll) -> list[Action]:
    """Generates all legal actions for Phase 1 (The White Dice Sum). 
    
    All players (active and passive) simultaneously evaluate this sum.
    Passing is always a valid option in Phase 1."""
    legal_actions: list[Action] = [PassAction()]
    white_sum = roll.white_sum

    # Check each row to see if the white sum can be legally marked
    for color, row in sheet.rows.items():
        if row.can_mark(white_sum):
            legal_actions.append(MarkAction(color=color, number=white_sum))

    return legal_actions

def get_legal_color_actions(sheet: ScoreSheet, roll: DiceRoll) -> list[Action]:
    """Generates all legal actions for Phase 2 (White + Colored Combinations).
    
    Only the active player takes this phase. They may pair either white die with any active 
    colored die to mark that color's row. Passing is always an available choice."""
    legal_actions: list[Action] = [PassAction()]

    # Evaluate each colored die still in play
    for color in roll.colored_dice: 
        row = sheet.rows[color]
        # A roll may provide 1 or 2 distinct sums for this color
        possible_sums = roll.color_combinations(color)

        for combo_sum in possible_sums:
            if row.can_mark(combo_sum):
                legal_actions.append(MarkAction(color=color, number=combo_sum))

    return legal_actions