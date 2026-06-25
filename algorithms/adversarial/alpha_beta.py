import random
from ..base import Algorithm

# Đại lý AI tìm kiếm đối kháng sử dụng thuật toán cắt tỉa Alpha-Beta.
class AlphaBetaAgent(Algorithm):
    def __init__(self, board):
        super().__init__(board)
        self.name = "Alpha-Beta Pruning"
        self.category = "Adversarial Search"
        self.category_index = 5
        self.description = "Dựa trên Minimax, nhưng áp dụng cắt tỉa Alpha-Beta: dừng tìm kiếm ngay khi Môi trường (Min) chứng minh được một ô có khả năng là mìn, giúp tìm ô an toàn nhanh hơn."

    # Vòng lặp giải chính tìm kiếm ô an toàn/ô mìn thông qua cắt tỉa giả định.
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

            safe_cells = []
            mine_cells = []

            for cell in border_cells:
                self.metrics['nodes_explored'] += 1
                
                can_be_mine = self._exists_valid_config_with_assumption(border_cells, numbers, {cell: True})
                
                if not can_be_mine:
                    safe_cells.append(cell)
                    continue
                
                can_be_safe = self._exists_valid_config_with_assumption(border_cells, numbers, {cell: False})
                
                if not can_be_safe:
                    mine_cells.append(cell)

            if mine_cells:
                for mc in mine_cells:
                    self.do_flag(*mc)
            elif safe_cells:
                for sc in safe_cells:
                    if self.do_reveal(*sc) == -1: return
            else:
                r, c = random.choice(border_cells)
                self.do_reveal(r, c)

    # Áp dụng nhanh các quy tắc logic cơ bản để cắm cờ hoặc mở ô.
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

    # Kiểm tra xem có tồn tại bất kỳ cấu hình mìn hợp lệ nào thỏa mãn giả định đưa ra hay không.
    def _exists_valid_config_with_assumption(self, border_cells, numbers, assumptions):
        def backtrack(index, current_mines, current_safes):
            self.metrics['nodes_explored'] += 1
            if index == len(border_cells):
                return self._is_valid_config(current_mines, numbers)

            cell = border_cells[index]
            must_be_mine = assumptions.get(cell, None)
            
            if must_be_mine is not False:
                if self._can_place_mine(cell, current_mines, numbers):
                    current_mines.add(cell)
                    if backtrack(index + 1, current_mines, current_safes):
                        return True
                    current_mines.remove(cell)
                    
            if must_be_mine is not True:
                if self._can_place_safe(cell, current_mines, numbers, border_cells, index):
                    current_safes.add(cell)
                    if backtrack(index + 1, current_mines, current_safes):
                        return True
                    current_safes.remove(cell)
                    
            return False

        return backtrack(0, set(), set())

    # Kiểm tra tính khả thi khi gán mìn tại ô biên.
    def _can_place_mine(self, cell, current_mines, numbers):
        for (r, c), rem in numbers.items():
            if abs(r - cell[0]) <= 1 and abs(c - cell[1]) <= 1:
                count = sum(1 for m in current_mines if abs(r - m[0]) <= 1 and abs(c - m[1]) <= 1)
                if count >= rem:
                    return False
        return True

    # Kiểm tra tính khả thi khi gán an toàn tại ô biên.
    def _can_place_safe(self, cell, current_mines, numbers, border_cells, index):
        for (r, c), rem in numbers.items():
            if abs(r - cell[0]) <= 1 and abs(c - cell[1]) <= 1:
                count = sum(1 for m in current_mines if abs(r - m[0]) <= 1 and abs(c - m[1]) <= 1)
                rem_border = sum(1 for i in range(index + 1, len(border_cells)) 
                               if abs(r - border_cells[i][0]) <= 1 and abs(c - border_cells[i][1]) <= 1)
                if count + rem_border < rem:
                    return False
        return True

    # Xác nhận xem cấu hình mìn giả định có hoàn toàn thỏa mãn các ô số đã biết.
    def _is_valid_config(self, current_mines, numbers):
        for (r, c), rem in numbers.items():
            count = sum(1 for m in current_mines if abs(r - m[0]) <= 1 and abs(c - m[1]) <= 1)
            if count != rem:
                return False
        return True

    # Mở ngẫu nhiên một ô chưa mở khi không tìm thấy lựa chọn logic nào.
    def _open_random(self):
        hidden = []
        for r in range(self.board.rows):
            for c in range(self.board.cols):
                if not self.board.is_revealed(r, c) and not self.board.is_flagged(r, c):
                    hidden.append((r, c))
        if hidden:
            r, c = random.choice(hidden)
            self.do_reveal(r, c)
