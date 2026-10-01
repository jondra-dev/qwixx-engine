"""
qwixx.core.observer

Defines the GameObserver interface and a default ConsoleObserver for printing 
real-time game events to the terminal.
"""

from abc import ABC
from qwixx.core.action import Action
from qwixx.core.dice import DiceRoll
from qwixx.core.sheet import RowColor
from qwixx.players.base import Player


class GameObserver(ABC):
    """Abstract listener that receives game lifecycle events."""

    def on_turn_start(self, active_player: Player) -> None:
        """Fired at the start of a turn before dice are rolled."""
        pass

    def on_dice_rolled(self, roll: DiceRoll) -> None:
        """Fired after the dice have been rolled."""
        pass

    def on_action_taken(self, player: Player, action: Action, phase: str ) -> None:
        """Fired whenever a player makes a mark or passes."""
        pass

    def on_penalty_assigned(self, player: Player, total_penalties: int) -> None:
        """Fired when the active player receives a penalty."""
        pass

    def on_row_locked(self, color: RowColor, locking_player: Player) -> None:
        """Fired when a row is officially locked."""
        pass

    def on_game_over(self, final_scores: dict[Player, int]) -> None:
        """Fired when the match concludes."""
        pass


class ConsoleObserver(GameObserver):
    """Prints game events to standard output in human-readable format."""

    def on_turn_start(self, active_player: Player) -> None:
        print(f"\n{'=' * 45}")
        print(f"--- Turn Start: {active_player.name} is rolling ---")

    def on_dice_rolled(self, roll: DiceRoll) -> None:
        colored_str = " | ".join(
            f"{color.value}: {value}" for color, value in roll.colored_dice.items()
        )
        print(f"Roll: White=[{roll.white1}, {roll.white2}] (Sum: {roll.white_sum}) | {colored_str}")

    def on_action_taken(self, player: Player, action: Action, phase: str) -> None:
        print(f"[{phase}] {player.name} -> {action}")

    def on_penalty_assigned(self, player: Player, total_penalties: int) -> None:
        print(f"*** PENALTY! {player.name} marked nothing this turn. (Total: {total_penalties}/4) ***")

    def on_row_locked(self, color: RowColor, locking_player: Player) -> None:
        print(f"*** ROW LOCKED! {locking_player.name} locked the {color.value} row. That die is removed.***")

    def on_game_over(self, final_scores: dict[Player, int]) -> None:
        print("\n" + "=" * 45)
        print("GAME OVER! Final Results:")
        for player, score in sorted(final_scores.items(), key=lambda item: item[1], reverse=True):
            print(f"  {player.name:<15}: {score:>3} pts")
        print("=" * 45 + "\n")