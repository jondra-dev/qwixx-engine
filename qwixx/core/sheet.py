"""qwixx.core.sheet.

This module models the Qwixx scoresheet components, tracking marked numbers, row locking conditions,
penalties, and score calculations.
"""

# standard library imports:
# - Enum: creates strongly typed enumerations so we don't rely on raw strings
# - dataclass: automatically generates boilerplate like __init__, __repr__, and __eq__
# - field: allows initializing default values for mutable types (like an empty list)
from enum import Enum
from dataclasses import dataclass, field


class RowColor(Enum):
    """Represents the four colored scoring rows on a Qwixx scoresheet."""
    
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"

# In Qwixx, row scoring folows triangular numbers: T_n = n * (n + 1) // 2.
# 1 mark = 1 pt, 2 marks = 3 pts, etc., up to 12 marks = 78 pts.
# Pre-calculating this dictionary avoids recalculating triangular numbers repeatedly on every query.

ROW_SCORING_TABLE: dict[int, int] = {
    0: 0,
    1: 1,
    2: 3,
    3: 6,
    4: 10,
    5: 15,
    6: 21,
    7: 28,
    8: 36,
    9: 45,
    10: 55,
    11: 66,
    12: 78,
}

# Points subtracted for each failed turn penalty mark
PENALTY_VALUE: int = 5


# Official rule: A row must have at least 5 marks befoer a player can mark 
# the final number (12 or 2) and lock that row.
MIN_MARKS_TO_LOCK: int = 5


@dataclass
class Row:
    """Represents a single colored row on a player's Qwixx scoresheet.
    
    Enforces strict left-to-right number progression and locking rules.
    """

    color: RowColor
    ascending: bool # True for Red & Yellow (2 -> 12), False for Green & Blue (12 -> 2)
    marked_numbers: list[int] = field(default_factory=list)
    is_locked: bool = False

    @property
    def target_sequence(self) -> list[int]:
        """Returns the full sequence of numbers for this row in valid play order."""
        return list(range(2, 13)) if self.ascending else list(range(12, 1, -1))

    @property
    def lock_number(self) -> int:
        """The final number on the row that triggers a lock (12 or 2)."""
        return 12 if self.ascending else 2

    @property
    def mark_count(self) -> int:
        """Total marks counted toward scoring, including the lock bonus box."""
        # When a row locks, the player crosses the lock number AND gets an extra bonus mark on the lock symbol itself.
        return len(self.marked_numbers) + (1 if self.is_locked else 0)

    def can_mark(self, number: int) -> bool:
        """Validates whether a number can legally be marked in this row."""
        if self.is_locked:
            return False  # No further marks allowed if the row is locked
        if number not in self.target_sequence:
            return False  # Number is not part of this row's valid sequence

        # Monotonicity check: numbers must be marked strictly to the right of the last marked number
        if self.marked_numbers:
            last_marked = self.marked_numbers[-1]
            last_index = self.target_sequence.index(last_marked)
            candidate_index = self.target_sequence.index(number)
            if candidate_index <= last_index:
                return False  # Cannot mark a number to the left of the last marked number

        # Locking check: to mark the final number, the player must already ahve at least MIN_MARKS_TO_LOCK marks in this row
        if number == self.lock_number:
            if len(self.marked_numbers) < MIN_MARKS_TO_LOCK:
                return False  # Cannot mark the lock number without enough prior marks

        return True  # All checks passed; marking is valid

    def mark(self, number: int) -> bool:
        """Marks a number on this row.
        
        Returns True if this mark successfully locked the row. 
        Raises ValueError if the mark is invalid.
        """
        if not self.can_mark(number):
            raise ValueError(f"Cannot mark {number} in {self.color.value} row.")

        self.marked_numbers.append(number)

        # If marking the final number, lock the row
        if number == self.lock_number:
            self.is_locked = True
            return True # Row is now locked

        return False # Row is not locked yet

    def score(self) -> int:
        """Calculates the total points scored by this row."""
        # Cap count at 12 to safely match table bounds.
        count = min(self.mark_count, 12)
        return ROW_SCORING_TABLE[count]
