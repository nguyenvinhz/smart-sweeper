from collections import deque
from ..base import Algorithm

# Thuật toán duyệt theo chiều rộng (BFS) để khám phá bảng mìn theo từng lớp.
class BFSAlgorithm(Algorithm):
    def __init__(self, board):
        super().__init__(board)
        self.name = "BFS - Duyệt rộng"
        self.category = "Uninformed Search"
        self.category_index = 1
        self.description = (
            "Duyệt theo chiều rộng (BFS): khám phá bảng mìn theo từng lớp "
            "từ ô trung tâm. Dùng hàng đợi FIFO, ưu tiên mở ô gần nhất "
            "trước. Kết hợp luật cơ bản để đảm bảo an toàn."
        )

    # Vòng lặp giải chính sử dụng hàng đợi FIFO kết hợp luật cơ bản và phỏng đoán ô an toàn.
    def _solve(self):
        center_r = self.board.rows // 2
        center_c = self.board.cols // 2
        result = self.do_reveal(center_r, center_c)
        if result == -1:
            return

        queue = deque()
        visited = set()
        visited.add((center_r, center_c))

        self._enqueue_neighbors(center_r, center_c, queue, visited)

        for r, c in self.board.revealed:
            if (r, c) not in visited:
                visited.add((r, c))
                self._enqueue_neighbors(r, c, queue, visited)

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
                        self._enqueue_neighbors(r, c, queue, visited)

            if self.board.is_complete():
                return

            revealed_from_queue = False

            while queue and not revealed_from_queue:
                cell_r, cell_c = queue.popleft()
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
                        revealed_from_queue = True
                        self._enqueue_neighbors(cell_r, cell_c, queue, visited)
                        for r, c in self.board.revealed:
                            if (r, c) not in visited:
                                visited.add((r, c))
                                self._enqueue_neighbors(r, c, queue, visited)

            if not revealed_from_queue and not queue:
                safest = self.get_safest_cell()
                if safest:
                    r, c = safest
                    res = self.do_reveal(r, c)
                    if res == -1:
                        return
                    if (r, c) not in visited:
                        visited.add((r, c))
                    self._enqueue_neighbors(r, c, queue, visited)
                    for rev_r, rev_c in self.board.revealed:
                        if (rev_r, rev_c) not in visited:
                            visited.add((rev_r, rev_c))
                            self._enqueue_neighbors(rev_r, rev_c, queue, visited)
                else:
                    break

    # Đưa các ô lân cận chưa thăm của một ô vào hàng đợi.
    def _enqueue_neighbors(self, row, col, queue, visited):
        for nr, nc in self.board.get_neighbors(row, col):
            if (nr, nc) not in visited:
                if not self.board.is_revealed(nr, nc) and not self.board.is_flagged(nr, nc):
                    visited.add((nr, nc))
                    queue.append((nr, nc))
