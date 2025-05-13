let currentState = null;
let showHints = false; // Initialize showHints
let currentCustomMask = null; // Variable to store the current custom mask

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("new-game-btn").addEventListener("click", startNewGame);
    const hintToggle = document.getElementById("show-hint-toggle");
    showHints = hintToggle.checked; // Initialize based on checkbox state
    hintToggle.addEventListener("change", () => {
        showHints = hintToggle.checked;
        renderBoard(); // Re-render board when hint visibility changes
    });

    initializeMaskGrid();
    document.getElementById("enable-custom-mask").addEventListener("change", toggleCustomMask);

    startNewGame(); // Initial game start
});

function getBoardConfig() {
    const width = parseInt(document.getElementById("board-width").value);
    const height = parseInt(document.getElementById("board-height").value);
    const numMines = parseInt(document.getElementById("num-mines").value);
    const enableMaskCheckbox = document.getElementById("enable-custom-mask");
    let customMask = null;
    if (enableMaskCheckbox.checked) {
        customMask = getCustomMaskFromGrid();
    }
    return { width, height, num_mines: numMines, custom_mask: customMask };
}

function startNewGame() {
    const config = getBoardConfig();
    currentCustomMask = config.custom_mask; // Store the mask used for the current game
    fetch("/api/new_game", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        currentState = data;
        renderBoard();
        updateStatus();
    });
}

document.getElementById("watch-agent-btn").addEventListener("click", playAgent);

function renderBoard() {
    const boardDiv = document.getElementById("board-container");
    boardDiv.innerHTML = "";

    const board = currentState.board;
    const activeMaskForHint = currentCustomMask; // Use the game's active mask

    for (let r = 0; r < board.length; r++) {
        const rowDiv = document.createElement("div");
        rowDiv.className = "row";
        for (let c = 0; c < board[r].length; c++) {
            const cellValue = board[r][c];
            const cellBtn = document.createElement("button");
            cellBtn.className = "cell";
            cellBtn.dataset.row = r;
            cellBtn.dataset.col = c;

            if (cellValue === null) {
                cellBtn.textContent = "";
            } else if (cellValue === "F") {
                cellBtn.textContent = "🚩";
            } else if (cellValue === "M") { // Revealed mine (game lost)
                cellBtn.textContent = "💣";
                cellBtn.disabled = true;
                cellBtn.classList.add("revealed", "mine");
            } else if (cellValue === "*") { // Exploded mine (the one clicked)
                cellBtn.textContent = "💥";
                cellBtn.disabled = true;
                cellBtn.classList.add("revealed", "mine", "exploded");
            } else if (cellValue === "X") { // Incorrectly flagged non-mine
                cellBtn.textContent = "❌";
                cellBtn.disabled = true;
                cellBtn.classList.add("revealed", "misflagged");
            } else {
                cellBtn.textContent = cellValue === 0 ? "" : cellValue;
                cellBtn.disabled = true;
                cellBtn.classList.add("revealed");

                if (showHints && typeof cellValue === "number" && cellValue > 0) {
                    // Use the game's active mask for counting flagged neighbors for hints
                    const flaggedCount = countFlaggedNeighborsWithMask(r, c, activeMaskForHint || getDefaultNeighborsMask());
                    if (flaggedCount === cellValue) {
                        cellBtn.classList.add("mass-reveal-hint");
                    }
                }
            }

            cellBtn.addEventListener("click", handleReveal);
            cellBtn.addEventListener("contextmenu", handleFlag);
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
    const config = getBoardConfig();
    currentCustomMask = config.custom_mask; // Store the mask for agent games too

    fetch("/api/play_agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent: selectedAgent, ...config })
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

// Functions for Custom Mask UI
function initializeMaskGrid() {
    const gridContainer = document.getElementById("custom-mask-grid");
    gridContainer.innerHTML = ''; // Clear previous grid
    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
            const cell = document.createElement("div");
            cell.className = "mask-cell";
            cell.dataset.row = i - 1; // Store relative coordinates (-1, 0, 1)
            cell.dataset.col = j - 1;
            if (i === 1 && j === 1) {
                cell.classList.add("center");
                cell.textContent = "X"; // Center cell
            } else {
                cell.classList.add("selectable");
                // By default, all selectable cells are part of the mask (standard 8 neighbors)
                cell.classList.add("selected"); 
            }
            cell.addEventListener("click", toggleMaskCell);
            gridContainer.appendChild(cell);
        }
    }
    // Disable grid initially if checkbox is not checked
    toggleCustomMaskGridDisabledState(!document.getElementById("enable-custom-mask").checked);
}

function toggleMaskCell(event) {
    if (event.target.classList.contains("center")) return; // Center cell is not selectable

    const cell = event.target;
    cell.classList.toggle("selected");
}

function getCustomMaskFromGrid() {
    const mask = [];
    const cells = document.querySelectorAll("#custom-mask-grid .mask-cell.selectable");
    cells.forEach(cell => {
        if (cell.classList.contains("selected")) {
            mask.push([parseInt(cell.dataset.row), parseInt(cell.dataset.col)]);
        }
    });
    // Ensure the mask is not empty, if all are deselected, revert to default (or handle as error)
    // For now, if empty, it means no neighbors are considered, which might be a valid (though strange) custom game.
    return mask;
}

function toggleCustomMask() {
    const isEnabled = document.getElementById("enable-custom-mask").checked;
    toggleCustomMaskGridDisabledState(!isEnabled);
    // Potentially start a new game or inform the user that settings will apply on next game
    // For simplicity, we'll let it apply on the next "New Game" or "Watch Agent" click.
}

function toggleCustomMaskGridDisabledState(isDisabled) {
    const gridContainer = document.getElementById("custom-mask-grid");
    const cells = gridContainer.querySelectorAll(".mask-cell.selectable");
    if (isDisabled) {
        gridContainer.classList.add("disabled");
        cells.forEach(cell => cell.removeEventListener("click", toggleMaskCell));
    } else {
        gridContainer.classList.remove("disabled");
        cells.forEach(cell => {
            // Remove existing to prevent duplicates if called multiple times
            cell.removeEventListener("click", toggleMaskCell); 
            cell.addEventListener("click", toggleMaskCell);
        });
    }
}

// Helper to get default 8 neighbors if no custom mask is active (for hints)
function getDefaultNeighborsMask() {
    return [
        [-1,-1], [-1,0], [-1,1],
        [0,-1],          [0,1],
        [1,-1], [1,0], [1,1]
    ];
}

function countFlaggedNeighborsWithMask(row, col, mask) {
    let count = 0;
    const board = currentState.board;
    const height = board.length;
    const width = board[0].length;

    for (const [dr, dc] of mask) { // Iterate using the provided mask
        const nr = row + dr;
        const nc = col + dc;
        if (nr >= 0 && nr < height && nc >= 0 && nc < width) {
            if (board[nr][nc] === "F") count++;
        }
    }
    return count;
}
