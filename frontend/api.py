# frontend/api.py

from flask import Blueprint, request, jsonify
from backend.game import GameSession

api_blueprint = Blueprint("api", __name__)

# Global session (for now – can be improved later with user/session IDs)
game = GameSession(width=8, height=8, num_mines=10)


@api_blueprint.route("/new_game", methods=["POST"])
def new_game():
    global game
    game.reset()
    return jsonify(game.get_state())


@api_blueprint.route("/step", methods=["POST"])
def step():
    data = request.json
    action = data.get("action")
    row = data.get("row")
    col = data.get("col")

    if action not in {"reveal", "flag"} or row is None or col is None:
        return jsonify({"error": "Invalid input"}), 400

    result = game.step(action, row, col)
    return jsonify(result)


@api_blueprint.route("/state", methods=["GET"])
def get_state():
    return jsonify(game.get_state())

# frontend/api.py (add below other endpoints)

from models.random_agent.agent import RandomAgent
# Future: from models.your_agent.agent import YourAgent

AGENT_REGISTRY = {
    "random": RandomAgent,
    # "your_agent_name": YourAgent,
}

@api_blueprint.route("/play_agent", methods=["POST"])

def play_agent():
    global game
    game.reset()

    data = request.json
    agent_type = data.get("agent", "random").lower()
    agent_cls = AGENT_REGISTRY.get(agent_type, RandomAgent)

    agent = agent_cls()
    frames = []

    while not game.is_game_over():
        state = game.get_state()
        action = agent.act(state)
        game.step(*action)
        frames.append({
            "state": game.get_state(),
            "action": {
                "type": action[0],
                "row": action[1],
                "col": action[2]
            }
        })

    return jsonify({
        "frames": frames,
        "final": game.get_state()
    })
