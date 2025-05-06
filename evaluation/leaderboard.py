# evaluation/leaderboard.py

import os
import csv
from collections import defaultdict
from glob import glob


def load_summary_csv(path: str):
    data = []
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                "won": row["won"].lower() == "true",
                "moves": int(row["moves"]),
                "score": float(row.get("score", 0.0))
            })
    return data


def summarize_agent_logs(log_dir: str):
    leaderboard = defaultdict(lambda: {"wins": 0, "games": 0, "total_moves": 0, "total_score": 0.0})

    for csv_file in glob(os.path.join(log_dir, "**", "summary_*.csv"), recursive=True):
        agent_name = csv_file.split("/")[-2]
        difficulty = agent_name.split("_")[-1]
        agent_base = "_".join(agent_name.split("_")[:-1])

        key = (agent_base, difficulty)
        data = load_summary_csv(csv_file)
        for row in data:
            leaderboard[key]["games"] += 1
            leaderboard[key]["total_moves"] += row["moves"]
            leaderboard[key]["total_score"] += row["score"]
            if row["won"]:
                leaderboard[key]["wins"] += 1

    return leaderboard


def display_leaderboard(leaderboard):
    print("\n🏆 Minesweeper AI Leaderboard\n")
    header = f"{'Agent':<20} {'Difficulty':<10} {'Win Rate':<10} {'Avg Moves':<12} {'Avg Score'}"
    print(header)
    print("-" * len(header))

    for (agent, diff), stats in sorted(leaderboard.items()):
        win_rate = stats["wins"] / stats["games"] if stats["games"] else 0
        avg_moves = stats["total_moves"] / stats["games"] if stats["games"] else 0
        avg_score = stats["total_score"] / stats["games"] if stats["games"] else 0
        print(f"{agent:<20} {diff:<10} {win_rate:.2%}    {avg_moves:<12.1f} {avg_score:.2f}")


def export_leaderboard_csv(leaderboard, path="leaderboard.csv"):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Agent", "Difficulty", "Win Rate", "Avg Moves", "Avg Score"])
        for (agent, diff), stats in sorted(leaderboard.items()):
            games = stats["games"]
            win_rate = stats["wins"] / games if games else 0
            avg_moves = stats["total_moves"] / games if games else 0
            avg_score = stats["total_score"] / games if games else 0
            writer.writerow([agent, diff, f"{win_rate:.2%}", f"{avg_moves:.1f}", f"{avg_score:.2f}"])


def export_leaderboard_markdown(leaderboard, path="leaderboard.md"):
    with open(path, "w") as f:
        f.write("## 🏆 Minesweeper AI Leaderboard\n\n")
        f.write("| Agent | Difficulty | Win Rate | Avg Moves | Avg Score |\n")
        f.write("|-------|------------|----------|------------|-----------|\n")
        for (agent, diff), stats in sorted(leaderboard.items()):
            games = stats["games"]
            win_rate = stats["wins"] / games if games else 0
            avg_moves = stats["total_moves"] / games if games else 0
            avg_score = stats["total_score"] / games if games else 0
            f.write(f"| {agent} | {diff} | {win_rate:.2%} | {avg_moves:.1f} | {avg_score:.2f} |\n")


if __name__ == "__main__":
    leaderboard = summarize_agent_logs("evaluation/logs")
    display_leaderboard(leaderboard)
    export_leaderboard_csv(leaderboard)
    export_leaderboard_markdown(leaderboard)
    print("\nLeaderboard saved as CSV and Markdown.")


# automatically update the project’s main README.md with the latest leaderboard content 