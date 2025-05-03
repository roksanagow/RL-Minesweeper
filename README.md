# 🧠 Minesweeper Reinforcement Learning Project

Welcome! This is a collaborative project to build a Minesweeper environment, train reinforcement learning (RL) agents, and explore how well AI can learn to solve this classic puzzle.

## 📐 Project Structure

```
minesweeper-rl/
├── backend/                 # Core game logic, board generation, game state
│   ├── __init__.py
│   ├── board.py             # MinesweeperBoard class: logic, reveal, flag, etc.
│   ├── game.py              # GameSession class: player actions, win/loss, resets
│   └── utils.py             # Helper functions (e.g., random board gen, display)

├── frontend/                # Local web interface (Flask + JS or full SPA)
│   ├── static/              # JS, CSS, images
│   ├── templates/           # HTML templates
│   ├── app.py               # Flask app (serves game + API for model interaction)
│   └── api.py               # Defines REST endpoints (e.g., /new_game, /step, /state)

├── models/                  # Folder for RL agents
│   ├── base_agent.py        # BaseAgent class (standard API: act(), observe(), train())
│   ├── your_model/          # Example custom agent
│   │   ├── agent.py         # YourAgent(BaseAgent)
│   │   └── config.yaml      # Any custom config
│   ├── ...others can add folders...
│   └── registry.py          # Auto-discovery / loading of available models

├── evaluation/              # Code for running and comparing models
│   ├── evaluate.py
│   ├── leaderboard.json     # Optional: shared results
│   └── visualizer.py        # For replay rendering, statistics, heatmaps

├── notebooks/               # Optional: for experimentation, debugging, analysis

├── config/                  # Game or training configs (YAML or JSON)
│   ├── game_config.yaml
│   └── training_config.yaml

├── tests/                   # Unit tests for backend, models
│   └── test_board.py

├── README.md
├── requirements.txt
└── setup.py                 # Optional: make it pip-installable as a package
```

---

## 🚦 Project Phases

### Phase 1: Build the Game (Collaborative)
- Core game logic
- Local web interface (Flask or other)
- API endpoints for agents and human play

### Phase 2: Train and Submit Models
- Add models in `models/your_model_name/`
- Inherit from `BaseAgent` to ensure compatibility
- Submit models for evaluation

---

## 🔧 BaseAgent API

```python
class BaseAgent:
    def __init__(self, config=None):
        ...

    def act(self, observation):
        """Return action given the current observation."""
        pass

    def observe(self, transition):
        """Optional: Store (s, a, r, s') tuples for learning."""
        pass

    def train(self):
        """Train the model on stored experiences (if applicable)."""
        pass
```

---

## 📋 Contributing

- Everyone contributes to the backend and frontend in Phase 1
- In Phase 2, fork the repo or add new agents in the `models/` directory
- Use PRs to share your models or improvements

---

## 📈 Evaluation

We will compare models based on:
- Win rate
- Efficiency (avg. moves per win)
- Generalization to new board sizes

Optionally, submit to a leaderboard.

---

## 📞 Questions or Ideas?
Open an issue or start a discussion! Let's build something cool together.

---

Ready to play Minesweeper with AI? Let’s go! 🚀
