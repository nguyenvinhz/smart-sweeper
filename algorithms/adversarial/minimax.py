import random
from itertools import combinations
from ..base import Algorithm

# Đại lý AI tìm kiếm đối kháng sử dụng thuật toán Minimax.
class MinimaxAgent(Algorithm):
    def __init__(self, board):
        super().__init__(board)
        self.name = "Minimax Search"
        self.category = "Adversarial Search"
        self.category_index = 5
        self.description = "Sử dụng Minimax: Max (Agent) cố gắng chọn ô an toàn, Min (Môi trường) cố gắng đặt mìn vào ô đó trong một cấu hình hợp lệ."

    # Vòng lặp giải chính đánh giá tất cả các cấu hình biên bằng minimax để chọn ô tối ưu.
    def _solve(self):
        while not self.board.is_complete() and self.metrics['mines_hit'] == 0:
            border_cells = set()
            numbers = {}
            for r in range(self.board.rows):
                for c in range(self.board.cols):
                    if self.board.is_revealed(r, c):
                        num = self.board.numbers.get((r, c), 0)
                        if num > 0:
                            hidden_neighbors = self.board.get_neighbors(r, c, hidden_only=True)
                            flagged_neighbors = [n for n in self.board.get_neighbors(r, c) if self.board.is_flagged(*n)]
                            if hidden_neighbors:
                                border_cells.update(hidden_neighbors)
                                numbers[(r, c)] = num - len(flagged_neighbors)
                                
            border_cells = list(border_cells)
            
            progress_made = self._apply_basic_rules(numbers)
            if progress_made:
                continue

            if not border_cells:
                self._open_random()
                continue

            valid_configs = self._get_valid_configs(border_cells, numbers)
            
            if not valid_configs:
                self._open_random()
                continue

            best_score = -float('inf')
            best_cell = None
            safe_cells = []
            mine_cells = []
            
            mine_counts = {cell: 0 for cell in border_cells}
            for cfg in valid_configs:
                for cell in cfg:
                    mine_counts[cell] += 1

            for cell in border_cells:
                self.metrics['nodes_explored'] += 1
                can_be_mine = any(cell in cfg for cfg in valid_configs)
                can_be_safe = any(cell not in cfg for cfg in valid_configs)
                
                if not can_be_mine:
                    score = 1
                    safe_cells.append(cell)
                elif not can_be_safe:
                    score = -1
                    mine_cells.append(cell)
                else:
                    score = - (mine_counts[cell] / len(valid_configs))
                
                if score > best_score:
                    best_score = score
                    best_cell = cell

            if mine_cells:
                for mc in mine_cells:
                    self.do_flag(*mc)
            elif safe_cells:
                for sc in safe_cells:
                    if self.do_reveal(*sc) == -1: return
            else:
                if best_cell:
                    if self.do_reveal(*best_cell) == -1: return
                else:
                    self._open_random()

    # Áp dụng nhanh luật nhất quán cơ bản để cắm cờ hoặc mở ô.
    def _apply_basic_rules(self, numbers):
        made_progress = False
        for (r, c), remaining_mines in numbers.items():
            hidden = self.board.get_neighbors(r, c, hidden_only=True)
            if len(hidden) == remaining_mines and remaining_mines > 0:
                for h in hidden:
                    self.do_flag(*h)
                    made_progress = True
            elif remaining_mines == 0 and len(hidden) > 0:
                for h in hidden:
                    if self.do_reveal(*h) == -1: return True
                    made_progress = True
        return made_progress

    # Tìm tất cả các cấu hình gán mìn biên hợp lệ bằng cách quay lui.
    def _get_valid_configs(self, border_cells, numbers):
        valid_configs = []
        
        def backtrack(index, current_mines):
            self.metrics['nodes_explored'] += 1
            if index == len(border_cells):
                if self._is_valid_config(current_mines, numbers):
                    valid_configs.append(set(current_mines))
                return

            cell = border_cells[index]
            
            if self._can_place_mine(cell, current_mines, numbers):
                current_mines.add(cell)
                backtrack(index + 1, current_mines)
                current_mines.remove(cell)
            
            if self._can_place_safe(cell, current_mines, numbers, border_cells, index):
                backtrack(index + 1, current_mines)

        backtrack(0, set())
        return valid_configs
        
    # Kiểm tra xem có thể đặt mìn tại ô biên mà không vi phạm ràng buộc ô số hay không.
    def _can_place_mine(self, cell, current_mines, numbers):
        for (r, c), rem in numbers.items():
            if abs(r - cell[0]) <= 1 and abs(c - cell[1]) <= 1:
                count = sum(1 for m in current_mines if abs(r - m[0]) <= 1 and abs(c - m[1]) <= 1)
                if count >= rem:
                    return False
        return True

    # Kiểm tra xem việc bỏ trống ô biên (an toàn) có khả thi với ràng buộc ô số hay không.
    def _can_place_safe(self, cell, current_mines, numbers, border_cells, index):
        for (r, c), rem in numbers.items():
            if abs(r - cell[0]) <= 1 and abs(c - cell[1]) <= 1:
                count = sum(1 for m in current_mines if abs(r - m[0]) <= 1 and abs(c - m[1]) <= 1)
                rem_border = sum(1 for i in range(index + 1, len(border_cells)) 
                               if abs(r - border_cells[i][0]) <= 1 and abs(c - border_cells[i][1]) <= 1)
                if count + rem_border < rem:
                    return False
        return True

    # Kiểm tra xem cấu hình mìn hiện tại có thỏa mãn toàn bộ ô số biên hay không.
    def _is_valid_config(self, current_mines, numbers):
        for (r, c), rem in numbers.items():
            count = sum(1 for m in current_mines if abs(r - m[0]) <= 1 and abs(c - m[1]) <= 1)
            if count != rem:
                return False
        return True

    # Chọn mở ngẫu nhiên một ô chưa mở khi không thể suy luận logic.
    def _open_random(self):
        hidden = []
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if not self.board.is_revealed(r, c) and not self.board.is_flagged(r, c):
                    hidden.append((r, c))
        if hidden:
            r, c = random.choice(hidden)
            self.do_reveal(r, c)
