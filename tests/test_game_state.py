"""
Tests for game_state.py
Run with: python -m pytest tests/test_game_state.py -v
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.game_state import GameState, mod6


# ── mod6 ──────────────────────────────────────────────────────────────────────

def test_mod6_no_substitution_below_6() -> None:
    assert mod6(5) == (5, False)

def test_mod6_no_substitution_at_6() -> None:
    assert mod6(6) == (6, False)

def test_mod6_substitution_at_7() -> None:
    assert mod6(7) == (1, True)

def test_mod6_substitution_at_8() -> None:
    assert mod6(8) == (2, True)

def test_mod6_substitution_at_12() -> None:
    assert mod6(12) == (6, True)


# ── get_moves ─────────────────────────────────────────────────────────────────

def test_get_moves_even_length_no_delete() -> None:
    """Even length — pairs only, no delete available."""
    state: GameState = GameState([1, 2, 3, 4])
    moves = state.get_moves()
    types = [m['type'] for m in moves]
    assert 'delete' not in types

def test_get_moves_even_length_correct_pairs() -> None:
    state: GameState = GameState([1, 2, 3, 4])
    moves = state.get_moves()
    assert moves[0] == {'type': 'pair', 'pair_idx': 0}
    assert moves[1] == {'type': 'pair', 'pair_idx': 1}

def test_get_moves_odd_length_has_delete() -> None:
    """Odd length — delete must be available."""
    state: GameState = GameState([1, 2, 3, 4, 5])
    moves = state.get_moves()
    types = [m['type'] for m in moves]
    assert 'delete' in types

def test_get_moves_odd_length_correct_pair_count() -> None:
    state: GameState = GameState([1, 2, 3, 4, 5])
    moves = state.get_moves()
    assert sum(1 for m in moves if m['type'] == 'pair') == 2

def test_pair_indices_always_even() -> None:
    """pair_idx * 2 must always land on an even index — slots never cross boundaries."""
    state: GameState = GameState([1, 2, 3, 4, 5, 6])
    for move in state.get_moves():
        if move['type'] == 'pair':
            assert (move['pair_idx'] * 2) % 2 == 0

def test_single_number_has_no_moves() -> None:
    """Terminal state — no moves available."""
    state: GameState = GameState([4])
    assert state.get_moves() == []


# ── apply_move ────────────────────────────────────────────────────────────────

def test_apply_move_pair_reduces_length_by_one() -> None:
    state: GameState = GameState([1, 2, 3, 4])
    new_state = state.apply_move({'type': 'pair', 'pair_idx': 0})
    assert len(new_state.nums) == len(state.nums) - 1

def test_apply_move_delete_reduces_length_by_one() -> None:
    state: GameState = GameState([1, 2, 3])
    new_state = state.apply_move({'type': 'delete'})
    assert len(new_state.nums) == len(state.nums) - 1

def test_apply_move_does_not_mutate_original() -> None:
    state: GameState    = GameState([1, 2, 3, 4])
    original: list[int] = list(state.nums)
    state.apply_move({'type': 'pair', 'pair_idx': 0})
    assert state.nums == original

def test_pair_adds_one_point() -> None:
    state: GameState = GameState([1, 2, 3, 4])
    new_state = state.apply_move({'type': 'pair', 'pair_idx': 0})
    assert new_state.points == state.points + 1

def test_delete_subtracts_one_point() -> None:
    state: GameState = GameState([1, 2, 3])
    new_state = state.apply_move({'type': 'delete'})
    assert new_state.points == state.points - 1

def test_pair_with_substitution_correct_value() -> None:
    """4 + 5 = 9 → mod6 → 3"""
    state: GameState = GameState([4, 5])
    new_state = state.apply_move({'type': 'pair', 'pair_idx': 0})
    assert new_state.nums[0] == 3

def test_pair_with_substitution_increments_bank() -> None:
    state: GameState = GameState([4, 5])
    new_state = state.apply_move({'type': 'pair', 'pair_idx': 0})
    assert new_state.bank == 1

def test_pair_without_substitution_correct_value() -> None:
    """2 + 3 = 5 — no substitution"""
    state: GameState = GameState([2, 3])
    new_state = state.apply_move({'type': 'pair', 'pair_idx': 0})
    assert new_state.nums[0] == 5

def test_pair_without_substitution_no_bank() -> None:
    state: GameState = GameState([2, 3])
    new_state = state.apply_move({'type': 'pair', 'pair_idx': 0})
    assert new_state.bank == 0

def test_turn_flips_first_to_second() -> None:
    state: GameState = GameState([1, 2, 3, 4], turn='first')
    new_state = state.apply_move({'type': 'pair', 'pair_idx': 0})
    assert new_state.turn == 'second'

def test_turn_flips_second_to_first() -> None:
    state: GameState = GameState([1, 2, 3, 4], turn='second')
    new_state = state.apply_move({'type': 'pair', 'pair_idx': 0})
    assert new_state.turn == 'first'

def test_delete_removes_last_element() -> None:
    state: GameState = GameState([1, 2, 3])
    new_state = state.apply_move({'type': 'delete'})
    assert new_state.nums == [1, 2]


# ── is_terminal ───────────────────────────────────────────────────────────────

def test_is_terminal_single_number() -> None:
    assert GameState([4]).is_terminal() is True

def test_is_terminal_two_numbers() -> None:
    assert GameState([1, 2]).is_terminal() is False

def test_is_terminal_many_numbers() -> None:
    assert GameState([1, 2, 3, 4, 5]).is_terminal() is False


# ── get_result ────────────────────────────────────────────────────────────────

def test_get_result_first_wins_both_even() -> None:
    """Final number 2 (even), total 2+0=2 (even) → first wins."""
    state: GameState = GameState([2], points=2, bank=0)
    assert state.get_result() == 'first'

def test_get_result_first_wins_with_bank() -> None:
    """Final number 4 (even), total 1+1=2 (even) → first wins."""
    state: GameState = GameState([4], points=1, bank=1)
    assert state.get_result() == 'first'

def test_get_result_second_wins_both_odd() -> None:
    """Final number 3 (odd), total 1+0=1 (odd) → second wins."""
    state: GameState = GameState([3], points=1, bank=0)
    assert state.get_result() == 'second'

def test_get_result_draw_even_odd() -> None:
    """Final number 2 (even), total 1+0=1 (odd) → draw."""
    state: GameState = GameState([2], points=1, bank=0)
    assert state.get_result() == 'draw'

def test_get_result_draw_odd_even() -> None:
    """Final number 3 (odd), total 2+0=2 (even) → draw."""
    state: GameState = GameState([3], points=2, bank=0)
    assert state.get_result() == 'draw'

def test_get_result_none_if_not_terminal() -> None:
    state: GameState = GameState([1, 2])
    assert state.get_result() is None