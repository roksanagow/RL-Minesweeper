let currentState = null;

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("new-game-btn").addEventListener("click", startNewGame);
    startNewGame();
});

function startNewGame() {
    fetch("/api/new_game", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        currentState = data;
        renderBoard();
        updateStatus();
    });
}

document.getElementById("watch-agent-btn").addEventListener("click", playAgent);

function countFlaggedNeighbors(row, col) {
    let count = 0;
    const board = currentState.board;
    const height = board.length;
    const width = board[0].length;

    for (let dr = -1; dr <= 1; dr++) {
        for (let dc = -1; dc <= 1; dc++) {
            if (dr === 0 && dc === 0) continue;
            const nr = row + dr;
            const nc = col + dc;
            if (nr >= 0 && nr < height && nc >= 0 && nc < width) {
                if (board[nr][nc] === "F") count++;
            }
        }
    }
    return count;
}


function renderBoard() {
    const boardDiv = document.getElementById("board-container");
    boardDiv.innerHTML = "";

    const board = currentState.board;
    for (let r = 0; r < board.length; r++) {
        const rowDiv = document.createElement("div");
        rowDiv.className = "row";
        for (let c = 0; c < board[r].length; c++) {
            const cell = board[r][c];
            const cellBtn = document.createElement("button");
            cellBtn.className = "cell";
            cellBtn.dataset.row = r;
            cellBtn.dataset.col = c;

            if (cell === null) {
                cellBtn.textContent = "";
            } else if (cell === "F") {
                cellBtn.textContent = "🚩";
            } else {
                cellBtn.textContent = cell === 0 ? "" : cell;
                cellBtn.disabled = true;
                cellBtn.classList.add("revealed");

                // Optional: Add mass-reveal hint
                if (showHints && typeof cell === "number" && cell > 0) {
                    const flaggedCount = countFlaggedNeighbors(r, c);
                    if (flaggedCount === cell) {
                        cellBtn.classList.add("mass-reveal-hint");
                    }
                }
                
            }

            cellBtn.addEventListener("click", handleReveal);
            cellBtn.addEventListener("contextmenu", handleFlag); // Right-click to flag
            rowDiv.appendChild(cellBtn);
        }
        boardDiv.appendChild(rowDiv);
    }
}

function handleReveal(event) {
    const row = event.target.dataset.row;
    const col = event.target.dataset.col;

    fetch("/api/step", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "reveal", row: parseInt(row), col: parseInt(col) })
    })
    .then(res => res.json())
    .then(data => {
        currentState = data;
        renderBoard();
        updateStatus();
    });
}

function handleFlag(event) {
    event.preventDefault();  // prevent context menu
    const row = event.target.dataset.row;
    const col = event.target.dataset.col;

    fetch("/api/step", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "flag", row: parseInt(row), col: parseInt(col) })
    })
    .then(res => res.json())
    .then(data => {
        currentState = data;
        renderBoard();
        updateStatus();
    });
}

function updateStatus() {
    const statusDiv = document.getElementById("game-status");
    if (currentState.game_over) {
        statusDiv.textContent = currentState.won ? "🎉 You win!" : "💥 You hit a mine!";
    } else {
        statusDiv.textContent = "Game in progress...";
    }
}

function playAgent() {
    const selectedAgent = document.getElementById("agent-select").value;

    fetch("/api/play_agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent: selectedAgent })
    })
    .then(res => res.json())
    .then(data => {
        let frames = data.frames;
        let finalState = data.final;

        let i = 0;
        function nextFrame() {
            if (i < frames.length) {
                currentState = frames[i].state;
                renderBoard();
                updateStatus();
                i++;
                setTimeout(nextFrame, 300); // delay between moves
            } else {
                currentState = finalState;
                renderBoard();
                updateStatus();
            }
        }
        nextFrame();
    });
}

function handleReveal(event) {
    const row = parseInt(event.target.dataset.row);
    const col = parseInt(event.target.dataset.col);
    const cell = currentState.board[row][col];

    // If already revealed and has a number — treat this as a mass reveal attempt
    const isRevealed = event.target.classList.contains("revealed");
    const isNumber = cell !== null && typeof cell === "number" && cell > 0;

    const action = "reveal";  // backend will decide what to do

    fetch("/api/step", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, row, col })
    })
    .then(res => res.json())
    .then(data => {
        currentState = data;
        renderBoard();
        updateStatus();
    });
}
