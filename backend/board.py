import random

class MinesweeperBoard:
    def __init__(self, width, height, num_mines, seed=None):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.seed = seed

        self.board = []         # -1 = mine, 0-8 = adjacent mine counts
        self.revealed = []      # bool grid
        self.flags = []         # bool grid

        self._init_board()

    def _init_board(self):
        if self.seed is not None:
            random.seed(self.seed)

        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.revealed = [[False for _ in range(self.width)] for _ in range(self.height)]
        self.flags = [[False for _ in range(self.width)] for _ in range(self.height)]

        self._place_mines()
        self._compute_adjacent_counts()

    def _place_mines(self):
        all_coords = [(r, c) for r in range(self.height) for c in range(self.width)]
        mine_coords = random.sample(all_coords, self.num_mines)

        for r, c in mine_coords:
            self.board[r][c] = -1

    def _compute_adjacent_counts(self):
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] == -1:
                    continue
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if self.is_valid_coord(nr, nc) and self.board[nr][nc] == -1:
                            count += 1
                self.board[r][c] = count

    def is_valid_coord(self, row, col):
        return 0 <= row < self.height and 0 <= col < self.width

    def reveal(self, row, col):
        if not self.is_valid_coord(row, col) or self.revealed[row][col] or self.flags[row][col]:
            return False

        self.revealed[row][col] = True
        if self.board[row][col] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = row + dr, col + dc
                    if (dr != 0 or dc != 0) and self.is_valid_coord(nr, nc):
                        self.reveal(nr, nc)
        return self.board[row][col] == -1

    def flag(self, row, col):
        if self.is_valid_coord(row, col) and not self.revealed[row][col]:
            self.flags[row][col] = not self.flags[row][col]

    def is_mine(self, row, col):
        return self.is_valid_coord(row, col) and self.board[row][col] == -1

    def is_revealed(self, row, col):
        return self.is_valid_coord(row, col) and self.revealed[row][col]

    def is_flagged(self, row, col):
        return self.is_valid_coord(row, col) and self.flags[row][col]

    def is_complete(self):
        for r in range(self.height):
            for c in range(self.width):
                if self.board[r][c] != -1 and not self.revealed[r][c]:
                    return False
        return True

    def get_visible_state(self, game_over_flag=False, game_won_flag=False):
        state = []
        for r in range(self.height):
            row_cells = []
            for c in range(self.width):
                is_mine_cell = (self.board[r][c] == -1)

                if game_over_flag:
                    if is_mine_cell:
                        if game_won_flag:
                            # Game won, all mines are effectively "flagged"
                            row_cells.append("F")
                        else: # Game lost
                            if self.revealed[r][c] and self.board[r][c] == -1: # This is the mine that was clicked
                                row_cells.append("*") # Exploded mine
                            elif self.flags[r][c]: # Correctly flagged mine
                                row_cells.append("F")
                            else: # Other unflagged, unrevealed mines
                                row_cells.append("M")
                    else: # Not a mine
                        if self.flags[r][c]: # Incorrectly flagged non-mine
                            row_cells.append("X")
                        elif self.revealed[r][c]:
                            row_cells.append(self.board[r][c])
                        else:
                            # Unrevealed non-mine cell in a game over state (loss)
                            # Show as None (still hidden) or could show its number
                            row_cells.append(None)
                else:
                    if self.flags[r][c]:
                        row_cells.append("F")
                    elif not self.revealed[r][c]:
                        row_cells.append(None)
                    else:
                        row_cells.append(self.board[r][c])
            state.append(row_cells)
        return state

    def print_debug_board(self):
        for r in range(self.height):
            row = ""
            for c in range(self.width):
                if self.board[r][c] == -1:
                    row += " * "
                else:
                    row += f" {self.board[r][c]} "
            print(row)

    def reveal(self, row: int, col: int) -> bool:
        if not self.is_valid_coord(row, col):
            return False

        # CASE 1: normal reveal (if not yet revealed)
        if not self.revealed[row][col] and not self.flags[row][col]:
            self.revealed[row][col] = True
            if self.board[row][col] == 0:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = row + dr, col + dc
                        if (dr != 0 or dc != 0) and self.is_valid_coord(nr, nc):
                            self.reveal(nr, nc)
            return self.board[row][col] == -1

        # CASE 2: mass reveal (if already revealed and is a number)
        if self.revealed[row][col] and self.board[row][col] > 0:
            # Count flagged neighbors
            flagged = 0
            to_reveal = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = row + dr, col + dc
                    if self.is_valid_coord(nr, nc):
                        if self.flags[nr][nc]:
                            flagged += 1
                        elif not self.revealed[nr][nc]:
                            to_reveal.append((nr, nc))
            
            # If the number of flags equals the cell's number, reveal remaining
            if flagged == self.board[row][col]:
                mine_hit = False
                for nr, nc in to_reveal:
                    if self.reveal(nr, nc):  # Recursive call
                        mine_hit = True
                return mine_hit
        return False
