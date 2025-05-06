# evaluation/evaluate.py

import os
import json
import csv
import time
from typing import Type, Dict, List
from backend.game import GameSession
from models.base_agent import BaseAgent


def evaluate_agent(
    agent_class: Type[BaseAgent],
    num_episodes: int,
    width: int,
    height: int,
    num_mines: int,
    agent_config: Dict = None,
    verbose: bool = False,
    save_dir: str = None
):
    """
    Evaluate the agent and optionally log results and save replays.
    """
    os.makedirs(save_dir, exist_ok=True) if save_dir else None

    agent = agent_class(config=agent_config)
    summary = []
    replays = []

    wins = 0
    total_moves = 0

    for ep in range(1, num_episodes + 1):
        game = GameSession(width, height, num_mines)
        moves = 0
        replay = []

        while not game.is_game_over():
            state = game.get_state()
            action = agent.act(state)
            replay.append({
                "step": moves,
                "state": state,
                "action": action
            })
            game.step(*action)
            moves += 1

        won = game.is_win()
        score = game.get_score()
        summary.append({
            "episode": ep,
            "moves": moves,
            "won": won,
            "score": score
        })
        if save_dir:
            replays.append({
                "episode": ep,
                "won": won,
                "replay": replay
            })

        total_moves += moves
        wins += int(won)

        if verbose:
            print(f"Episode {ep}: {'WIN' if won else 'loss'} in {moves} moves (score: {score:.2f})")

    win_rate = wins / num_episodes
    avg_moves = total_moves / num_episodes
    print(f"\n{agent_class.__name__} - Win rate: {win_rate:.2%}, Avg moves: {avg_moves:.1f}")

    # Save logs
    if save_dir:
        timestamp = int(time.time())
        with open(f"{save_dir}/summary_{timestamp}.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["episode", "moves", "won", "score"])
            writer.writeheader()
            writer.writerows(summary)

        with open(f"{save_dir}/replays_{timestamp}.json", "w") as f:
            json.dump(replays, f, indent=2)


def evaluate_multiple_difficulties(agent_class: Type[BaseAgent], agent_config: Dict = None):
    difficulties = [
        {"width": 8, "height": 8, "num_mines": 10, "label": "easy"},
        {"width": 16, "height": 16, "num_mines": 40, "label": "medium"},
        {"width": 30, "height": 16, "num_mines": 99, "label": "hard"},
    ]
    for setting in difficulties:
        print(f"\n== Difficulty: {setting['label']} ==")
        evaluate_agent(
            agent_class=agent_class,
            num_episodes=50,
            width=setting["width"],
            height=setting["height"],
            num_mines=setting["num_mines"],
            agent_config=agent_config,
            save_dir=f"evaluation/logs/{agent_class.__name__.lower()}_{setting['label']}",
            verbose=False
        )


if __name__ == "__main__":
    from models.random_agent.agent import RandomAgent

    evaluate_multiple_difficulties(RandomAgent)
