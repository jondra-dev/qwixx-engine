"""simulate.py

Quick runner script to simulate multiple headless matches between bots."""

from qwixx.core.game import QwixxGame
from qwixx.players.random_player import RandomPlayer


def main() -> None:
    # Set up two random bot instances (unseeded so rolls are natural)
    alice = RandomPlayer("Alice")
    bob = RandomPlayer("Bob")

    game = QwixxGame(players=[alice, bob])

    print("Running 5 simulated games:\n" + "-" * 55)

    for match in range(1, 6):
        game.reset()
        scores = game.play_game()

        # Determine the winner
        winner = max(scores, key=scores.get) # type: ignore[arg-type]
        print(
            f"Game {match:2d} | "
            f"Alice: {scores[alice]:3d} pts | "
            f"Bob: {scores[bob]:3d} pts | "
            f"Winner: {winner.name}"
        )

if __name__ == "__main__":
    main()