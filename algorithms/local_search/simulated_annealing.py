import random
import math
from ..base import Algorithm

# Thuật toán mô phỏng luyện kim (Simulated Annealing) tìm cấu hình mìn tối ưu.
class SimulatedAnnealing(Algorithm):
    def __init__(self, board):
        super().__init__(board)
        self.name = "Simulated Annealing"
        self.category = "Local Search"
        self.category_index = 3
        self.description = (
            "Giống leo đồi nhưng thoát được cực trị địa phương. "
            "Nhiệt độ bắt đầu từ 1.0, giảm dần với hệ số 0.995. "
            "Bước tốt hơn luôn được chấp nhận, bước xấu hơn "
            "được chấp nhận với xác suất exp(-delta/T). "
            "Khi nhiệt độ nguội, dùng phân bổ cuối để xác định ô an toàn."
        )

    # Vòng lặp giải chính sử dụng mô phỏng luyện kim hạ nhiệt để thoát khỏi cực trị cục bộ.
    def _solve(self):
        rng = random.Random(1234)
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

            frontier_list = list(frontier)
            remaining_mines = self.board.num_mines - len(self.board.flagged)

            assignment = {}
            indices = list(range(len(frontier_list)))
            rng.shuffle(indices)
            mines_to_place = min(remaining_mines, len(frontier_list))
            mine_indices = set(indices[:mines_to_place])

            for i, cell in enumerate(frontier_list):
                assignment[cell] = (i in mine_indices)

            current_score = self._score_assignment(assignment)
            best_assignment = dict(assignment)
            best_score = current_score
            self.metrics['nodes_explored'] += 1

            temperature = 1.0
            cooling_rate = 0.995
            min_temperature = 0.001
            sa_iterations = min(len(frontier_list) * 20, 500)

            for sa_iter in range(sa_iterations):
                if temperature < min_temperature:
                    break

                flip_cell = rng.choice(frontier_list)
                assignment[flip_cell] = not assignment[flip_cell]

                new_score = self._score_assignment(assignment)
                self.metrics['nodes_explored'] += 1
                delta = new_score - current_score

                if delta > 0:
                    current_score = new_score
                elif delta == 0:
                    current_score = new_score
                else:
                    # Accept worse state with probability exp(delta/T)
                    acceptance_prob = math.exp(delta / temperature)
                    if rng.random() < acceptance_prob:
                        current_score = new_score
                    else:
                        assignment[flip_cell] = not assignment[flip_cell]

                if current_score > best_score:
                    best_score = current_score
                    best_assignment = dict(assignment)

            hill_iter = 0
            while hill_iter < len(frontier_list):
                hill_iter += 1
                best_flip_cell = None
                best_flip_score = best_score
                
                for cell in frontier_list:
                    best_assignment[cell] = not best_assignment[cell]
                    new_score = self._score_assignment(best_assignment)
                    self.metrics['nodes_explored'] += 1
                    
                    if new_score > best_flip_score:
                        best_flip_score = new_score
                        best_flip_cell = cell
                        
                    best_assignment[cell] = not best_assignment[cell]
                    
                if best_flip_cell is not None:
                    best_assignment[best_flip_cell] = not best_assignment[best_flip_cell]
                    best_score = best_flip_score
                else:
                    break

            is_perfect = True
            numbered_cells = self.board.get_revealed_numbered_cells()
            for r, c, number in numbered_cells:
                flagged_count = self.board.get_flagged_neighbor_count(r, c)
                remaining_needed = number - flagged_count
                unrevealed = self.board.get_unrevealed_neighbors(r, c)
                assigned_mines = sum(1 for cell in unrevealed if best_assignment.get(cell, False))
                if assigned_mines != remaining_needed:
                    is_perfect = False
                    break
                    
            if is_perfect:
                total_assigned = sum(1 for v in best_assignment.values() if v)
                expected = self.board.num_mines - len(self.board.flagged)
                if total_assigned > expected:
                    is_perfect = False

            revealed_any = False
            mine_cells = []

            if is_perfect:
                safe_cells = [cell for cell, is_mine in best_assignment.items()
                              if not is_mine
                              and not self.board.is_revealed(cell[0], cell[1])
                              and not self.board.is_flagged(cell[0], cell[1])]

                mine_cells = [cell for cell, is_mine in best_assignment.items()
                              if is_mine
                              and not self.board.is_revealed(cell[0], cell[1])
                              and not self.board.is_flagged(cell[0], cell[1])]

                for cell in mine_cells:
                    self.do_flag(cell[0], cell[1])

                for cell in safe_cells:
                    result = self.do_reveal(cell[0], cell[1])
                    if result is not None:
                        revealed_any = True

            if not revealed_any and not mine_cells:
                safest = self.get_safest_cell()
                if safest:
                    self.do_reveal(safest[0], safest[1])
                else:
                    unrevealed = self.board.get_all_unrevealed_unflagged()
                    if unrevealed:
                        cell = rng.choice(unrevealed)
                        self.do_reveal(cell[0], cell[1])

    # Tính điểm số cho một cấu hình gán mìn thử nghiệm dựa trên các ô số xung quanh.
    def _score_assignment(self, assignment):
        score = 0
        numbered_cells = self.board.get_revealed_numbered_cells()

        for r, c, number in numbered_cells:
            flagged_count = self.board.get_flagged_neighbor_count(r, c)
            remaining_needed = number - flagged_count

            unrevealed = self.board.get_unrevealed_neighbors(r, c)
            assigned_mines = sum(1 for cell in unrevealed
                                 if assignment.get(cell, False))

            if assigned_mines == remaining_needed:
                score += 10
            else:
                diff = abs(assigned_mines - remaining_needed)
                score -= diff * 5

        total_assigned = sum(1 for v in assignment.values() if v)
        expected = self.board.num_mines - len(self.board.flagged)
        score -= abs(total_assigned - expected) * 3

        return score
