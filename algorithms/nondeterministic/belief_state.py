import random
from itertools import combinations
from ..base import Algorithm

# Thuật toán tìm kiếm theo trạng thái niềm tin (Belief State) để giải quyết quan sát một phần.
class BeliefStateSearch(Algorithm):
    def __init__(self, board):
        super().__init__(board)
        self.name = "Belief State Search"
        self.category = "Belief / Nondeter."
        self.category_index = 4
        self.description = (
            "Xử lý quan sát một phần bằng trạng thái niềm tin. "
            "Duy trì tập cấu hình mìn phù hợp với quan sát hiện tại. "
            "Ô AN TOÀN nếu an toàn trong TẤT CẢ cấu hình. "
            "Ô MÌN nếu là mìn trong TẤT CẢ cấu hình. "
            "Nếu không chắc chắn, chọn ô an toàn trong NHIỀU cấu hình nhất."
        )

    # Vòng lặp giải chính ước lượng trạng thái niềm tin từ các cấu hình mìn phù hợp với quan sát.
    def _solve(self):
        rng = random.Random(42)
        MAX_ITERATIONS = 1000
        MAX_CONFIGS = 100

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

            frontier_list = sorted(frontier)
            remaining_mines = self.board.num_mines - len(self.board.flagged)

            configs = self._generate_consistent_configs(
                frontier_list, remaining_mines, MAX_CONFIGS, rng
            )

            if not configs:
                safest = self.get_safest_cell()
                if safest:
                    self.do_reveal(safest[0], safest[1])
                continue

            num_configs = len(configs)
            mine_count = {cell: 0 for cell in frontier_list}

            for config in configs:
                for cell in config:
                    if cell in mine_count:
                        mine_count[cell] += 1

            self.metrics['nodes_explored'] += num_configs

            safe_cells = [cell for cell in frontier_list
                          if mine_count.get(cell, 0) == 0
                          and not self.board.is_revealed(cell[0], cell[1])
                          and not self.board.is_flagged(cell[0], cell[1])]

            mine_cells = [cell for cell in frontier_list
                          if mine_count.get(cell, 0) == num_configs
                          and not self.board.is_revealed(cell[0], cell[1])
                          and not self.board.is_flagged(cell[0], cell[1])]

            for cell in mine_cells:
                self.do_flag(cell[0], cell[1])

            revealed_any = False
            for cell in safe_cells:
                result = self.do_reveal(cell[0], cell[1])
                if result is not None:
                    revealed_any = True

            if revealed_any or mine_cells:
                continue

            if frontier_list:
                candidates = [(cell, 1.0 - mine_count[cell] / num_configs)
                              for cell in frontier_list
                              if not self.board.is_revealed(cell[0], cell[1])
                              and not self.board.is_flagged(cell[0], cell[1])]

                if candidates:
                    candidates.sort(key=lambda x: -x[1])
                    best_cell = candidates[0][0]
                    self.do_reveal(best_cell[0], best_cell[1])
                else:
                    unrevealed = self.board.get_all_unrevealed_unflagged()
                    if unrevealed:
                        cell = rng.choice(unrevealed)
                        self.do_reveal(cell[0], cell[1])

    # Sinh các cấu hình phân bổ mìn trên biên thỏa mãn tất cả các ràng buộc ô số đã biết.
    def _generate_consistent_configs(self, frontier, remaining_mines, max_configs, rng):
        configs = []
        numbered_cells = self.board.get_revealed_numbered_cells()

        if len(frontier) <= 20:
            mines_in_frontier = min(remaining_mines, len(frontier))
            max_check = max_configs * 50

            checked = 0
            for num_mines_in_f in range(max(0, mines_in_frontier - 2),
                                         min(len(frontier), mines_in_frontier + 3) + 1):
                if num_mines_in_f < 0 or num_mines_in_f > len(frontier):
                    continue
                if len(configs) >= max_configs:
                    break

                for combo in combinations(frontier, num_mines_in_f):
                    checked += 1
                    if checked > max_check:
                        break

                    mine_set = set(combo)
                    if self._is_consistent(mine_set, numbered_cells):
                        configs.append(mine_set)
                        if len(configs) >= max_configs:
                            break

        attempts = 0
        max_attempts = max_configs * 10
        while len(configs) < max_configs and attempts < max_attempts:
            attempts += 1
            num_mines_in_frontier = min(remaining_mines, len(frontier))
            if num_mines_in_frontier <= 0:
                config = set()
            elif num_mines_in_frontier >= len(frontier):
                config = set(frontier)
            else:
                sample = rng.sample(frontier, num_mines_in_frontier)
                config = set(sample)

            if self._is_consistent(config, numbered_cells):
                config_frozen = frozenset(config)
                is_dup = any(frozenset(c) == config_frozen for c in configs)
                if not is_dup:
                    configs.append(config)

        return configs

    # Kiểm tra xem một phân bổ mìn giả định có nhất quán với tất cả các ô số đã biết lân cận hay không.
    def _is_consistent(self, mine_set, numbered_cells):
        for r, c, number in numbered_cells:
            flagged_count = self.board.get_flagged_neighbor_count(r, c)
            remaining_needed = number - flagged_count

            unrevealed = self.board.get_unrevealed_neighbors(r, c)
            mines_in_neighbors = sum(1 for cell in unrevealed if cell in mine_set)

            if mines_in_neighbors != remaining_needed:
                return False

        return True
