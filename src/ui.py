# Tkinter graphical interface for the Number String Game — light theme, no external dependencies

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random

from src.game_state import GameState
from src.minimax import get_best_move as minimax_best
from src.alphabeta import get_best_move as alphabeta_best
from src.experiments import ExperimentTracker


# Colors

BG          = '#f5f4f0'
PANEL       = '#ffffff'
CARD        = '#f0eeea'
BORDER      = '#d0cec8'
TEXT        = '#1a1a1a'
TEXT_DIM    = '#666666'
ACCENT      = '#c0392b'

EVEN_BG     = '#dbeafe'
EVEN_FG     = '#1e40af'
EVEN_BD     = '#93c5fd'
ODD_BG      = '#dcfce7'
ODD_FG      = '#166534'
ODD_BD      = '#86efac'
UNPAIR_BG   = '#fef9c3'
UNPAIR_FG   = '#854d0e'
UNPAIR_BD   = '#fde047'
SINGLE_BG   = '#fce7f3'
SINGLE_FG   = '#9d174d'
SINGLE_BD   = '#f9a8d4'
COMP_HL_BG  = '#fed7aa'
COMP_HL_BD  = '#f97316'

LOG_HUMAN   = '#1d4ed8'
LOG_COMP    = '#15803d'
LOG_INFO    = '#666666'
LOG_RESULT  = '#c0392b'

FONT_TITLE  = ('Georgia', 18, 'bold')
FONT_SUB    = ('Georgia', 10)
FONT_LABEL  = ('Courier', 10)
FONT_NUM    = ('Courier', 15, 'bold')
FONT_BTN    = ('Courier', 10)
FONT_LOG    = ('Courier', 10)
FONT_SCORE  = ('Courier', 16, 'bold')


# PP

