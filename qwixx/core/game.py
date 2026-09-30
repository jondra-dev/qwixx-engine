"""qwixx.core.game

The core game loop and rules orchestrator. Coordinates turns, dice rolling, player decision dispatching, penalty 
assignments, and game-over condition detection."""

from dataclasses import dataclass, field
import random

from qwixx.core.action import (
    Action,
    MarkAction,
    PassAction,
    get_legal_color_actions,
    get_legal_white_actions,
)
from qwixx.core.dice import DiceRoll, DicePool
from qwixx.core.sheet import RowColor, ScoreSheet
from qwixx.players.base import Player


class QwixxGame:
    """Orchestrates a complete game of Qwixx among two or more players."""

    def __init__(
            self,
            players: list[Player],
            rng: random.Random | None = None,
    ) -> None:
        if len(players) < 2:
            raise ValueError("Qwixx requires at least 2 players.")

        self.players: list[Player] = players
        self.rng: random.Random | None = rng
        # Each player gets a score sheet
        self.sheets: dict[Player, ScoreSheet]
        self.dice_pool: DicePool
        self.active_index: int
        self.locked_rows: set[RowColor]

        # Initialize the mutable round state
        self.reset()

    def reset(self) -> None:
        """Resets the game state for a fresh match with the same players."""
        self.sheets = {p: ScoreSheet() for p in self.players}
        self.dice_pool = DicePool()
        self.active_index = 0
        self.locked_rows = set()

    @property
    def active_player(self) -> Player:
        """Returns the player whose turn it currently is to roll."""
        return self.players[self.active_index]

    @property
    def is_game_over(self) -> bool:
        """Game ends when any two rows are locked or any player has 4 penalties."""
        if len(self.locked_rows) >= 2:
            return True

        if any(sheet.penalties >= 4 for sheet in self.sheets.values()):
            return True

        return False
    def _apply_mark(self, player: Player, action: MarkAction) -> None:
        """Applies a mark to a player's sheet and synchronizes locks across the game."""
        sheet = self.sheets[player]
        locked = sheet.rows[action.color].mark(action.number)

        if locked: # If this mark closed a row
            self.locked_rows.add(action.color)
            self.dice_pool.remove_color(action.color)

            # Close this row externally for all other players
            for other_player, other_sheet in self.sheets.items():
                if other_player is not player:
                    other_sheet.external_lock_row(action.color)

    def play_turn(self) -> DiceRoll:
        """Executes one full turn cycle:

        1. Active player rolls.
        2. Phase 1: All players simultaneously choose white actions.
        3. Phase 2: Active player chooses color action.
        4. Apply penalty if active player marked nothing this turn.
        5. Advance active player index.
        """
        if self.is_game_over:
            raise RuntimeError("Cannot play turn; game is already over.")

        roll = self.dice_pool.roll(rng=self.rng)
        active_p = self.active_player
        active_made_mark = False

        # --- Phase 1: The White Dice Sum (all players) ---
        for player in self.players:
            sheet = self.sheets[player]
            valid_actions: list[Action] = get_legal_white_actions(sheet, roll)
            is_active = player is active_p

            chosen_action = player.choose_white_action(
                sheet=sheet,
                roll=roll,
                valid_actions=valid_actions,
                is_active=is_active,
            )

            # Defensive verification: force players to obey rules
            if chosen_action not in valid_actions:
                chosen_action = PassAction() # any invalid moves (cheats?) are treated as a pass

            if isinstance(chosen_action, MarkAction):
                self._apply_mark(player, chosen_action)
                if is_active:
                    active_made_mark = True

        # --- Phase 2: Color Combinations (Active Player only) ---
        active_sheet = self.sheets[active_p]
        valid_color_actions: list[Action] = get_legal_color_actions(active_sheet, roll)

        chosen_color_action = active_p.choose_color_action(
            sheet=active_sheet,
            roll=roll,
            valid_actions=valid_color_actions,
        )

        if chosen_color_action not in valid_color_actions:
            chosen_color_action = PassAction()

        if isinstance(chosen_color_action, MarkAction):
            self._apply_mark(active_p, chosen_color_action)
            active_made_mark = True

        # --- Penalty Check for Active Player ---
        if not active_made_mark:
            active_sheet.add_penalty()

        # Advance to the next player
        self.active_index = (self.active_index + 1) % len(self.players)
        return roll

    def play_game(self) -> dict[Player, int]:
        """Runs turn cycles until the game is over and returns final scores."""
        while not self.is_game_over:
            self.play_turn()

        return {p: self.sheets[p].total_score() for p in self.players}