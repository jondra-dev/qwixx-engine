"""simulate.py

Quick runner script to execute headless simulations or observe games in the terminal."""

from random import shuffle
import sys

from qwixx.core.game import QwixxGame
from qwixx.players.random_player import RandomPlayer
from qwixx.core.observer import ConsoleObserver
from qwixx.players.human_player import HumanCLIPlayer

def run_headless_batch(games_to_play: int = 5) -> None:
    """Simulate games silently and prints the score summary."""
    alice = RandomPlayer("Alice")
    bob = RandomPlayer("Bob")
    game = QwixxGame(players=[alice, bob])

    print (f"\nRunning {games_to_play} simulated games:\n" + "-" * 55)

    for match in range(1, games_to_play + 1):
        game.reset()
        scores = game.play_game()
        winner = max(scores, key=scores.get) # type: ignore[arg-type]
        print(
            f"Game: {match:2d} | "
            f"Alice: {scores[alice]:3d} pts | "
            f"Bob: {scores[bob]:3d} pts | "
            f"Winner: {winner.name}"
        )
    print("-" * 55 + "\n")

def run_observed_match() -> None:
    """Plays a single game streaming every roll and action to stdout."""
    alice = RandomPlayer("Alice")
    bob = RandomPlayer("Bob")
    game = QwixxGame(players=[alice, bob], observers=[ConsoleObserver()])
    game.play_game()

def run_interactive_match() -> None:
    """Launches an interactive match between a human and RandomBot."""
    player_name = input("Enter your name: ").strip() or "Player"
    human = HumanCLIPlayer(player_name)
    bot = RandomPlayer("RandomBot")
    observer = ConsoleObserver()

    # Shuffle the player order and make the game
    players = [human, bot]
    shuffle(players)
    game = QwixxGame(players=players, observers=[observer])
    game.play_game()

def main() -> None:
    # Check if a choice is passed via terminal: python simulate.py 1
    choice = sys.argv[1] if len(sys.argv) > 1 else None

    if not choice:
        print("Select simulation mode:")
        print("  [1] Headless batch (5 games)")
        print("  [2] Observed match (1 game)")
        print("  [3] Play interactive game against RandomBot")
        choice = input("Enter choice: ").strip()

    if choice == "1":
        run_headless_batch(5)
    elif choice == "2":
        run_observed_match()
    elif choice == "3":
        run_interactive_match()
    else:
        print(f"Invalid choice: {choice}. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()


# Run this in py interpreter to see output of simulated game.

# from qwixx.core.game import QwixxGame
# from qwixx.players.random_player import RandomPlayer
# from qwixx.core.observer import ConsoleObserver

# alice = RandomPlayer("Alice")
# bob = RandomPlayer("Bob")
# game = QwixxGame(players=[alice, bob], observers=[ConsoleObserver()])
# game.play_game()