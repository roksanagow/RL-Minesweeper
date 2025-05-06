# models/random_agent/agent.py

import random
from typing import Dict, Tuple
from models.base_agent import BaseAgent

class RandomAgent(BaseAgent):
    """
    A simple baseline agent that randomly chooses a valid unrevealed cell
    and selects either 'reveal' or 'flag' (randomly).
    """

    def __init__(self, config=None):
        super().__init__(config)
        self.prefer_reveal = self.config.get("prefer_reveal", True)

    def act(self, observation: Dict) -> Tuple[str, int, int]:
        board = observation["board"]
        height = len(board)
        width = len(board[0]) if board else 0

        # Find all unrevealed and unflagged tiles
        candidates = []
        for r in range(height):
            for c in range(width):
                cell = board[r][c]
                if cell is None or cell == "F":
                    if cell is None:
                        candidates.append((r, c))

        if not candidates:
            return ("reveal", 0, 0)  # fallback

        row, col = random.choice(candidates)

        action = "reveal" if self.prefer_reveal else random.choice(["reveal", "flag"])
        return (action, row, col)
