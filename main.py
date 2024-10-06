
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Move(BaseModel):
    player: str
    position: int

class GameState(BaseModel):
    board: List[str]
    current_player: str
    winner: str = None
    draw: bool = False

# Initialize the game state
game_state = GameState(board=[""] * 9, current_player="X")

@app.get("/state", response_model=GameState)
def get_state():
    return game_state

@app.post("/move", response_model=GameState)
def make_move(move: Move):
    if game_state.board[move.position] != "":
        raise HTTPException(status_code=400, detail="Position already taken")
    if game_state.winner or game_state.draw:
        raise HTTPException(status_code=400, detail="Game already finished")

    game_state.board[move.position] = move.player
    game_state.current_player = "O" if move.player == "X" else "X"

    # Check for a winner
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
        [0, 4, 8], [2, 4, 6]              # diagonals
    ]
    for combo in winning_combinations:
        if game_state.board[combo[0]] == game_state.board[combo[1]] == game_state.board[combo[2]] != "":
            game_state.winner = move.player
            return game_state

    # Check for a draw
    if all(cell != "" for cell in game_state.board):
        game_state.draw = True

    return game_state

@app.post("/reset", response_model=GameState)
def reset_game():
    global game_state
    game_state = GameState(board=[""] * 9, current_player="X")
    return game_state

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
