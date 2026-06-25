import heapq
from ..base import Algorithm

# Thuật toán tìm kiếm tham lam (Greedy Best-First Search) ưu tiên ô ít rủi ro nhất.
class GreedyBestFirst(Algorithm):
    def __init__(self, board):
        super().__init__(board)
        self.name = "Greedy Best-First"
        self.category = "Informed Search"
        self.category_index = 2
        self.description = (
            "Tìm kiếm tham lam (Greedy Best-First): luôn chọn ô có xác suất "
            "mìn thấp nhất. Dùng hàng đợi ưu tiên, thuần tham lam không "
            "quan tâm chi phí đường đi."
        )

    # Tính toán xác suất chứa mìn cho tất cả các ô chưa mở trên bảng.
    def _calculate_all_probabilities(self):
        probs = {}
        unrevealed = self.board.get_all_unrevealed_unflagged()

        if not unrevealed:
            return probs

        remaining_mines = self.board.num_mines - len(
            self.board.flagged & self.board.mines
        )
        total_unknown = len(unrevealed)
        global_prob = remaining_mines / max(total_unknown, 1)

        for r, c in unrevealed:
            probs[(r, c)] = global_prob

        numbered_cells = self.board.get_revealed_numbered_cells()

        constraint_probs = {}
        constraint_counts = {}

        for r, c, number in numbered_cells:
            flagged_count = self.board.get_flagged_neighbor_count(r, c)
            unrevealed_neighbors = self.board.get_unrevealed_neighbors(r, c)
            unknown_count = len(unrevealed_neighbors)

            if unknown_count == 0:
                continue

            remaining = number - flagged_count
            local_prob = max(0.0, min(1.0, remaining / unknown_count))
            self.metrics['nodes_explored'] += 1

            for ur, uc in unrevealed_neighbors:
                if (ur, uc) not in constraint_probs:
                    constraint_probs[(ur, uc)] = 0.0
                    constraint_counts[(ur, uc)] = 0
                constraint_probs[(ur, uc)] += local_prob
                constraint_counts[(ur, uc)] += 1

        for cell in constraint_probs:
            probs[cell] = constraint_probs[cell] / constraint_counts[cell]

        return probs

    # Xây dựng hàng đợi ưu tiên để chọn các ô theo thứ tự xác suất mìn tăng dần.
    def _build_priority_queue(self):
        probs = self._calculate_all_probabilities()
        heap = []
        counter = 0
        for (r, c), prob in probs.items():
            heapq.heappush(heap, (prob, counter, r, c))
            counter += 1
        return heap

    # Vòng lặp giải chính của thuật toán tham lam.
    def _solve(self):
        center_r = self.board.rows // 2
        center_c = self.board.cols // 2
        result = self.do_reveal(center_r, center_c)
        if result == -1:
            return

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

            if self.board.is_complete():
                return

            heap = self._build_priority_queue()

            if not heap:
                break

            revealed = False
            while heap and not revealed:
                prob, _, r, c = heapq.heappop(heap)

                if self.board.is_revealed(r, c) or self.board.is_flagged(r, c):
                    continue

                if prob >= 1.0:
                    self.do_flag(r, c)
                    continue

                res = self.do_reveal(r, c)
                if res == -1:
                    return
                if res is not None:
                    revealed = True

            if not revealed and not heap:
                break
