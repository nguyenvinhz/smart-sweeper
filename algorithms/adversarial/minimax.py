import random
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

            # Phân tách thành các cụm liên thông độc lập để giảm thiểu không gian tìm kiếm
            components = self._partition_border_cells(border_cells, numbers)
            
            best_score = -float('inf')
            best_cell = None
            safe_cells = []
            mine_cells = []

            for comp in components:
                comp_set = set(comp)
                comp_numbers = {pos: val for pos, val in numbers.items()
                                if any(n in comp_set for n in self.board.get_neighbors(*pos))}
                
                valid_configs = self._get_valid_configs(comp, comp_numbers)
                
                if not valid_configs:
                    # Nếu cụm quá lớn/phức tạp hoặc không tìm thấy cấu hình hợp lệ, dùng xác suất cơ bản làm dự phòng
                    for cell in comp:
                        prob = self.get_mine_probability(*cell)
                        score = -prob
                        if score > best_score:
                            best_score = score
                            best_cell = cell
                    continue

                mine_counts = {cell: 0 for cell in comp}
                for cfg in valid_configs:
                    for cell in cfg:
                        mine_counts[cell] += 1

                for cell in comp:
                    self.metrics['nodes_explored'] += 1
                    can_be_mine = any(cell in cfg for cfg in valid_configs)
                    can_be_safe = any(cell not in cfg for cfg in valid_configs)
                    
                    if not can_be_mine:
                        safe_cells.append(cell)
                    elif not can_be_safe:
                        mine_cells.append(cell)
                    else:
                        prob = mine_counts[cell] / len(valid_configs)
                        score = -prob
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

    # Tìm tất cả các cấu hình gán mìn biên hợp lệ của cụm bằng cách quay lui.
    def _get_valid_configs(self, border_cells, numbers):
        valid_configs = []
        node_limit = 2000
        self._nodes_in_comp = 0
        self._limit_exceeded = False
        
        def backtrack(index, current_mines):
            if self._limit_exceeded:
                return

            self._nodes_in_comp += 1
            self.metrics['nodes_explored'] += 1
            if self._nodes_in_comp > node_limit:
                self._limit_exceeded = True
                return

            if index == len(border_cells):
                if self._is_valid_config(current_mines, numbers):
                    valid_configs.append(set(current_mines))
                return

            cell = border_cells[index]
            
            if self._can_place_mine(cell, current_mines, numbers):
                current_mines.add(cell)
                backtrack(index + 1, current_mines)
                current_mines.remove(cell)
            
            if self._limit_exceeded:
                return

            if self._can_place_safe(cell, current_mines, numbers, border_cells, index):
                backtrack(index + 1, current_mines)

        backtrack(0, set())
        if self._limit_exceeded:
            return []
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
