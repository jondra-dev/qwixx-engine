"""qwixx.players.base

Defines the abstract base class (interface) that every Qwixx player must satisfy,
whetehr they are a human CLI interface, a random bot, or a trained agent."""

# abc (Abstract Base Classes):
# - ABC: base class to inherit from to create an abstract class
# - abstractmethod: decorator enforcing that derived subclasses MUST implement the decorated method
from abc import ABC, abstractmethod

# Core domain inputs
from qwixx.core.action import Action
from qwixx.core.dice import DiceRoll
from qwixx.core.sheet import ScoreSheet


class Player(ABC):
    """Abstract base class representing an actor in a game of Qwixx."""
    
    def __init__(self, name: str) -> None:
        self.name: str = name

    def __repr__(self,) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"

    @abstractmethod
    def choose_white_action(
        self,
        sheet: ScoreSheet,
        roll: DiceRoll,
        valid_actions: list[Action],
        is_active: bool,
    ) -> Action:
        """Select an action during Phase 1 (The White Dice Sum).
        
        Args:
            sheet: A snapshot of this player's current score sheet.
            roll: The dice rolled for this turn.
            valid_actions: All legal moves available (always contains at least a PassAction.)
            is_active: True if this player rolled the dice this turn;
                       False if they are participating as a passive player.
        
        Returns:
            The chosen action, which must be one of the valid_actions.
        """
        pass

    @abstractmethod
    def choose_color_action(
        self,
        sheet: ScoreSheet,
        roll: DiceRoll,
        valid_actions: list[Action],
    ) -> Action:
        """Select an action during Phase 2 (White + Colored Combinations).

        Only called for the active player.

        Args:
            sheet: A snapshot of this player's current score sheet.
            roll: The dice rolled for this turn.
            valid_actions: All legal moves available (always contains at least a PassAction.)

        Returns:
            The chosen action, which must be one of the valid_actions.
        """
        pass