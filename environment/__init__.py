from gymnasium.envs.registration import register
from .minesweeper_env import MinesweeperEnv

register(
    id='Minesweeper-v0',
    entry_point='environment.minesweeper_env:MinesweeperEnv',
)

__all__ = ['MinesweeperEnv']
