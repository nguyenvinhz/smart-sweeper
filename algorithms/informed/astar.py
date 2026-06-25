import heapq
from ..base import Algorithm

# Thuật toán tìm kiếm A* để giải game Minesweeper.
class AStarSearch(Algorithm):
    def __init__(self, board):
        super().__init__(board)
        self.name = "A* Search"
        self.category = "Informed Search"
        self.category_index = 2
        self.description = (
            "Tìm kiếm A*: f(n) = g(n) + h(n), kết hợp chi phí thực tế "
            "(số bước đã đi) với heuristic (ước lượng rủi ro còn lại). "
            "Cân bằng hơn tìm kiếm tham lam thuần túy."
        )
        self.reveal_count = 0

    # Tính giá trị heuristic h(n) dựa trên xác suất mìn và số ô an toàn còn lại.
    def _calculate_heuristic(self, row, col):
        prob = self._get_constraint_probability(row, col)
        revealed_safe, total_safe = self.board.get_progress()
        remaining = max(1, total_safe - revealed_safe)
        # h(n) = probability * remaining
        return prob * remaining

    # Tính xác suất ô chứa mìn dựa trên các ràng buộc lân cận hoặc trung bình toàn cục.
    def _get_constraint_probability(self, row, col):
        if self.board.is_revealed(row, col) or self.board.is_flagged(row, col):
            return 0.0

        probs_from_constraints = []

        for nr, nc in self.board.get_neighbors(row, col):
            if not self.board.is_revealed(nr, nc):
                continue
            if (nr, nc) in self.board.mines:
                continue

            number = self.board.numbers.get((nr, nc), 0)
            if number == 0:
                return 0.0

            flagged = self.board.get_flagged_neighbor_count(nr, nc)
            unknown = self.board.get_unknown_neighbor_count(nr, nc)

            if unknown > 0:
                remaining_mines = number - flagged
                local_prob = max(0.0, min(1.0, remaining_mines / unknown))
                probs_from_constraints.append(local_prob)

            self.metrics['nodes_explored'] += 1

        if probs_from_constraints:
            return sum(probs_from_constraints) / len(probs_from_constraints)

        total_unknown = len(self.board.get_all_unrevealed_unflagged())
        remaining_mines = self.board.num_mines - len(
            self.board.flagged & self.board.mines
        )
        if total_unknown > 0:
            return remaining_mines / total_unknown
        return 0.0

    # Xây dựng hàng đợi ưu tiên cho A* với điểm f(n) = g(n) + h(n).
    def _build_astar_queue(self):
        heap = []
        counter = 0
        unrevealed = self.board.get_all_unrevealed_unflagged()
        g = self.reveal_count

        for r, c in unrevealed:
            h = self._calculate_heuristic(r, c)
            # f(n) = g(n) + h(n)
            f = g + h
            heapq.heappush(heap, (f, counter, r, c))
            counter += 1

        return heap

    # Vòng lặp giải chính của A* kết hợp luật cơ bản và hàng đợi ưu tiên.
    def _solve(self):
        center_r = self.board.rows // 2
        center_c = self.board.cols // 2
        result = self.do_reveal(center_r, center_c)
        if result == -1:
            return
        self.reveal_count += 1

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

            heap = self._build_astar_queue()

            if not heap:
                break

            revealed = False
            while heap and not revealed:
                f_score, _, r, c = heapq.heappop(heap)

                if self.board.is_revealed(r, c) or self.board.is_flagged(r, c):
                    continue

                prob = self._get_constraint_probability(r, c)

                if prob >= 1.0:
                    self.do_flag(r, c)
                    continue

                res = self.do_reveal(r, c)
                if res == -1:
                    return
                if res is not None:
                    self.reveal_count += 1
                    revealed = True

            if not revealed and not heap:
                break
