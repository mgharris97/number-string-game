import math
from src.game_state import GameState

def heuristic_evaluation(state: GameState, perspective: str = 'first') -> float:
    """
    Evaluate a non‑terminal state from the given player's perspective.
    Returns a number: positive means good for that player, negative means bad.
    Placeholder – you can replace with a smarter heuristic.
    """
    # Very simple heuristic: difference in total points (including bank)
    total = state.points + state.bank
    if perspective == 'first':
        return total  # not zero-sum, but we can treat as score difference? Actually points are shared.
    else:
        return -total
    # Better: we might incorporate future opportunities, but for now 0.
    # Let's keep it simple: return 0 for all non-terminal (depth-limited search only).
    return 0.0

def minimax(state: GameState, depth: int, maximizing_player: bool) -> tuple[float, dict | None]:
    """
    Minimax search (without pruning).
    Returns (value, best_move).  value is from the perspective of the first player.
    If depth == 0 or terminal, heuristic/result is returned.
    """
    if state.is_terminal():
        result = state.get_result()
        # Convert result to numeric from first player's perspective:
        if result == 'first':
            return 1.0, None
        elif result == 'second':
            return -1.0, None
        else:
            return 0.0, None

    if depth == 0:
        # Heuristic from first player's perspective
        return heuristic_evaluation(state, perspective='first'), None

    possible_moves = state.get_moves()
    if not possible_moves:
        return 0.0, None   # should not happen

    best_move = possible_moves[0]
    if maximizing_player:   # first player to move
        best_value = -math.inf
        for move in possible_moves:
            next_state = state.apply_move(move)
            value, _ = minimax(next_state, depth - 1, False)
            if value > best_value:
                best_value = value
                best_move = move
        return best_value, best_move
    else:                   # second player to move
        best_value = math.inf
        for move in possible_moves:
            next_state = state.apply_move(move)
            value, _ = minimax(next_state, depth - 1, True)
            if value < best_value:
                best_value = value
                best_move = move
        return best_value, best_move