class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root        = root
        self.root.title('Number String Game')
        self.root.configure(bg=BG)
        self.root.minsize(920, 680)

        self.tracker     = ExperimentTracker()
        self.game_state  = None
        self.human_role  = 'first'
        self.comp_role   = 'second'
        self.total_nodes = 0
        self.move_times: list[float] = []
        self.game_active = False
        self.last_comp_move = None

        self._build_ui()
        self._show_setup()

    def run(self) -> None:
        self.root.mainloop()

    # Build UI

    def _build_ui(self) -> None:
        # Header
        hdr = tk.Frame(self.root, bg=BG, pady=14)
        hdr.pack(fill='x', padx=24)
        tk.Label(hdr, text='Number String Game', font=FONT_TITLE,
                 bg=BG, fg=TEXT).pack(side='left')
        tk.Label(hdr, text='  human vs computer', font=FONT_SUB,
                 bg=BG, fg=TEXT_DIM).pack(side='left')
        tk.Button(hdr, text='Rules', font=FONT_BTN, bg=CARD, fg=TEXT,
                  relief='flat', padx=10, pady=4, cursor='hand2',
                  highlightbackground=BORDER, highlightthickness=1,
                  command=self._show_rules).pack(side='right')

        # Divider
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill='x')

        # Content
        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(fill='both', expand=True, padx=24, pady=16)

        self._build_setup_frame()
        self._build_game_frame()

    def _build_setup_frame(self) -> None:
        self.setup_frame = tk.Frame(self.content, bg=PANEL,
                                    relief='flat', bd=1,
                                    highlightbackground=BORDER,
                                    highlightthickness=1)

        tk.Label(self.setup_frame, text='New game',
                 font=('Georgia', 14, 'bold'), bg=PANEL, fg=TEXT).pack(
            pady=(24, 2))
        tk.Label(self.setup_frame, text='Configure your game below',
                 font=FONT_SUB, bg=PANEL, fg=TEXT_DIM).pack(pady=(0, 20))

        grid = tk.Frame(self.setup_frame, bg=PANEL)
        grid.pack(padx=40, fill='x')
        grid.columnconfigure(1, weight=1)

        self.var_len     = tk.IntVar(value=16)
        self.var_starter = tk.StringVar(value='human')
        self.var_algo    = tk.StringVar(value='alphabeta')
        self.var_depth   = tk.IntVar(value=4)

        def field(label: str, widget: tk.Widget, row: int) -> None:
            tk.Label(grid, text=label, font=FONT_LABEL,
                     bg=PANEL, fg=TEXT_DIM, anchor='w').grid(
                row=row, column=0, sticky='w', pady=8, padx=(0, 20))
            widget.grid(row=row, column=1, sticky='ew', pady=8)

        field('String length (15–25)',
              tk.Spinbox(grid, from_=15, to=25, textvariable=self.var_len,
                         width=6, font=FONT_BTN, bg=CARD, fg=TEXT,
                         relief='flat', highlightbackground=BORDER,
                         highlightthickness=1),
              0)
        field('Who starts?',
              ttk.Combobox(grid, textvariable=self.var_starter,
                           values=['human', 'computer'],
                           state='readonly', font=FONT_BTN),
              1)
        field('Algorithm',
              ttk.Combobox(grid, textvariable=self.var_algo,
                           values=['alphabeta', 'minimax'],
                           state='readonly', font=FONT_BTN),
              2)
        field('Search depth',
              ttk.Combobox(grid, textvariable=self.var_depth,
                           values=[3, 4, 5, 6],
                           state='readonly', font=FONT_BTN),
              3)

        tk.Button(self.setup_frame, text='Start game',
                  font=('Courier', 11), bg=ACCENT, fg='white',
                  relief='flat', pady=10, cursor='hand2',
                  activebackground='#a93226', activeforeground='white',
                  command=self._start_game).pack(
            fill='x', padx=40, pady=(24, 30))

    def _build_game_frame(self) -> None:
        self.game_frame = tk.Frame(self.content, bg=BG)

        # ── Left column ──
        left = tk.Frame(self.game_frame, bg=BG)
        left.pack(side='left', fill='both', expand=True, padx=(0, 12))

        # String panel
        sp = tk.Frame(left, bg=PANEL, pady=12, padx=16,
                      highlightbackground=BORDER, highlightthickness=1)
        sp.pack(fill='x', pady=(0, 8))
        hdr_row = tk.Frame(sp, bg=PANEL)
        hdr_row.pack(fill='x')
        tk.Label(hdr_row, text='Number string', font=('Courier', 9, 'bold'),
                 bg=PANEL, fg=TEXT_DIM).pack(side='left')
        self.lbl_len = tk.Label(hdr_row, text='', font=FONT_LABEL,
                                bg=PANEL, fg=TEXT_DIM)
        self.lbl_len.pack(side='right')
        self.num_canvas = tk.Frame(sp, bg=PANEL)
        self.num_canvas.pack(fill='x', pady=(10, 0))

        # Status bar
        self.status_var = tk.StringVar(value='')
        self.status_bar = tk.Label(left, textvariable=self.status_var,
                                   font=FONT_LABEL, bg=CARD, fg=TEXT,
                                   anchor='w', padx=12, pady=8,
                                   highlightbackground=BORDER,
                                   highlightthickness=1)
        self.status_bar.pack(fill='x', pady=(0, 8))

        # Moves panel
        mp = tk.Frame(left, bg=PANEL, pady=10, padx=16,
                      highlightbackground=BORDER, highlightthickness=1)
        mp.pack(fill='x', pady=(0, 8))
        tk.Label(mp, text='Available moves', font=('Courier', 9, 'bold'),
                 bg=PANEL, fg=TEXT_DIM).pack(anchor='w', pady=(0, 8))
        self.pairs_frame = tk.Frame(mp, bg=PANEL)
        self.pairs_frame.pack(fill='x')

        # Control buttons
        ctrl = tk.Frame(left, bg=BG)
        ctrl.pack(fill='x', pady=(0, 8))
        self.btn_delete = tk.Button(
            ctrl, text='Delete unpaired number',
            font=FONT_BTN, bg=PANEL, fg=UNPAIR_FG,
            relief='flat', pady=7, state='disabled',
            highlightbackground=BORDER, highlightthickness=1,
            cursor='hand2', command=self._execute_delete)
        self.btn_delete.pack(side='left', expand=True, fill='x', padx=(0, 6))
        tk.Button(ctrl, text='Start Over', font=FONT_BTN, bg=PANEL, fg=ACCENT,
                  relief='flat', pady=7, cursor='hand2',
                  highlightbackground=BORDER, highlightthickness=1,
                  activeforeground=ACCENT,
                  command=self._reset_game).pack(side='left')

        # Right column
        right = tk.Frame(self.game_frame, bg=BG, width=290)
        right.pack(side='right', fill='both')
        right.pack_propagate(False)

        # Scoreboard
        sc = tk.Frame(right, bg=PANEL, pady=10, padx=12,
                      highlightbackground=BORDER, highlightthickness=1)
        sc.pack(fill='x', pady=(0, 8))
        tk.Label(sc, text='Scoreboard', font=('Courier', 9, 'bold'),
                 bg=PANEL, fg=TEXT_DIM).pack(anchor='w', pady=(0, 8))
        cards = tk.Frame(sc, bg=PANEL)
        cards.pack(fill='x')
        self.sc_points = self._score_card(cards, 'Points', 0)
        self.sc_bank   = self._score_card(cards, 'Bank',   1)
        self.sc_nodes  = self._score_card(cards, 'Nodes',  2)
        self.sc_time   = self._score_card(cards, 'Avg ms', 3)

        # Tabs
        tab_row = tk.Frame(right, bg=BG)
        tab_row.pack(fill='x')
        self.btn_tab_log = tk.Button(
            tab_row, text='Move log', font=FONT_BTN,
            relief='flat', bg=ACCENT, fg='white', pady=5,
            command=lambda: self._switch_tab('log'))
        self.btn_tab_log.pack(side='left', expand=True, fill='x')
        self.btn_tab_exp = tk.Button(
            tab_row, text='Experiments', font=FONT_BTN,
            relief='flat', bg=CARD, fg=TEXT_DIM, pady=5,
            command=lambda: self._switch_tab('experiments'))
        self.btn_tab_exp.pack(side='left', expand=True, fill='x')

        # Log panel
        self.log_frame = tk.Frame(right, bg=PANEL,
                                  highlightbackground=BORDER,
                                  highlightthickness=1)
        self.log_frame.pack(fill='both', expand=True)
        self.log_text = tk.Text(
            self.log_frame, font=FONT_LOG, bg=PANEL, fg=TEXT_DIM,
            relief='flat', wrap='word', state='disabled', padx=8, pady=8)
        log_scroll = tk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        log_scroll.pack(side='right', fill='y')
        self.log_text.pack(fill='both', expand=True)
        self.log_text.tag_configure('human',  foreground=LOG_HUMAN)
        self.log_text.tag_configure('comp',   foreground=LOG_COMP)
        self.log_text.tag_configure('info',   foreground=LOG_INFO)
        self.log_text.tag_configure('result', foreground=LOG_RESULT,
                                    font=('Courier', 10, 'bold'))

        # Experiments panel
        self.exp_frame = tk.Frame(right, bg=PANEL,
                                  highlightbackground=BORDER,
                                  highlightthickness=1)
        cols = ('Game', 'Algo', 'Depth', 'Result', 'Nodes', 'ms')
        style = ttk.Style()
        style.configure('Light.Treeview',
                        background=PANEL, foreground=TEXT,
                        fieldbackground=PANEL, rowheight=22,
                        font=FONT_LOG)
        style.configure('Light.Treeview.Heading',
                        background=CARD, foreground=TEXT,
                        font=('Courier', 9, 'bold'))
        self.exp_tree = ttk.Treeview(
            self.exp_frame, columns=cols, show='headings',
            height=8, style='Light.Treeview')
        widths = [36, 70, 42, 60, 60, 48]
        for c, w in zip(cols, widths):
            self.exp_tree.heading(c, text=c)
            self.exp_tree.column(c, width=w, anchor='center')
        exp_scroll = ttk.Scrollbar(self.exp_frame, orient='vertical',
                                   command=self.exp_tree.yview)
        self.exp_tree.configure(yscrollcommand=exp_scroll.set)
        exp_scroll.pack(side='right', fill='y')
        self.exp_tree.pack(fill='both', expand=True)
        self.exp_summary = tk.Label(
            self.exp_frame, text='', font=FONT_LOG,
            bg=PANEL, fg=TEXT_DIM, anchor='w', padx=8)
        self.exp_summary.pack(fill='x', pady=(4, 0))
        tk.Button(self.exp_frame, text='Export CSV', font=FONT_BTN,
                  bg=CARD, fg=TEXT, relief='flat', pady=5, cursor='hand2',
                  command=self._export_csv).pack(
            fill='x', padx=8, pady=6)

    def _score_card(self, parent: tk.Frame, label: str, col: int) -> tk.StringVar:
        f = tk.Frame(parent, bg=CARD, padx=8, pady=6,
                     highlightbackground=BORDER, highlightthickness=1)
        f.grid(row=0, column=col,
               padx=(0 if col == 0 else 4, 0), sticky='ew')
        parent.columnconfigure(col, weight=1)
        tk.Label(f, text=label, font=('Courier', 8),
                 bg=CARD, fg=TEXT_DIM).pack()
        var = tk.StringVar(value='0')
        tk.Label(f, textvariable=var, font=FONT_SCORE,
                 bg=CARD, fg=TEXT).pack()
        return var

    # How / Hide

    def _show_setup(self) -> None:
        self.game_frame.pack_forget()
        self.setup_frame.place(relx=0.5, rely=0.5, anchor='center',
                               width=480, height=380)

    def _show_game(self) -> None:
        self.setup_frame.place_forget()
        self.game_frame.pack(fill='both', expand=True)

    def _switch_tab(self, tab: str) -> None:
        if tab == 'log':
            self.exp_frame.pack_forget()
            self.log_frame.pack(fill='both', expand=True)
            self.btn_tab_log.configure(bg=ACCENT, fg='white')
            self.btn_tab_exp.configure(bg=CARD, fg=TEXT_DIM)
        else:
            self.log_frame.pack_forget()
            self.exp_frame.pack(fill='both', expand=True)
            self.btn_tab_exp.configure(bg=ACCENT, fg='white')
            self.btn_tab_log.configure(bg=CARD, fg=TEXT_DIM)

    # Rules dialog

    def _show_rules(self) -> None:
        win = tk.Toplevel(self.root)
        win.title('Game Rules')
        win.configure(bg=PANEL)
        win.resizable(False, False)
        win.geometry('480x420')
        rules = (
            "NUMBER STRING GAME — RULES\n"
            "\n"
            "A string of 15–25 numbers (each 1–6) is generated randomly.\n"
            "Two players take turns. Each turn you must do one of:\n"
            "\n"
            "PAIR — choose a fixed adjacent pair (1st+2nd, 3rd+4th, …)\n"
            "and replace them with their sum.\n"
            "  • If the sum > 6, apply substitution:\n"
            "    7→1, 8→2, 9→3, 10→4, 11→5, 12→6\n"
            "  • Pairing adds +1 point.\n"
            "  • If substitution was used, +1 to the bank.\n"
            "\n"
            "DELETE — only when the string length is odd.\n"
            "  Removes the last unpaired number. Costs −1 point.\n"
            "\n"
            "Every move shrinks the string by 1. The game ends\n"
            "when one number remains.\n"
            "\n"
            "WINNING CONDITION (bank is added to points):\n"
            "  • Final number even AND total score even → First wins\n"
            "  • Final number odd AND total score odd → Second wins\n"
            "  • Otherwise → Draw"
        )
        tk.Label(win, text=rules, font=FONT_LOG, bg=PANEL, fg=TEXT,
                 justify='left', anchor='nw', padx=20, pady=20).pack(
            fill='both', expand=True)
        tk.Button(win, text='Close', font=FONT_BTN, bg=CARD, fg=TEXT,
                  relief='flat', pady=6, cursor='hand2',
                  command=win.destroy).pack(pady=(0, 16))

    # Game Lifecycle

    def _start_game(self) -> None:
        length           = max(15, min(25, int(self.var_len.get())))
        starter          = self.var_starter.get()
        self.human_role  = 'first'  if starter == 'human'    else 'second'
        self.comp_role   = 'second' if starter == 'human'    else 'first'
        nums             = [random.randint(1, 6) for _ in range(length)]
        self.game_state  = GameState(nums, 0, 0, 'first')
        self.total_nodes    = 0
        self.move_times     = []
        self.move_count     = 0
        self.last_comp_move = None
        self.game_active    = True
        self._show_game()
        self._clear_log()
        self._log(f'Game started — [{", ".join(map(str, nums))}]', 'info')
        self._log(f'Human = {self.human_role} | Computer = {self.comp_role}', 'info')
        self._render()
        if self.game_state.turn == self.comp_role:
            self.root.after(600, self._computer_move)

    def _reset_game(self) -> None:
        self.game_active = False
        self.game_state  = None
        self._show_setup()

    # Render

    def _render(self) -> None:
        if not self.game_state:
            return
        nums = self.game_state.nums
        n    = len(nums)

        self.lbl_len.configure(
            text=f'{n} number{"s" if n != 1 else ""} remaining')

        # Clear number cells
        for w in self.num_canvas.winfo_children():
            w.destroy()

        hl = self.last_comp_move  # index to highlight (or None)
        num_pairs = n // 2
        for p in range(num_pairs):
            i1, i2 = p * 2, p * 2 + 1
            highlighted = hl is not None and (i1 == hl or i2 == hl)
            bg = COMP_HL_BG if highlighted else (EVEN_BG if p % 2 == 0 else ODD_BG)
            fg = EVEN_FG if p % 2 == 0 else ODD_FG
            bd = COMP_HL_BD if highlighted else (EVEN_BD if p % 2 == 0 else ODD_BD)
            slot = tk.Frame(self.num_canvas, bg=BG)
            slot.pack(side='left', padx=(0, 6))
            cells = tk.Frame(slot, bg=bd, padx=1, pady=1)
            cells.pack()
            tk.Label(cells, text=str(nums[i1]), font=FONT_NUM,
                     bg=bg, fg=fg, width=2, pady=4).pack(side='left')
            tk.Frame(cells, bg=bd, width=1).pack(side='left', fill='y')
            tk.Label(cells, text=str(nums[i2]), font=FONT_NUM,
                     bg=bg, fg=fg, width=2, pady=4).pack(side='left')
            tk.Label(slot, text=f'pair {p+1}', font=('Courier', 8),
                     bg=BG, fg=TEXT_DIM).pack()

        if n % 2 != 0:
            slot = tk.Frame(self.num_canvas, bg=BG)
            slot.pack(side='left', padx=(0, 6))
            bg = SINGLE_BG if n == 1 else UNPAIR_BG
            fg = SINGLE_FG if n == 1 else UNPAIR_FG
            bd = SINGLE_BD if n == 1 else UNPAIR_BD
            cell = tk.Frame(slot, bg=bd, padx=1, pady=1)
            cell.pack()
            tk.Label(cell, text=str(nums[-1]), font=FONT_NUM,
                     bg=bg, fg=fg, width=2, pady=4).pack()
            tk.Label(slot, text='final' if n == 1 else 'unpaired',
                     font=('Courier', 8), bg=BG, fg=fg).pack()

        # Status bar
        is_human = self.game_state.turn == self.human_role
        if self.game_state.is_terminal():
            r = self.game_state.get_result()
            self.status_var.set(f'  Game over — {self._label_result(r)}')
            self.status_bar.configure(fg=ACCENT)
        else:
            who = 'Your turn' if is_human else 'Computer thinking…'
            self.status_var.set(
                f'  {who}   |   {n} numbers   |   '
                f'Points: {self.game_state.points}   Bank: {self.game_state.bank}')
            self.status_bar.configure(fg=EVEN_FG if is_human else ODD_FG)

        # Pair buttons
        for w in self.pairs_frame.winfo_children():
            w.destroy()
        active = self.game_active and is_human and not self.game_state.is_terminal()
        for p in range(num_pairs):
            i1, i2 = p * 2, p * 2 + 1
            a, b   = nums[i1], nums[i2]
            raw    = a + b
            from src.game_state import mod6
            val, sub = mod6(raw)
            label = f'Pair {p+1}:  {a} + {b} = {raw}' + (f' → {val}' if sub else '')
            tk.Button(
                self.pairs_frame, text=label, font=FONT_BTN,
                bg=CARD, fg=TEXT, relief='flat', pady=5,
                anchor='w', padx=8,
                state='normal' if active else 'disabled',
                highlightbackground=BORDER, highlightthickness=1,
                cursor='hand2' if active else 'arrow',
                activebackground=EVEN_BG,
                command=lambda idx=p: self._execute_pair(idx)
            ).pack(fill='x', pady=2)

        # Delete button
        can_delete = active and n % 2 != 0 and n > 1
        self.btn_delete.configure(
            state='normal' if can_delete else 'disabled',
            text=f'Delete unpaired: {nums[-1]}' if can_delete
                 else 'Delete unpaired number')

        # Scores
        self.sc_points.set(str(self.game_state.points))
        self.sc_bank.set(str(self.game_state.bank))
        self.sc_nodes.set(str(self.total_nodes))
        avg = round(sum(self.move_times) / len(self.move_times)) \
              if self.move_times else 0
        self.sc_time.set(str(avg))

    # Human moves

    def _execute_pair(self, pair_idx: int) -> None:
        if not self.game_active or self.game_state.turn != self.human_role:
            return
        self.last_comp_move = None
        from src.game_state import mod6
        i1, i2  = pair_idx * 2, pair_idx * 2 + 1
        a, b    = self.game_state.nums[i1], self.game_state.nums[i2]
        raw     = a + b
        val, sub = mod6(raw)
        self.move_count += 1
        self._log(
            f'#{self.move_count}  You  →  pair {pair_idx+1}: ({a}, {b}) = {raw}'
            + (f' → {val}' if sub else '')
            + f'  |  +1 pt' + ('  +1 bank' if sub else ''),
            'human')
        self.game_state = self.game_state.apply_move(
            {'type': 'pair', 'pair_idx': pair_idx})
        self._render()
        self._check_end()

    def _execute_delete(self) -> None:
        if not self.game_active or self.game_state.turn != self.human_role:
            return
        self.last_comp_move = None
        val = self.game_state.nums[-1]
        self.move_count += 1
        self._log(f'#{self.move_count}  You  →  delete unpaired: {val}  |  −1 pt', 'human')
        self.game_state = self.game_state.apply_move({'type': 'delete'})
        self._render()
        self._check_end()

    # Computer move

    def _computer_move(self) -> None:
        if not self.game_active or not self.game_state:
            return
        if self.game_state.is_terminal() or self.game_state.turn != self.comp_role:
            return
        algo  = self.var_algo.get()
        depth = int(self.var_depth.get())
        res   = (alphabeta_best if algo == 'alphabeta' else minimax_best)(
            self.game_state, depth)
        if not res or not res['move']:
            return
        self.total_nodes += res['nodes']
        self.move_times.append(res['time_ms'])
        self.move_count += 1
        m = res['move']
        # Track which index in the new array the computer's result lands at
        if m['type'] == 'pair':
            self.last_comp_move = m['pair_idx'] * 2
        else:
            self.last_comp_move = -1  # delete — highlight last cell before removal
        from src.game_state import mod6
        if m['type'] == 'pair':
            i1, i2  = m['pair_idx'] * 2, m['pair_idx'] * 2 + 1
            a, b    = self.game_state.nums[i1], self.game_state.nums[i2]
            raw     = a + b
            val, sub = mod6(raw)
            self._log(
                f'#{self.move_count}  Comp →  pair {m["pair_idx"]+1}: ({a}, {b}) = {raw}'
                + (f' → {val}' if sub else '')
                + f'  |  +1 pt' + ('  +1 bank' if sub else '')
                + f'  [{res["nodes"]} nodes, {round(res["time_ms"])}ms]',
                'comp')
        else:
            self._log(
                f'#{self.move_count}  Comp →  delete: {self.game_state.nums[-1]}'
                + f'  |  −1 pt  [{res["nodes"]} nodes, {round(res["time_ms"])}ms]',
                'comp')
        self.game_state = self.game_state.apply_move(m)
        self._render()
        self._check_end()

    # End of game

    def _check_end(self) -> None:
        if not self.game_state.is_terminal():
            if self.game_active and self.game_state.turn == self.comp_role:
                self.root.after(600, self._computer_move)
            return
        self.game_active = False
        r   = self.game_state.get_result()
        fn  = self.game_state.nums[0]
        tot = self.game_state.points + self.game_state.bank
        self._log(
            f'Final: {fn} ({"even" if fn%2==0 else "odd"})  '
            f'Total: {self.game_state.points} + {self.game_state.bank} = {tot} '
            f'({"even" if tot%2==0 else "odd"})', 'info')
        self._log(f'Result: {self._label_result(r)}', 'result')
        self._render()
        self._record_experiment(r)
        again = messagebox.askquestion(
            self._label_result(r),
            f'{self._label_result(r)}\n\n'
            f'Final number: {fn}  |  Total score: {tot}\n\n'
            f'Play again?', icon='info')
        if again == 'yes':
            self._reset_game()

    def _label_result(self, r: str) -> str:
        if r == self.human_role:   return 'You win!'
        if r == self.comp_role:    return 'Computer wins'
        return 'Draw'

    # Experiments

    def _record_experiment(self, result: str) -> None:
        self.tracker.record(
            algo       = self.var_algo.get(),
            depth      = int(self.var_depth.get()),
            length     = int(self.var_len.get()),
            starter    = self.var_starter.get(),
            result     = result,
            nodes      = self.total_nodes,
            move_times = self.move_times,
            points     = self.game_state.points,
            bank       = self.game_state.bank,
        )
        g  = self.tracker.games[-1]
        rl = self._label_result(result)
        self.exp_tree.insert('', 'end', values=(
            g['game'], g['algo'], g['depth'], rl, g['nodes'], g['avg_ms']
        ))
        hw = sum(1 for x in self.tracker.games if x['result'] == self.human_role)
        cw = sum(1 for x in self.tracker.games if x['result'] == self.comp_role)
        dr = sum(1 for x in self.tracker.games if x['result'] == 'draw')
        self.exp_summary.configure(
            text=f'  {len(self.tracker.games)} games  |  '
                 f'Human: {hw}  Computer: {cw}  Draws: {dr}')

    def _export_csv(self) -> None:
        if not self.tracker.games:
            messagebox.showinfo('No data', 'No experiments recorded yet.')
            return
        fp = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile='experiments.csv')
        if fp:
            self.tracker.export_csv(fp)
            messagebox.showinfo('Exported', f'Saved to:\n{fp}')

    # ── Log ───────────────────────────────────────────────────────────────────

    def _log(self, msg: str, tag: str = 'info') -> None:
        self.log_text.configure(state='normal')
        self.log_text.insert('end', msg + '\n', tag)
        self.log_text.configure(state='disabled')
        self.log_text.see('end')

    def _clear_log(self) -> None:
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.configure(state='disabled')
