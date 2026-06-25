
import random
import copy


# Đại diện cho bảng game Minesweeper, quản lý trạng thái, đặt mìn, mở ô và thông tin lân cận.
class Board:


    # Khởi tạo bảng với số hàng, số cột, số mìn và seed ngẫu nhiên.
    def __init__(self, rows, cols, num_mines, seed=None):
        self.rows = rows
        self.cols = cols
        self.num_mines = min(num_mines, rows * cols - 9)
        self.seed = seed
        self.mines = set()
        self.revealed = set()
        self.flagged = set()
        self.numbers = {}
        self.mines_hit = 0
        self.game_over = False
        self.mines_placed = False

    # Đặt mìn ngẫu nhiên lên bảng, loại trừ ô đầu tiên và các ô lân cận để đảm bảo an toàn.
    def place_mines(self, safe_row=None, safe_col=None):
        rng = random.Random(self.seed)
        forbidden = set()
        if safe_row is not None and safe_col is not None:
            forbidden.add((safe_row, safe_col))
            for nr, nc in self._get_neighbors(safe_row, safe_col):
                forbidden.add((nr, nc))
        all_cells = [(r, c) for r in range(self.rows) for c in range(self.cols)
                     if (r, c) not in forbidden]
        actual_mines = min(self.num_mines, len(all_cells))
        self.mines = set(rng.sample(all_cells, actual_mines))
        self.num_mines = actual_mines
        self.mines_placed = True
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in self.mines:
                    count = sum(1 for nr, nc in self._get_neighbors(r, c)
                                if (nr, nc) in self.mines)
                    self.numbers[(r, c)] = count

    # Mở một ô trên bảng, trả về giá trị số mìn lân cận hoặc -1 nếu trúng mìn.
    def reveal(self, row, col):
        if not self._in_bounds(row, col):
            return None, []
        if (row, col) in self.revealed or (row, col) in self.flagged:
            return None, []
        newly_revealed = []
        if (row, col) in self.mines:
            self.revealed.add((row, col))
            self.mines_hit += 1
            newly_revealed.append((row, col))
            return -1, newly_revealed
        self._flood_reveal(row, col, newly_revealed)
        return self.numbers.get((row, col), 0), newly_revealed

    # Thuật toán loang (flood fill) để tự động mở các ô trống lân cận.
    def _flood_reveal(self, row, col, newly_revealed):
        if (row, col) in self.revealed or (row, col) in self.flagged:
            return
        if (row, col) in self.mines or not self._in_bounds(row, col):
            return
        self.revealed.add((row, col))
        newly_revealed.append((row, col))
        if self.numbers.get((row, col), 0) == 0:
            for nr, nc in self._get_neighbors(row, col):
                self._flood_reveal(nr, nc, newly_revealed)

    # Cắm cờ đánh dấu mìn tại một ô chưa mở.
    def flag(self, row, col):
        if (row, col) not in self.revealed and self._in_bounds(row, col):
            self.flagged.add((row, col))

    # Gỡ cờ đánh dấu tại một ô.
    def unflag(self, row, col):
        self.flagged.discard((row, col))

    def is_mine(self, r, c):     return (r, c) in self.mines
    def is_revealed(self, r, c): return (r, c) in self.revealed
    def is_flagged(self, r, c):  return (r, c) in self.flagged

    def get_number(self, r, c):
        if (r, c) in self.revealed and (r, c) not in self.mines:
            return self.numbers.get((r, c), 0)
        return None

    def is_complete(self):
        total_safe = self.rows * self.cols - len(self.mines)
        return len(self.revealed - self.mines) >= total_safe

    def get_progress(self):
        total_safe = self.rows * self.cols - len(self.mines)
        return len(self.revealed - self.mines), total_safe

    # Lấy danh sách tọa độ các ô lân cận hợp lệ trong phạm vi bảng.
    def _get_neighbors(self, row, col):
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = row + dr, col + dc
                if self._in_bounds(nr, nc):
                    neighbors.append((nr, nc))
        return neighbors

    # Lấy các ô lân cận, hỗ trợ lọc ô chưa mở (hidden_only).
    def get_neighbors(self, row, col, hidden_only=False):
        if hidden_only:
            return [(r, c) for r, c in self._get_neighbors(row, col)
                    if (r, c) not in self.revealed]
        return self._get_neighbors(row, col)

    # Lấy danh sách các ô lân cận chưa mở và không bị cắm cờ.
    def get_unrevealed_neighbors(self, row, col):
        return [(r, c) for r, c in self._get_neighbors(row, col)
                if (r, c) not in self.revealed and (r, c) not in self.flagged]

    def get_flagged_neighbor_count(self, row, col):
        return sum(1 for r, c in self._get_neighbors(row, col) if (r, c) in self.flagged)

    def get_unknown_neighbor_count(self, row, col):
        return len(self.get_unrevealed_neighbors(row, col))

    def get_revealed_numbered_cells(self):
        result = []
        for (r, c) in self.revealed:
            if (r, c) not in self.mines:
                n = self.numbers.get((r, c), 0)
                if n > 0:
                    result.append((r, c, n))
        return result

    def get_all_unrevealed(self):
        return [(r, c) for r in range(self.rows) for c in range(self.cols)
                if (r, c) not in self.revealed]

    def get_all_unrevealed_unflagged(self):
        return [(r, c) for r in range(self.rows) for c in range(self.cols)
                if (r, c) not in self.revealed and (r, c) not in self.flagged]

    # Lấy các ô biên (chưa mở, không cắm cờ nhưng kề cạnh ít nhất một ô đã mở).
    def get_frontier_cells(self):
        frontier = set()
        for (r, c) in self.revealed:
            for nr, nc in self._get_neighbors(r, c):
                if (nr, nc) not in self.revealed and (nr, nc) not in self.flagged:
                    frontier.add((nr, nc))
        return list(frontier)

    def _in_bounds(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def copy(self):
        new_board = Board(self.rows, self.cols, self.num_mines, self.seed)
        new_board.mines = set(self.mines)
        new_board.revealed = set(self.revealed)
        new_board.flagged = set(self.flagged)
        new_board.numbers = dict(self.numbers)
        new_board.mines_hit = self.mines_hit
        new_board.game_over = self.game_over
        new_board.mines_placed = self.mines_placed
        return new_board

    def reset(self):
        self.revealed = set()
        self.flagged = set()
        self.mines_hit = 0
        self.game_over = False

    def __repr__(self):
        lines = []
        for r in range(self.rows):
            row_str = ""
            for c in range(self.cols):
                if (r, c) in self.mines and (r, c) in self.revealed:
                    row_str += " * "
                elif (r, c) in self.flagged:
                    row_str += " F "
                elif (r, c) in self.revealed:
                    row_str += f" {self.numbers.get((r, c), 0)} "
                else:
                    row_str += " . "
            lines.append(row_str)
        return "\n".join(lines)
