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
        # Nước đi đầu tiên: luôn mở ô trung tâm để đảm bảo an toàn
        center_r = self.board.rows // 2
        center_c = self.board.cols // 2
        if self.do_reveal(center_r, center_c) == -1:
            return

        last_revealed = -1
        last_flagged = -1

        while not self.board.is_complete() and self.metrics['mines_hit'] == 0:
            current_revealed = len(self.board.revealed)
            current_flagged = len(self.board.flagged)
            if current_revealed == last_revealed and current_flagged == last_flagged:
                break
            last_revealed = current_revealed
            last_flagged = current_flagged

            # Áp dụng các luật logic cơ bản (nhất quán) từ lớp cơ sở
            progress_made = True
            while progress_made:
                progress_made = self.apply_basic_rules()
                if self.board.is_complete() or self.metrics['mines_hit'] > 0:
                    return

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
            
            if not border_cells:
                self._open_random()
                continue

            # Phân tách thành các cụm độc lập
            components = self._partition_border_cells(border_cells, numbers)
            
            safe_cells = []
            mine_cells = []
            undetermined_cells = []

            for comp in components:
                comp_set = set(comp)
                comp_numbers = {pos: val for pos, val in numbers.items()
                                if any(n in comp_set for n in self.board.get_neighbors(*pos))}

                for cell in comp:
                    self.metrics['nodes_explored'] += 1
                    
                    # Giả định cell là MÌN, xem có cấu hình nào hợp lệ không.
                    # Nếu KHÔNG có cấu hình hợp lệ nào tồn tại khi cell là MÌN, thì cell chắc chắn AN TOÀN!
                    can_be_mine = self._exists_valid_config_with_assumption(comp, comp_numbers, {cell: True})
                    
                    if not can_be_mine:
                        safe_cells.append(cell)
                        continue
                    
                    # Giả định cell là AN TOÀN, xem có cấu hình nào hợp lệ không.
                    # Nếu KHÔNG có cấu hình hợp lệ nào tồn tại khi cell là AN TOÀN, thì cell chắc chắn là MÌN!
                    can_be_safe = self._exists_valid_config_with_assumption(comp, comp_numbers, {cell: False})
                    
                    if not can_be_safe:
                        mine_cells.append(cell)
                    else:
                        undetermined_cells.append(cell)

            if mine_cells:
                for mc in mine_cells:
                    self.do_flag(*mc)
            elif safe_cells:
                for sc in safe_cells:
                    if self.do_reveal(*sc) == -1: return
            else:
                # Nếu không tìm thấy nước đi chắc chắn nào, chọn ô có xác suất chứa mìn thấp nhất trong các ô biên
                if undetermined_cells:
                    best_cell = None
                    best_prob = float('inf')
                    for cell in undetermined_cells:
                        prob = self.get_mine_probability(*cell)
                        if prob < best_prob:
                            best_prob = prob
                            best_cell = cell
                    
                    if best_cell:
                        if self.do_reveal(*best_cell) == -1: return
                    else:
                        self._open_random()
                else:
                    self._open_random()

    # Phân chia các ô biên thành các cụm độc lập bằng Union-Find.
    def _partition_border_cells(self, border_cells, numbers):
        parent = {v: v for v in border_cells}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        for (nr, nc), _ in numbers.items():
            neighbors = [n for n in self.board.get_neighbors(nr, nc) if n in parent]
            for i in range(1, len(neighbors)):
                union(neighbors[0], neighbors[i])

        groups = {}
        for v in border_cells:
            root = find(v)
            if root not in groups:
                groups[root] = []
            groups[root].append(v)

        return list(groups.values())

    # Kiểm tra xem có tồn tại bất kỳ cấu hình mìn hợp lệ nào thỏa mãn giả định đưa ra hay không.
    def _exists_valid_config_with_assumption(self, border_cells, numbers, assumptions):
        node_limit = 2000
        self._nodes_in_comp = 0
        self._limit_exceeded = False
        
        def backtrack(index, current_mines, current_safes):
            if self._limit_exceeded:
                return False

            self._nodes_in_comp += 1
            self.metrics['nodes_explored'] += 1
            if self._nodes_in_comp > node_limit:
                self._limit_exceeded = True
                return False

            if index == len(border_cells):
                return self._is_valid_config(current_mines, numbers)

            cell = border_cells[index]
            must_be_mine = assumptions.get(cell, None)
            
            # Cắt tỉa alpha-beta sớm bằng cách dừng ngay khi tìm được cấu hình hợp lệ đầu tiên
            if must_be_mine is not False:
                if self._can_place_mine(cell, current_mines, numbers):
                    current_mines.add(cell)
                    if backtrack(index + 1, current_mines, current_safes):
                        return True
                    current_mines.remove(cell)
                    
            if self._limit_exceeded:
                return False
                    
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
