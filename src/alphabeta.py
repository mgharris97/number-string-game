# Matthew Harris
# March 29, 2026

# import time to measure how long the computer will take to make a move
import time 
from src.game_state import GameState
# reuse the heuristic from minmax as there is no need to rewrite it
from src.minimax import heuristic 


def alphabeta(
    state:   GameState,         # the current position in the game
    depth:   int,               # how many more levels are allowed to look ahead
    alpha:   float,             # best score the maximizer cal already guarantee
    beta:    float,             # best score the minimizer can already gurantee
    is_max:  bool,              # boolean to check if it is the maximizers turn (true)
    counter: dict[str, int],    # visited node counter 
) -> float:
    
    # Node counter. Every call to alphabeta increments this by one regardless if the node gets pruned or not. 
    # So for example, the it will increment by 1 after the first move
    counter['nodes'] += 1

    # Recursion stops if the the game is over due to one number remaining or if we've reached the depth limit
    # is_terminal() is define within game_state and just checks if only one number is left in the string. 
    if state.is_terminal() or depth == 0:
        result = state.get_result()
        if result == 'first':  return  100 + depth
        if result == 'second': return -(100 + depth)
        if result == 'draw':   return  0
        return heuristic(state)
    # If the game is over we return a definitive score. 

    moves = state.get_moves()


    if is_max:
        best: float = float('-inf')
        for move in moves:
            val   = alphabeta(state.apply_move(move), depth - 1, alpha, beta, False, counter)
            best  = max(best, val)
            alpha = max(alpha, best)
            if beta <= alpha:
                break               # beta cut-off — minimiser won't allow this
        return best
    else:
        best: float = float('inf')
        for move in moves:
            val  = alphabeta(state.apply_move(move), depth - 1, alpha, beta, True, counter)
            best = min(best, val)
            beta = min(beta, best)
            if beta <= alpha:
                break               # alpha cut-off — maximiser won't allow this
        return best


def get_best_move(
    state: GameState,
    depth: int,
) -> dict[str, object]:
    """
    Find the best move for the current player using Alpha-Beta pruning.
    Identical interface to minimax.get_best_move.

    Parameters
    ----------
    state : current game state
    depth : number of plies to search

    Returns
    -------
    dict with keys:
        move     : dict   — the best move found
        nodes    : int    — total nodes evaluated
        time_ms  : float  — time taken in milliseconds
    """
    counter:   dict[str, int]  = {'nodes': 0}
    is_first:  bool            = state.turn == 'first'
    best_move: dict | None     = None
    best_val:  float           = float('-inf') if is_first else float('inf')
    t0:        float           = time.time()

    for move in state.get_moves():
        child = state.apply_move(move)
        val   = alphabeta(child, depth - 1, float('-inf'), float('inf'), not is_first, counter)

        if is_first and val > best_val:
            best_val  = val
            best_move = move
        elif not is_first and val < best_val:
            best_val  = val
            best_move = move

    return {
        'move':    best_move,
        'nodes':   counter['nodes'],
        'time_ms': (time.time() - t0) * 1000,
    }
