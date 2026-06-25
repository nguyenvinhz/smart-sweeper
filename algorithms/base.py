import time

# Lớp cơ sở cho mọi thuật toán giải game Minesweeper.
class Algorithm:
    def __init__(self, board):
        self.original_board = board
        self.board = board.copy()
        self.name = "Base Algorithm"
        self.category = "Unknown"
        self.category_index = 0
        self.description = ""

        self.steps = []

        self.metrics = {
            'time_ms': 0,
            'total_steps': 0,
            'reveals': 0,
            'flags_placed': 0,
            'mines_hit': 0,
            'cells_revealed': 0,
            'nodes_explored': 0,
            'completed': False,
            'success': False,
            'progress': 0.0,
        }

    # Thực thi thuật toán giải, đo thời gian chạy và lưu trữ các chỉ số hiệu suất.
    def solve(self):
        start = time.perf_counter()
        try:
            self._solve()
        except Exception as e:
            self.metrics['error'] = str(e)
        elapsed = time.perf_counter() - start
        self.metrics['time_ms'] = round(elapsed * 1000, 2)
        self.metrics['total_steps'] = len(self.steps)

        revealed_safe, total_safe = self.board.get_progress()
        self.metrics['cells_revealed'] = revealed_safe
        self.metrics['progress'] = round(revealed_safe / max(total_safe, 1) * 100, 1)
        self.metrics['completed'] = self.board.is_complete()
        self.metrics['success'] = self.metrics['completed'] and self.metrics['mines_hit'] == 0

    def _solve(self):
        raise NotImplementedError

    # Thực hiện mở ô trên bảng sao chép và ghi lại bước đi.
    def do_reveal(self, row, col):
        result, auto_revealed = self.board.reveal(row, col)
        if result is None:
            return None

        step = {
            'action': 'reveal',
            'row': row,
            'col': col,
            'result': result,
            'auto_revealed': auto_revealed,
        }
        self.steps.append(step)
        self.metrics['reveals'] += 1
        self.metrics['nodes_explored'] += 1

        if result == -1:
            self.metrics['mines_hit'] += 1

        return result

    # Thực hiện cắm cờ ô trên bảng sao chép và ghi lại bước đi.
    def do_flag(self, row, col):
        if self.board.is_revealed(row, col) or self.board.is_flagged(row, col):
            return
        self.board.flag(row, col)
        step = {
            'action': 'flag',
            'row': row,
            'col': col,
            'result': None,
            'auto_revealed': [],
        }
        self.steps.append(step)
        self.metrics['flags_placed'] += 1

    # Ước lượng xác suất ô chứa mìn dựa trên các ô số lân cận đã mở.
    def get_mine_probability(self, row, col):
        if self.board.is_revealed(row, col) or self.board.is_flagged(row, col):
            return 0.0

        max_prob = 0.0
        has_info = False

        for nr, nc in self.board.get_neighbors(row, col):
            if self.board.is_revealed(nr, nc) and (nr, nc) not in self.board.mines:
                has_info = True
                number = self.board.numbers.get((nr, nc), 0)
                flagged = self.board.get_flagged_neighbor_count(nr, nc)
                unknown = self.board.get_unknown_neighbor_count(nr, nc)
                remaining_mines = number - flagged
                if unknown > 0:
                    prob = remaining_mines / unknown
                    max_prob = max(max_prob, prob)

        if not has_info:
            total_unknown = len(self.board.get_all_unrevealed_unflagged())
            remaining_mines = len(self.board.mines) - len(self.board.flagged & self.board.mines)
            if total_unknown > 0:
                return remaining_mines / total_unknown
            return 0.0

        return min(max_prob, 1.0)

    # Áp dụng các luật logic cơ bản (nhất quán) để mở hoặc cắm cờ các ô lân cận.
    def apply_basic_rules(self):
        changed = False
        numbered_cells = self.board.get_revealed_numbered_cells()

        for r, c, number in numbered_cells:
            flagged_count = self.board.get_flagged_neighbor_count(r, c)
            unrevealed = self.board.get_unrevealed_neighbors(r, c)
            unknown_count = len(unrevealed)

            if unknown_count == 0:
                continue

            if flagged_count == number and unknown_count > 0:
                for ur, uc in unrevealed:
                    result = self.do_reveal(ur, uc)
                    if result is not None:
                        changed = True

            elif number - flagged_count == unknown_count:
                for ur, uc in unrevealed:
                    self.do_flag(ur, uc)
                    changed = True

        return changed

    # Tìm ô chưa mở có xác suất chứa mìn thấp nhất trên toàn bảng.
    def get_safest_cell(self):
        unrevealed = self.board.get_all_unrevealed_unflagged()
        if not unrevealed:
            return None

        best_cell = None
        best_prob = float('inf')

        for r, c in unrevealed:
            prob = self.get_mine_probability(r, c)
            if prob < best_prob:
                best_prob = prob
                best_cell = (r, c)

        return best_cell

    def get_metrics(self):
        return self.metrics

    def get_steps(self):
        return self.steps
