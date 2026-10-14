"""
qwixx.players.human_player

Provides an interactive terminal interface for a human player, displaying the player's scoresheet
and acccepting valiudated move input via stdin.
"""

from qwixx.core.action import Action
from qwixx.core.dice import DiceRoll
from qwixx.core.sheet import Row, RowColor, ScoreSheet
from qwixx.players.base import Player

# ANSI escape sequences for terminal colors and text styles
ANSI_RESET: str = "\033[0m"
ANSI_BOLD: str = "\033[1m"
ANSI_DIM: str = "\033[2m"
ANSI_STRIKETHROUGH: str = "\033[9m"

ROW_ANSI_COLORS: dict[RowColor, str] = {
    RowColor.RED: "\033[91m",   # Bright Red
    RowColor.YELLOW: "\033[93m",  # Bright Yellow
    RowColor.GREEN: "\033[92m",  # Bright Green
    RowColor.BLUE: "\033[94m",   # Bright Blue
}

def format_row(row: Row) -> str:
    """Renders a single colorized row with marks, skipped dashes, and lock status."""
    color_code = ROW_ANSI_COLORS[row.color]
    seq = row.target_sequence

    # Find the index of the right-most mark (-1 if no marks yet)
    last_marked_idx: int = seq.index(row.marked_numbers[-1]) if row.marked_numbers else -1
    
    items: list[str] = []
    for idx, num in enumerate(row.target_sequence):
        if num in row.marked_numbers:
            # Marked numbers: Bold 'X' in the row's color
            items.append(f"{ANSI_BOLD}{color_code} X{ANSI_RESET}")
        elif idx < last_marked_idx or row.is_locked:
            # Skipped numbers (left of last mark) or locked out: Dimmed '-': items.append(f"{ANSI_DIM} -{ANSI_RESET}")
            # We'll use dimmed strikethrough numbers in the following:
            items.append(f"{ANSI_DIM}{ANSI_STRIKETHROUGH}{num:>2}{ANSI_RESET}")
        else:
            # Still open to be marked: Normal colored number
            items.append(f"{color_code}{num:>2}{ANSI_RESET}")

    lock_sym = f"{ANSI_BOLD}[LOCKED]{ANSI_RESET}" if row.is_locked else "       "
    row_label = f"{ANSI_BOLD}{color_code}{row.color.value.upper():<6}{ANSI_RESET}"
    
    return f"{row_label} | {' '.join(items)} | Marks: {row.mark_count:>2} {lock_sym}"

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
            valid_actions: list[Action],
    ) -> Action:
        """Displays sheet, and choices, prompting the user until a valid index is chosen."""

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
        return self._prompt_action(f"Phase 1 (White Sum: {roll.white_sum}) - {role}", sheet, valid_actions)

    def choose_color_action(
            self,
            sheet: ScoreSheet,
            roll: DiceRoll,
            valid_actions: list[Action],
    ) -> Action:
        return self._prompt_action(f"Phase 2 (Colored Combination)", sheet, valid_actions)