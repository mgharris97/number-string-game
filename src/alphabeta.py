# Matthew Harris
# March 29, 2026

# import time to measure how long the computer will take to make a move
import time
from src.game_state import GameState

# reuse the heuristic from minimax as there is no need to rewrite it
from src.minimax import heuristic
# The heuristic is what looks at a game position that isn't finished yet and returns a number estimating how good it is. It's located in minimax.py


def alphabeta(
    state: GameState,           # the current position in the game
    depth: int,                 # how many more levels are allowed to look ahead
    alpha: float,               # best score the maximizer can already guarantee
    beta: float,                # best score the minimizer can already guarantee
    is_max: bool,               # boolean to check if it is the maximizers turn (true)
    counter: dict[str, int],    # visited node counter
) -> float:

    # Node counter. Every call to alphabeta increments this by one regardless if the node gets pruned or not.
    # So for example, the it will increment by 1 after the first move
    counter["nodes"] += 1

    # Recursion stops if the the game is over due to one number remaining or if we've reached the depth limit
    # is_terminal() is define within game_state and just checks if only one number is left in the string.
    if state.is_terminal() or depth == 0:
        result = state.get_result() # see get_result() in game_state
        if result == "first":
            return 100 + depth
        if result == "second":
            return -(100 + depth)
        if result == "draw":
            return 0
        return heuristic(state)
    # If the game is over we return a definitive score.

    # call to get_moves from game_state.py and stores all the legal moves available on the current position 
    # The algorithm then loops over this list and evaluates each move one by one to decide which one is best. 
    moves = state.get_moves()

    # checks if it's maximizers turn otherwise it's the minimizers turn

    if is_max:
        best: float = float("-inf") # set maximizers starting score to negative infinity since anyting is better than negative infinity
        for move in moves:
            # For each move we apply it to get a new game state. 
            # Search one level deeper
            # Flip to the minimizers turn 
            # get back a score (val) representing how good of a move it is after looking n-level deep
            val = alphabeta(state.apply_move(move), depth - 1, alpha, beta, False, counter)
            # If this move's score is better than anything we've seen so far, update best
            best = max(best, val)
            alpha = max(alpha, best)
            if beta <= alpha:
                break  # beta cut-off — minimiser won't allow this
        return best
    else:
        # minimizers turn
        # same recursive call as maximizer except its a mirror image as minimizer wants the lowest possible score
        best: float = float("inf")
        for move in moves:
            val = alphabeta(
                state.apply_move(move), depth - 1, alpha, beta, True, counter
            )
            # if this move's score is lower than anything we've seen so far, update best
            best = min(best, val)
            beta = min(beta, best)
            if beta <= alpha:
                break  # alpha cut-off — maximiser won't allow this
        return best


# This is the entry point — the function the UI calls when it's the computer's turn.

def get_best_move(
    state: GameState,
    depth: int,
) -> dict[str, object]:

    # Creates the node counter starting at 0. This gets passed into every recursive alphabeta() call and incremented each time, so at the end we know the total number of nodes evaluated.
    counter: dict[str, int] = {"nodes": 0}
    # Checks whose turn it is 
    is_first: bool = state.turn == "first"
    # We haven't looked at any moves yet so best_move is None. 
    # best_val starts at -inf if we're maximising or +inf if we're minimising 
    best_move: dict | None = None
    best_val: float = float("-inf") if is_first else float("inf")
    # start time record to see how long it took 
    t0: float = time.time()

    # Loop over every legal move. 
    # For each one, apply it and run the full Alpha-Beta search on the resulting position.
    # return val, the score 
    for move in state.get_moves():
        child = state.apply_move(move)
        val = alphabeta(
            child, depth - 1, float("-inf"), float("inf"), not is_first, counter
        )

        if is_first and val > best_val:
            best_val = val
            best_move = move
        elif not is_first and val < best_val:
            best_val = val
            best_move = move

    # Return three things back to the UI:

    # move: the actual move the computer will play 
    # nodes: how many nodes were evaluated (for the experiments report) 
    # time_ms: how long it took in milliseconds (also for the report)
    return {
        "move": best_move,
        "nodes": counter["nodes"],
        "time_ms": (time.time() - t0) * 1000,
    }
