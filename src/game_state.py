MOD6_MAP = {7: 1, 8: 2, 9: 3, 10: 4, 11: 5, 12: 6}


def mod6(n):
    """Apply mod-6 substitution: 7→1, 8→2 … 12→6. Returns (value, used_sub)."""
    if n > 6:
        return MOD6_MAP[n], True
    return n, False


class GameState:
    """
    Represents a single node in the game tree.

    Attributes
    ----------
    nums   : list[int]  current number string (shrinks by 1 each move)
    points : int        running total score
    bank   : int        substitution bank
    turn   : str        'first' or 'second'
    """

    def __init__(self, nums, points=0, bank=0, turn='first'):
        self.nums   = list(nums)
        self.points = points
        self.bank   = bank
        self.turn   = turn

    def clone(self):
        return GameState(self.nums, self.points, self.bank, self.turn)

    def is_terminal(self):
        return len(self.nums) == 1

    def get_moves(self):
        """
        Return all legal moves for the current state.

        A move is one of:
          {'type': 'pair',   'pair_idx': int}  — collapse fixed slot (pair_idx*2, pair_idx*2+1)
          {'type': 'delete'}                   — remove last element (only when len is odd)

        pair_idx * 2 is always an even index, so slots never cross boundaries.
        """
        moves = []
        n = len(self.nums)

        # Fixed pair slots: (0,1), (2,3), (4,5) …
        for p in range(n // 2):
            moves.append({'type': 'pair', 'pair_idx': p})

        # Delete only when length is odd (last element has no partner)
        if n % 2 != 0 and n > 1:
            moves.append({'type': 'delete'})

        return moves

    def apply_move(self, move):
        """
        Apply a move and return a NEW GameState. Never mutates self.
        """
        s = self.clone()

        if move['type'] == 'pair':
            i1  = move['pair_idx'] * 2
            i2  = i1 + 1
            raw = s.nums[i1] + s.nums[i2]
            val, used_sub = mod6(raw)
            s.nums[i1] = val
            del s.nums[i2]          # collapse pair into one value
            s.points += 1
            if used_sub:
                s.bank += 1

        elif move['type'] == 'delete':
            s.nums.pop()            # remove last unpaired element
            s.points -= 1

        # Flip turn
        s.turn = 'second' if s.turn == 'first' else 'first'
        return s

    def get_result(self):
        """
        Returns 'first', 'second', 'draw', or None if not terminal.

        Win conditions (checked at end of game):
          final number even  AND  total score even  → first player wins
          final number odd   AND  total score odd   → second player wins
          otherwise                                 → draw
        """
        if not self.is_terminal():
            return None

        final_num   = self.nums[0]
        total_score = self.points + self.bank

        if final_num % 2 == 0 and total_score % 2 == 0:
            return 'first'
        if final_num % 2 == 1 and total_score % 2 == 1:
            return 'second'
        return 'draw'

    def __repr__(self):
        return (f"GameState(nums={self.nums}, points={self.points}, "
                f"bank={self.bank}, turn={self.turn!r})")
