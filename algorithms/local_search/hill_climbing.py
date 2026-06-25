import random
from ..base import Algorithm

# Thuật toán leo đồi (Hill Climbing) tìm kiếm phân bổ mìn tối ưu.
class HillClimbing(Algorithm):
    def __init__(self, board):
        super().__init__(board)
        self.name = "Hill Climbing"
        self.category = "Local Search"
        self.category_index = 3
        self.description = (
            "Xử lý cấu hình mìn như bài toán tối ưu. "
            "Bắt đầu với phân bổ ngẫu nhiên, sau đó leo đồi "
            "bằng cách lật trạng thái từng ô (mìn↔an toàn). "
            "Chỉ chấp nhận bước cải thiện (steepest ascent). "
            "Khi hội tụ, mở các ô được đánh dấu an toàn."
        )

    # Vòng lặp giải chính sử dụng thuật toán leo đồi tìm cấu hình mìn phù hợp ràng buộc nhất.
    def _solve(self):
        rng = random.Random(42)
        MAX_ITERATIONS = 1000

        center_r, center_c = self.board.rows // 2, self.board.cols // 2
        self.do_reveal(center_r, center_c)

        self.apply_basic_rules()

        iteration = 0
        while not self.board.is_complete() and iteration < MAX_ITERATIONS:
            iteration += 1

            changed = True
            while changed and iteration < MAX_ITERATIONS:
                changed = self.apply_basic_rules()
                iteration += 1

            if self.board.is_complete():
                break

            frontier = self.board.get_frontier_cells()
            if not frontier:
                unrevealed = self.board.get_all_unrevealed_unflagged()
                if unrevealed:
                    cell = rng.choice(unrevealed)
                    self.do_reveal(cell[0], cell[1])
                continue

            total_mines = self.board.num_mines
            flagged_mines = len(self.board.flagged)
            remaining_mines = total_mines - flagged_mines

            assignment = {}
            frontier_list = list(frontier)
            rng.shuffle(frontier_list)

            mines_to_place = min(remaining_mines, len(frontier_list))
            for i, cell in enumerate(frontier_list):
                assignment[cell] = (i < mines_to_place)

            best_score = self._score_assignment(assignment)
            self.metrics['nodes_explored'] += 1

            hill_iterations = 0
            max_hill_iter = min(len(frontier_list) * 10, 500)

            improved = True
            while improved and hill_iterations < max_hill_iter:
                improved = False
                hill_iterations += 1

                best_flip_cell = None
                best_flip_score = best_score

                for cell in frontier_list:
                    assignment[cell] = not assignment[cell]
                    new_score = self._score_assignment(assignment)
                    self.metrics['nodes_explored'] += 1

                    if new_score > best_flip_score:
                        best_flip_score = new_score
                        best_flip_cell = cell

                    assignment[cell] = not assignment[cell]

                if best_flip_cell is not None:
                    assignment[best_flip_cell] = not assignment[best_flip_cell]
                    best_score = best_flip_score
                    improved = True

            safe_cells = [cell for cell, is_mine in assignment.items()
                          if not is_mine
                          and not self.board.is_revealed(cell[0], cell[1])
                          and not self.board.is_flagged(cell[0], cell[1])]

            mine_cells = [cell for cell, is_mine in assignment.items()
                          if is_mine
                          and not self.board.is_revealed(cell[0], cell[1])
                          and not self.board.is_flagged(cell[0], cell[1])]

            for cell in mine_cells:
                self.do_flag(cell[0], cell[1])

            revealed_any = False
            for cell in safe_cells:
                result = self.do_reveal(cell[0], cell[1])
                if result is not None:
                    revealed_any = True
                    if result == -1:
                        pass

            if not revealed_any and not mine_cells:
                unrevealed = self.board.get_all_unrevealed_unflagged()
                if unrevealed:
                    safest = self.get_safest_cell()
                    if safest:
                        self.do_reveal(safest[0], safest[1])
                    else:
                        cell = rng.choice(unrevealed)
                        self.do_reveal(cell[0], cell[1])

    # Tính điểm cho một phương án phân bổ mìn dựa trên mức độ thỏa mãn các ô số trên bảng.
    def _score_assignment(self, assignment):
        score = 0
        numbered_cells = self.board.get_revealed_numbered_cells()

        for r, c, number in numbered_cells:
            flagged_count = self.board.get_flagged_neighbor_count(r, c)
            remaining_mines_needed = number - flagged_count

            unrevealed_neighbors = self.board.get_unrevealed_neighbors(r, c)
            assigned_mines = sum(1 for cell in unrevealed_neighbors
                                 if assignment.get(cell, False))

            if assigned_mines == remaining_mines_needed:
                score += 10
            else:
                diff = abs(assigned_mines - remaining_mines_needed)
                score -= diff * 5

            if remaining_mines_needed < 0:
                score -= 20

        total_assigned_mines = sum(1 for v in assignment.values() if v)
        total_flagged = len(self.board.flagged)
        expected_remaining = self.board.num_mines - total_flagged

        mine_diff = abs(total_assigned_mines - expected_remaining)
        score -= mine_diff * 3

        return score
