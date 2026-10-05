"""
qwixx.players.human_player

Provides an interactive terminal interface for a human player, displaying the player's scoresheet
and acccepting valiudated move input via stdin.
"""

from qwixx.core.action import Action
from qwixx.core.dice import DiceRoll
from qwixx.core.sheet import Row, RowColor, ScoreSheet
from qwixx.players.base import Player

def format_row(row: Row) -> str:
    """Renders a single row with crossed-out marks, open numbers, and lock status."""
    items: list[str] = []
    for num in row.target_sequence:
        if num in row.marked_numbers:
            items.append(" X")
        else:
            items.append(f"{num:>2}")

    lock_sym = "[LOCKED]" if row.is_locked else "       "
    return f"{row.color.value:<6} | {' '.join(items)} | Marks: {row.mark_count:>2} {lock_sym}"

def render_sheet(name: str, sheet: ScoreSheet) -> str:
    """Generates a complete multi-line terminal display of a scoresheet."""
    header = f"=== {name}'s Scoresheet ==="
    divider = "-" * len(header)
    rows_str = "\n".join(format_row(row) for row in sheet.rows.values())
    footer = f"Penalties: {sheet.penalties}/4 (-{sheet.penalties * 5} pts) | Total Score: {sheet.total_score()} pts"
    return f"\n{header}\n{rows_str}\n{divider}\n{footer}\n"


class HumanCLIPlayer(Player):
    """An interactive player that displays choices to stdout and reads from stdin."""

    def _prompt_action(
            self,
            phase_name: str,
            sheet: ScoreSheet,
            roll: DiceRoll,
            valid_actions: list[Action],
    ) -> Action:
        """Displays sheet, roll, and choices, prompting the user until a valid index is chosen."""

        print (render_sheet(self.name, sheet))
        print(f"[{phase_name}] Choose your action:")

        for idx, action in enumerate(valid_actions):
            print(f"  [{idx}] {action}")

        while True:
            raw_input = input(f"Select option (0-{len(valid_actions) - 1}): ").strip()
            if raw_input.isdigit():
                choice = int(raw_input)
                if 0 <= choice < len(valid_actions):
                    return valid_actions[choice]
            print(f"Invalid input. Please enter a number between 0 and {len(valid_actions) - 1}.")

    def choose_white_action(
            self,
            sheet: ScoreSheet,
            roll: DiceRoll,
            valid_actions: list[Action],
            is_active: bool,
    ) -> Action:
        role = "ACTIVE PLAYER" if is_active else "PASSIVE PLAYER"
        return self._prompt_action(f"Phase 1 (White Sum: {roll.white_sum}) - {role}", sheet, roll, valid_actions)

    def choose_color_action(
            self,
            sheet: ScoreSheet,
            roll: DiceRoll,
            valid_actions: list[Action],
    ) -> Action:
        return self._prompt_action(f"Phase 2 (Colored Combination)", sheet, roll, valid_actions)