# models/base_agent.py

from typing import Any, Dict, Tuple

class BaseAgent:
    """
    Abstract base class for all Minesweeper RL agents.
    Provides a consistent interface for training and inference.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the agent with optional configuration.
        """
        self.config = config or {}

    def act(self, observation: Dict) -> Tuple[str, int, int]:
        """
        Decide on an action based on the current game observation.

        Returns:
            A tuple: (action_type, row, col), where
            - action_type: "reveal" or "flag"
            - row, col: coordinates of the selected cell
        """
        raise NotImplementedError("Agent must implement act().")

    def observe(self, transition: Dict[str, Any]):
        """
        Optional: record experience from environment (e.g., for replay buffer).

        transition example:
        {
            "state": ...,         # current observation
            "action": ("reveal", 3, 4),
            "reward": -1,
            "next_state": ...,
            "done": True
        }
        """
        pass  # Only needed for learning agents

    def train(self):
        """
        Optional: run one training step (e.g., from replay buffer).
        """
        pass

    def save(self, path: str):
        """
        Optional: save model state to disk.
        """
        pass

    def load(self, path: str):
        """
        Optional: load model state from disk.
        """
        pass
