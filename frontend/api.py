# frontend/api.py

from flask import Blueprint, request, jsonify
from backend.game import GameSession

api_blueprint = Blueprint("api", __name__)

game = None


@api_blueprint.route("/new_game", methods=["POST"])
def new_game():
    global game
    data = request.json
    width = data.get("width", 8)
    height = data.get("height", 8)
    num_mines = data.get("num_mines", 10)
    custom_mask = data.get("custom_mask", None)
    # print(f"New game request with mask: {custom_mask}") # Debugging

    # Global session (for now – can be improved later with user/session IDs)
    game = GameSession(width=width, height=height, num_mines=num_mines, custom_mask=custom_mask)
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

from models.random_agent.agent import RandomAgent
# Future: from models.your_agent.agent import YourAgent

AGENT_REGISTRY = {
    "random": RandomAgent,
    # "your_agent_name": YourAgent,
}
@api_blueprint.route("/play_agent", methods=["POST"])
def play_agent():
    global game
    data = request.json
    agent_type = data.get("agent", "random").lower()
    agent_cls = AGENT_REGISTRY.get(agent_type, RandomAgent)

    width = data.get("width")
    height = data.get("height")
    num_mines = data.get("num_mines")
    custom_mask = data.get("custom_mask", None)

    # print(f"Agent play request with mask: {custom_mask}") # Debugging

    if game is None or \
       (width is not None and game.width != width) or \
       (height is not None and game.height != height) or \
       (num_mines is not None and game.num_mines != num_mines) or \
       (custom_mask != game.custom_mask):
        current_width = width if width is not None else (game.width if game else 8)
        current_height = height if height is not None else (game.height if game else 8)
        current_num_mines = num_mines if num_mines is not None else (game.num_mines if game else 10)
        game = GameSession(width=current_width, height=current_height, num_mines=current_num_mines, custom_mask=custom_mask)
    else:
        game.reset()  # Reset with existing dimensions and mask if no new ones are provided

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
