from ..base import Algorithm

# Thuật toán duyệt theo chiều sâu (DFS) để khám phá bảng mìn theo đường sâu.
class DFSAlgorithm(Algorithm):
    def __init__(self, board):
        super().__init__(board)
        self.name = "DFS - Duyệt sâu"
        self.category = "Uninformed Search"
        self.category_index = 1
        self.description = (
            "Duyệt theo chiều sâu (DFS): dùng ngăn xếp LIFO, đi sâu vào "
            "một hướng trước khi quay lui. Tạo mẫu khám phá khác biệt so "
            "với BFS. Kết hợp luật cơ bản để giảm rủi ro."
        )

    # Vòng lặp giải chính sử dụng ngăn xếp LIFO kết hợp luật cơ bản và phỏng đoán ô an toàn.
    def _solve(self):
        center_r = self.board.rows // 2
        center_c = self.board.cols // 2
        result = self.do_reveal(center_r, center_c)
        if result == -1:
            return

        stack = []
        visited = set()
        visited.add((center_r, center_c))

        self._push_neighbors(center_r, center_c, stack, visited)

        for r, c in self.board.revealed:
            if (r, c) not in visited:
                visited.add((r, c))
                self._push_neighbors(r, c, stack, visited)

        max_iterations = 1000
        iteration = 0

        while not self.board.is_complete() and iteration < max_iterations:
            iteration += 1

            rules_applied = True
            while rules_applied:
                rules_applied = self.apply_basic_rules()
                if self.board.is_complete():
                    return
                if self.metrics['mines_hit'] > 0:
                    return

                for r, c in list(self.board.revealed):
                    if (r, c) not in visited:
                        visited.add((r, c))
                        self._push_neighbors(r, c, stack, visited)

            if self.board.is_complete():
                return

            revealed_from_stack = False

            while stack and not revealed_from_stack:
                cell_r, cell_c = stack.pop()
                self.metrics['nodes_explored'] += 1

                if self.board.is_revealed(cell_r, cell_c):
                    continue
                if self.board.is_flagged(cell_r, cell_c):
                    continue

                prob = self.get_mine_probability(cell_r, cell_c)

                if prob >= 1.0:
                    self.do_flag(cell_r, cell_c)
                    continue

                if prob == 0.0:
                    res = self.do_reveal(cell_r, cell_c)
                    if res == -1:
                        return
                    if res is not None:
                        revealed_from_stack = True
                        self._push_neighbors(cell_r, cell_c, stack, visited)
                        for r, c in self.board.revealed:
                            if (r, c) not in visited:
                                visited.add((r, c))
                                self._push_neighbors(r, c, stack, visited)

            if not revealed_from_stack and not stack:
                safest = self.get_safest_cell()
                if safest:
                    r, c = safest
                    res = self.do_reveal(r, c)
                    if res == -1:
                        return
                    if (r, c) not in visited:
                        visited.add((r, c))
                    self._push_neighbors(r, c, stack, visited)
                    for rev_r, rev_c in self.board.revealed:
                        if (rev_r, rev_c) not in visited:
                            visited.add((rev_r, rev_c))
                            self._push_neighbors(rev_r, rev_c, stack, visited)
                else:
                    break

    # Đẩy các ô lân cận chưa thăm của một ô vào ngăn xếp.
    def _push_neighbors(self, row, col, stack, visited):
        neighbors = self.board.get_neighbors(row, col)
        for nr, nc in reversed(neighbors):
            if (nr, nc) not in visited:
                if not self.board.is_revealed(nr, nc) and not self.board.is_flagged(nr, nc):
                    visited.add((nr, nc))
                    stack.append((nr, nc))
