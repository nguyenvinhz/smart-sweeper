import random
from ..base import Algorithm

# Thuật toán cây tìm kiếm AND-OR để tìm chiến lược giải tối ưu.
class AndOrSearch(Algorithm):
    def __init__(self, board):
        super().__init__(board)
        self.name = "AND-OR Search"
        self.category = "Belief / Nondeter."
        self.category_index = 4
        self.description = (
            "Lập kế hoạch dự phòng bằng cây AND-OR. "
            "OR node: agent chọn ô để mở (lựa chọn của agent). "
            "AND node: mọi kết quả có thể phải được xử lý (lựa chọn của tự nhiên). "
            "Đánh giá: số ô mở an toàn trong trường hợp xấu nhất. "
            "Tìm chiến lược tốt bất kể kết quả thực tế."
        )

    # Vòng lặp giải chính đánh giá các ô biên dựa trên cây AND-OR.
    def _solve(self):
        rng = random.Random(42)
        MAX_ITERATIONS = 1000
        MAX_DEPTH = 3

        center_r, center_c = self.board.rows // 2, self.board.cols // 2
        self.do_reveal(center_r, center_c)

        self.apply_basic_rules()

        iteration = 0
        while not self.board.is_complete() and iteration < MAX_ITERATIONS:
            iteration += 1

            changed = True
            sub_iter = 0
            while changed and sub_iter < 50:
                changed = self.apply_basic_rules()
                sub_iter += 1

            if self.board.is_complete():
                break

            frontier = self.board.get_frontier_cells()
            if not frontier:
                unrevealed = self.board.get_all_unrevealed_unflagged()
                if unrevealed:
                    cell = rng.choice(unrevealed)
                    self.do_reveal(cell[0], cell[1])
                continue

            candidates = sorted(frontier)
            if len(candidates) > 8:
                scored = []
                for cell in candidates:
                    r, c = cell
                    info_score = len(self.board.get_neighbors(r, c)) - \
                                 len(self.board.get_unrevealed_neighbors(r, c))
                    scored.append((cell, info_score))
                scored.sort(key=lambda x: -x[1])
                candidates = [s[0] for s in scored[:8]]

            best_cell = None
            best_value = float('-inf')

            for cell in candidates:
                # OR node: agent choice
                value = self._and_or_evaluate(cell, MAX_DEPTH, rng)
                self.metrics['nodes_explored'] += 1

                if value > best_value:
                    best_value = value
                    best_cell = cell

            if best_cell and best_value > 0:
                result = self.do_reveal(best_cell[0], best_cell[1])
                if result is not None and result >= 0:
                    self.apply_basic_rules()
            else:
                safest = self.get_safest_cell()
                if safest:
                    self.do_reveal(safest[0], safest[1])

    # Đánh giá đệ quy giá trị kỳ vọng tại nút AND-OR trong cây tìm kiếm.
    def _and_or_evaluate(self, cell, depth, rng):
        r, c = cell

        if self.board.is_revealed(r, c) or self.board.is_flagged(r, c):
            return 0

        mine_prob = self.get_mine_probability(r, c)

        if depth <= 0:
            return 1.0 - mine_prob

        # AND node: environment choice (safe vs mine)
        safe_value = 1.0

        if depth > 1:
            neighbor_unrevealed = self.board.get_unrevealed_neighbors(r, c)
            neighbor_unrevealed = [n for n in neighbor_unrevealed
                                    if n != cell
                                    and not self.board.is_revealed(n[0], n[1])
                                    and not self.board.is_flagged(n[0], n[1])]

            if neighbor_unrevealed:
                # OR node: agent choice of next step
                best_next = float('-inf')
                for next_cell in neighbor_unrevealed[:4]:
                    next_value = self._and_or_evaluate(next_cell, depth - 1, rng)
                    self.metrics['nodes_explored'] += 1
                    best_next = max(best_next, next_value)

                if best_next > float('-inf'):
                    safe_value += best_next * 0.5

        mine_value = -10.0
        # Expected value calculation
        and_value = (1.0 - mine_prob) * safe_value + mine_prob * mine_value

        return and_value

    # Đánh giá chất lượng trạng thái bảng hiện tại bằng số ô an toàn đã mở.
    def _evaluate_board_state(self):
        revealed_safe, total_safe = self.board.get_progress()
        return revealed_safe
