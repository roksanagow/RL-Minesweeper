# backend/game.py

from .board import MinesweeperBoard

class GameSession:
    """
    A wrapper around MinesweeperBoard that manages game state and turn flow.
    """

    def __init__(self, width: int, height: int, num_mines: int, seed: int = None, custom_mask: list[tuple[int, int]] | None = None):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.seed = seed
        self.custom_mask = custom_mask

        self.reset()

    def step(self, action: str, row: int, col: int) -> dict:
        """
        Apply an action ("reveal" or "flag") at position (row, col).
        Returns a dict describing the game state after the action.
        """
        if self.game_over:
            return self.get_state()

        if action == "reveal":
            hit_mine = self.board.reveal(row, col)
            if hit_mine:
                self.game_over = True
                self.won = False
            elif self.board.is_complete():
                self.game_over = True
                self.won = True

        elif action == "flag":
            self.board.flag(row, col)

        self.moves_made += 1
        return self.get_state()

    def get_state(self) -> dict:
        """
        Return the current visible board and game status.
        """
        return {
            "board": self.board.get_visible_state(game_over_flag=self.game_over, game_won_flag=self.won),
            "game_over": self.game_over,
            "won": self.won,
            "moves_made": self.moves_made,
            "dimensions": (self.height, self.width),
            "num_mines": self.num_mines
        }

    def reset(self):
        """
        Reset the game session to a fresh state with the same parameters.
        """
        self.board = MinesweeperBoard(self.width, self.height, self.num_mines, self.seed, self.custom_mask)
        self.game_over = False
        self.won = False
        self.moves_made = 0

    def is_game_over(self) -> bool:
        return self.game_over

    def is_win(self) -> bool:
        return self.won

    def get_score(self) -> float:
        """
        Compute a basic score based on how much of the board is revealed.
        Could be used to give intermediate rewards to agents.
        """
        revealed_count = sum(
            1 for r in range(self.height) for c in range(self.width)
            if self.board.is_revealed(r, c)
        )
        return revealed_count / (self.height * self.width)

    def reveal_full_board(self):
        """
        Return the complete board (including mines), useful for debugging or endgame state.
        """
        return self.board.board
