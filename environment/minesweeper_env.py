import gymnasium as gym
from gymnasium import spaces
from gymnasium.utils.env_checker import check_env
from backend.game import GameSession
import numpy as np
import pygame
from os import path
import os
import glob

class MinesweeperEnv(gym.Env):
    metadata = {"render_modes": ["human"], 'render_fps': 4}

    def __init__(self, board_size=(6, 6), num_mines=5, custom_mask=None, render_mode=None, seed=None, fps=None):
        super().__init__()
        self.board_width, self.board_height = board_size
        self.num_mines = num_mines
        self.render_mode = render_mode

        self.fps = fps if fps is not None else self.metadata['render_fps']

        self.game = GameSession(
            width=self.board_width,
            height=self.board_height,
            num_mines=self.num_mines,
            custom_mask=custom_mask,
            seed=seed
        )

        self.action_space = spaces.MultiDiscrete([self.board_width, self.board_height, 2])
        
        """
            Board values:
            -3 for unrevealed cells
            0-8 for no. of adjacent mines in revealed cells
            -1 for mines (when revealed)
            -2 for flagged cells
        """
        
        self.observation_space = spaces.Dict({
            "board": spaces.Box(low=-3, high=8, shape=(self.board_height, self.board_width), dtype=int),
            "visibility_mask": spaces.Box(low=-1, high=1, shape=(8, 2), dtype=int),
            "num_mines": spaces.Discrete(self.num_mines + 1),
            "game_over": spaces.Discrete(2)
        })

        self.max_possible_moves = self.board_width * self.board_height - self.num_mines
        self.step_efficiency_bonus = 0.1
        self.R_win = 1.0
        self.R_mine_hit = -1.0
        self.R_safe_reveal = 0.1
        self.step_penalty = -0.01
        self.moves_taken = 0
        self._episode_count = 0

        if self.render_mode == "human":
            self._init_pygame()

    def _init_pygame(self):
        pygame.init()
        pygame.display.init()
        pygame.display.set_caption("Minesweeper")
        self.cell_size = (40, 40)
        self.screen = pygame.display.set_mode((self.board_width * 40, self.board_height * 40))
        self.clock = pygame.time.Clock()
        
        # Create a dictionary to store all sprite images
        self.sprites = {}
        
        # Get path to the sprites directory
        sprites_dir = path.join(path.dirname(__file__), "sprites")
        
        # Find all PNG files in the sprites directory
        png_files = glob.glob(path.join(sprites_dir, "*.png"))
        
        # Load each sprite and scale it to cell size
        for png_file in png_files:
            # Extract the filename without extension to use as the key
            filename = path.basename(png_file)
            sprite_name = path.splitext(filename)[0]
            
            # Load and scale the image
            img = pygame.image.load(png_file)
            scaled_img = pygame.transform.scale(img, self.cell_size)
            
            # Store in the sprites dictionary
            self.sprites[sprite_name] = scaled_img

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.game.reset()
        self.moves_taken = 0
        self._episode_count += 1 # Increment episode count

        if self.render_mode == "human":
            self._frame_count = 0

        obs = {
            "board": self.get_encoded_board(),
            "visibility_mask": np.array(self.game.custom_mask),
            "num_mines": self.game.get_state()["num_mines"],
            "game_over": int(self.game.get_state()["game_over"])
        }

        info = {"episode": self._episode_count} # Add episode to info
        if self.render_mode == "human":
            info['frame'] = self._frame_count # Add frame to info if rendering
            self.render()
        return obs, info
    
    def step(self, action):
        col, row = action[0:2]
        action_type = action[2]
        action_str = "reveal" if action_type == 0 else "flag"
        result = self.game.step(action_str, row, col)
        if action_str == "reveal":
            self.moves_taken += 1

        obs = {
            "board": self.get_encoded_board(),
            "visibility_mask": np.array(self.game.custom_mask),
            "num_mines": result["num_mines"],
            "game_over": int(result["game_over"])
        }

        terminated = bool(obs["game_over"]) # Initial termination status from win/mine_hit

        game_state_for_reward = ""
        if terminated:
            if result["won"]:
                game_state_for_reward = "win"
            else:
                game_state_for_reward = "mine_hit"
        else:
            encoded_board = obs["board"]
            if not np.any(encoded_board == -3):
                # All cells are revealed or flagged. Since not a win/mine_hit yet, only move is unflagging which is considered non-ideal
                terminated = True
                obs["game_over"] = 1
                game_state_for_reward = "all_touched_not_won"
            elif action_type == 0:
                game_state_for_reward = "safe_reveal"
            else:
                game_state_for_reward = "flag_action"
        
        reward = self.calculate_reward(game_state_for_reward)

        info = {} # Initialize info for the step
        if self.render_mode == "human":
            info['frame'] = self._frame_count # Add frame to info if rendering
            self.render()
            
        return obs, reward, terminated, False, info

    def render(self):
        for r in range(self.board_height):
            for c in range(self.board_width):
                board = self.game.get_state()["board"]
                cell_value = board[r][c]
                if cell_value is None:
                    sprite = self.sprites["cellup"]
                elif cell_value == "F":
                    sprite = self.sprites["cellflag"]
                elif cell_value == -1:
                    sprite = self.sprites["cellmine"]
                elif cell_value == "*":
                    sprite = self.sprites["blast"]
                elif cell_value == "X":
                    sprite = self.sprites["falsemine"]
                elif cell_value == "M":
                    sprite = self.sprites["cellmine"]
                else:
                    sprite = self.sprites["cell" + str(cell_value)]
                self.screen.blit(sprite, (c * 40, r * 40))
        pygame.display.flip()
        if not os.path.exists("frames"):
            os.makedirs("frames")
        frame_count = getattr(self, '_frame_count', 0) # Keep track of frames
        pygame.image.save(self.screen, f"frames/episode_{self._episode_count:03d}_frame_{frame_count:04d}.png")
        self._frame_count = frame_count + 1
        self.clock.tick(self.fps)  

        return None

    def get_encoded_board(self):
        """
        Encode the board state into a format suitable for the observation space.
        """
        board = self.game.get_state()["board"]
        encoded_board = []

        for row in board:
            encoded_row = []
            for cell in row:
                if cell is None:
                    encoded_row.append(-3)  # Unrevealed
                elif cell == "F":
                    encoded_row.append(-2)  # Flagged
                else:
                    encoded_row.append(cell)  # Revealed number or mine
            encoded_board.append(encoded_row)

        return np.array(encoded_board)

    def is_valid_action(self, action):
        """
        Check if the action is valid (not flagged or revealed).
        Agent cannot unflag or reveal a flagged or revealed cell.
        """
        col, row = action[0:2]
        if self.game.board.is_flagged(row, col) or self.game.board.is_revealed(row, col):
            return False
        return True
    
    def calculate_reward(self, game_state):
        if game_state == "win":
            # Reward for winning, scaled by efficiency (fewer moves = higher reward)
            efficiency_bonus = (self.max_possible_moves - self.moves_taken) * self.step_efficiency_bonus
            return self.R_win + efficiency_bonus
        elif game_state == "mine_hit":
            # Penalty for hitting a mine
            return self.R_mine_hit
        elif game_state == "all_touched_not_won": # all cells acted upon, but not a win
            return -1.0 # same as losing
        elif game_state == "safe_reveal":
            # Small reward for safe reveal + penalty for each step to encourage efficiency
            return self.R_safe_reveal + self.step_penalty
        else: # e.g. for a flag action ("flag_action") that doesn't end the game
            return 0
    
    def get_valid_action(self):
        """
        Get a valid action from the action space.
        This is used to sample actions that are not flagged or revealed.
        """
        action = self.action_space.sample()
        while not self.is_valid_action(action):
            action = self.action_space.sample()
        return action

if __name__ == "__main__":
    env = gym.make("Minesweeper-v0", render_mode="human", seed=42, fps=10, num_mines=15, board_size=(20, 6))
    # print("Start environment check")
    # check_env(env.unwrapped)
    # print("Environment is valid!")
    
    # Example usage
    obs, info = env.reset()
    print("Initial Observation:", obs, info)
    terminated = False
    while True:
        action = env.unwrapped.get_valid_action()
        print("Action Sampled:", action)
        obs, reward, terminated, truncated, info = env.step(action)
        print("Step Result:", obs, reward, terminated, truncated, info)
        if terminated:
            obs, info = env.reset()
            print(obs, info)