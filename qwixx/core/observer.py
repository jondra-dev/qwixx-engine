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

ANSI_RESET: str = "\033[0m"
ANSI_BOLD: str = "\033[1m"
ANSI_WHITE: str = "\033[97m" # Bright White for the two white dice

# Moves cursor to top-left (\033[H) and clears the visible viewport (\033[2J)
# so the new turn header always sits cleanly at the top of the terminal.
ANSI_CLEAR_VIEWPORT: str = "\033[2J\033[H"

ROW_ANSI_COLORS: dict[RowColor, str] = {
    RowColor.RED: "\033[91m",   # Bright Red
    RowColor.YELLOW: "\033[93m",  # Bright Yellow
    RowColor.GREEN: "\033[92m",  # Bright Green
    RowColor.BLUE: "\033[94m",   # Bright Blue
}

# Maps each die face (1-6) to its 3 internal 7-character rows (top, middle, bottom).
# Note: You can swap '●' for 'o' or '*' if your terminal font doesn't have the dot glyph. 
# COPIED FROM AI (GEMINI)
DICE_PIPS: dict[int, tuple[str, str, str]] = {
    1: ("       ", "   ●   ", "       "),
    2: (" ●     ", "       ", "     ● "),
    3: (" ●     ", "   ●   ", "     ● "),
    4: (" ●   ● ", "       ", " ●   ● "),
    5: (" ●   ● ", "   ●   ", " ●   ● "),
    6: (" ●   ● ", " ●   ● ", " ●   ● "),
}

def build_die_lines(value: int, color_code: str, label: str) -> list[str]:
    """Constructs a 6-line vertical slice representing a single colored ASCII die."""
    top_pips, mid_pips, bot_pips = DICE_PIPS[value]

    # Each box is 9 chars wide (1 border + 7 interior + 1 border)
    lines: list[str] = [
        f"{color_code}┌───────┐{ANSI_RESET}", # Top border
        f"{color_code}│{ANSI_BOLD}{top_pips}{ANSI_RESET}{color_code}│{ANSI_RESET}", # Top pips
        f"{color_code}│{ANSI_BOLD}{mid_pips}{ANSI_RESET}{color_code}│{ANSI_RESET}", # Middle pips
        f"{color_code}│{ANSI_BOLD}{bot_pips}{ANSI_RESET}{color_code}│{ANSI_RESET}", # Bottom pips
        f"{color_code}└───────┘{ANSI_RESET}", # Bottom border
        f"{color_code}{label:^9}{ANSI_RESET}", # Centered label
    ]
    return lines

def format_dice_roll(roll: DiceRoll) -> str:
    """Stitches all rolled dice horizontally into a single multi-line string."""
    # Each element in dice_blocks is the 6-line list[str] for one die
    dice_blocks: list[list[str]] = [
        build_die_lines(roll.white1, ANSI_WHITE, "WHITE 1"),
        build_die_lines(roll.white2, ANSI_WHITE, "WHITE 2"),
    ]

    # Iterate through RowColor in standard order so the dice don't jump around
    # (since DiePool stores active colors in an unordered set)
    for color in RowColor:
        if color in roll.colored_dice: # Since not all colored dice may be rolled
            die_val: int = roll.colored_dice[color]
            ansi_color: str = ROW_ANSI_COLORS[color]
            dice_blocks.append(build_die_lines(die_val, ansi_color, color.value.upper()))

    # Stitch horizontally: join line 0 of every die, then line 1, up to 5
    num_lines: int = len(dice_blocks[0]) # Should always be 6
    combined_rows: list[str] = []

    for line_idx in range(num_lines):
        row_segments: list[str] = [die[line_idx] for die in dice_blocks]
        combined_rows.append("  ".join(row_segments)) # Two spaces between dice

    return "\n".join(combined_rows)


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
        # Clear viewport and jump to top left so "===..." is always line 1
        print(f"{ANSI_CLEAR_VIEWPORT}{'=' * 64}")
        print(f"--- Turn Start: {active_player.name} is rolling ---")

    def on_dice_rolled(self, roll: DiceRoll) -> None:
        print(format_dice_roll(roll))
        print(f"{ANSI_BOLD}White Sum: {roll.white_sum}{ANSI_RESET}")

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