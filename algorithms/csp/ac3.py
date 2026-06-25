import random
from collections import deque
from ..base import Algorithm

# Thuật toán AC-3 giải game dưới dạng bài toán thỏa mãn ràng buộc (CSP).
class AC3Algorithm(Algorithm):
    def __init__(self, board):
        super().__init__(board)
        self.name = "AC-3"
        self.category = "CSP / Constraint"
        self.category_index = 5
        self.description = (
            "Tính nhất quán cung (Arc Consistency) với lan truyền ràng buộc. "
            "Tạo đồ thị ràng buộc: mỗi ô số tạo ràng buộc lên các ô chưa biết lân cận. "
            "AC-3: duy trì hàng đợi cung, loại giá trị không có hỗ trợ. "
            "Miền trở thành singleton → ô được xác định. "
            "Khi AC-3 không đủ, kết hợp quay lui đơn giản."
        )

    # Vòng lặp giải chính khởi dựng đồ thị ràng buộc, chạy AC-3 và quay lui khi cần.
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

            frontier_set = set(frontier)
            domains = {cell: {True, False} for cell in frontier}
            constraints = self._build_constraints(frontier_set)

            if not constraints:
                safest = self.get_safest_cell()
                if safest:
                    self.do_reveal(safest[0], safest[1])
                continue

            ac3_result = self._ac3(domains, constraints)

            if not ac3_result:
                safest = self.get_safest_cell()
                if safest:
                    self.do_reveal(safest[0], safest[1])
                continue

            determined_safe = []
            determined_mine = []
            undetermined = []

            for cell in frontier:
                if cell not in domains:
                    continue
                domain = domains[cell]
                if len(domain) == 1:
                    if False in domain:
                        determined_safe.append(cell)
                    else:
                        determined_mine.append(cell)
                elif len(domain) == 0:
                    pass
                else:
                    undetermined.append(cell)

            for cell in determined_mine:
                if not self.board.is_flagged(cell[0], cell[1]):
                    self.do_flag(cell[0], cell[1])

            revealed_any = False
            for cell in determined_safe:
                if not self.board.is_revealed(cell[0], cell[1]) and \
                   not self.board.is_flagged(cell[0], cell[1]):
                    result = self.do_reveal(cell[0], cell[1])
                    if result is not None:
                        revealed_any = True

            if revealed_any or determined_mine:
                continue

            if undetermined:
                bt_vars = sorted(undetermined)[:20]
                bt_constraints = [
                    (pos, cells, needed) for pos, cells, needed in constraints
                    if any(c in set(bt_vars) for c in cells)
                ]

                safe_in_all, mine_in_all = self._simple_backtrack(
                    bt_vars, bt_constraints, domains
                )

                for cell in mine_in_all:
                    if not self.board.is_flagged(cell[0], cell[1]):
                        self.do_flag(cell[0], cell[1])

                for cell in safe_in_all:
                    if not self.board.is_revealed(cell[0], cell[1]) and \
                       not self.board.is_flagged(cell[0], cell[1]):
                        result = self.do_reveal(cell[0], cell[1])
                        if result is not None:
                            revealed_any = True

                if revealed_any or mine_in_all:
                    continue

            safest = self.get_safest_cell()
            if safest:
                self.do_reveal(safest[0], safest[1])
            else:
                unrevealed = self.board.get_all_unrevealed_unflagged()
                if unrevealed:
                    cell = rng.choice(unrevealed)
                    self.do_reveal(cell[0], cell[1])

    # Tạo các ràng buộc tuyến tính cho các biến biên dựa trên các ô số lân cận.
    def _build_constraints(self, frontier_set):
        constraints = []
        numbered_cells = self.board.get_revealed_numbered_cells()

        for r, c, number in numbered_cells:
            flagged_count = self.board.get_flagged_neighbor_count(r, c)
            remaining_needed = number - flagged_count
            unrevealed = self.board.get_unrevealed_neighbors(r, c)
            relevant = [cell for cell in unrevealed if cell in frontier_set]

            if relevant and remaining_needed >= 0:
                constraints.append(((r, c), relevant, remaining_needed))

        return constraints

    # Thuật toán duy trì nhất quán cung (Arc Consistency) trên các ô biên để thu hẹp miền giá trị.
    def _ac3(self, domains, constraints):
        queue = deque()
        cell_constraints = {}
        for i, (pos, cells, needed) in enumerate(constraints):
            for cell in cells:
                if cell not in cell_constraints:
                    cell_constraints[cell] = []
                cell_constraints[cell].append(i)
                queue.append((cell, i))

        max_queue_ops = 10000
        ops = 0

        while queue and ops < max_queue_ops:
            ops += 1
            cell, constraint_idx = queue.popleft()
            self.metrics['nodes_explored'] += 1

            if cell not in domains or not domains[cell]:
                continue

            pos, cells, needed = constraints[constraint_idx]

            revised = False
            values_to_remove = set()

            for value in list(domains[cell]):
                if not self._has_support(cell, value, cells, needed, domains):
                    values_to_remove.add(value)
                    revised = True

            domains[cell] -= values_to_remove

            if not domains[cell]:
                return False

            if revised:
                for other_constraint_idx in cell_constraints.get(cell, []):
                    if other_constraint_idx != constraint_idx:
                        _, other_cells, _ = constraints[other_constraint_idx]
                        for other_cell in other_cells:
                            if other_cell != cell and other_cell in domains:
                                queue.append((other_cell, other_constraint_idx))

        changed = True
        prop_iter = 0
        while changed and prop_iter < 100:
            changed = False
            prop_iter += 1

            for pos, cells, needed in constraints:
                determined_mines = sum(1 for c in cells
                                        if c in domains and domains[c] == {True})
                determined_safe = sum(1 for c in cells
                                       if c in domains and domains[c] == {False})
                undetermined = [c for c in cells
                                if c in domains and len(domains[c]) == 2]

                remaining_mines = needed - determined_mines

                if remaining_mines < 0: return False
                if remaining_mines > len(undetermined): return False

                if remaining_mines == len(undetermined) and undetermined:
                    for c in undetermined:
                        domains[c] = {True}
                        changed = True

                if remaining_mines == 0 and undetermined:
                    for c in undetermined:
                        domains[c] = {False}
                        changed = True

        return True

    # Kiểm tra xem một giá trị gán của biến có được hỗ trợ bởi ít nhất một phương án nhất quán của các biến lân cận hay không.
    def _has_support(self, cell, value, constraint_cells, needed, domains):
        other_cells = [c for c in constraint_cells if c != cell]

        mine_if_value = 1 if value else 0
        determined_mines = sum(1 for c in other_cells
                               if c in domains and domains[c] == {True})
        determined_safe = sum(1 for c in other_cells
                               if c in domains and domains[c] == {False})
        undetermined = [c for c in other_cells
                         if c in domains and len(domains[c]) == 2]

        total_mines = mine_if_value + determined_mines
        remaining_needed = needed - total_mines

        if remaining_needed < 0:
            return False
        if remaining_needed > len(undetermined):
            return False

        return True

    # Chạy quay lui trên một nhóm nhỏ biến biên để tìm tất cả các nghiệm hợp lệ.
    def _simple_backtrack(self, variables, constraints, domains):
        solutions = []
        assignment = {}
        max_solutions = 200
        nodes = [0]
        max_nodes = 3000

        remaining_mines = self.board.num_mines - len(self.board.flagged)

        def backtrack(idx):
            nodes[0] += 1
            self.metrics['nodes_explored'] += 1

            if nodes[0] > max_nodes or len(solutions) >= max_solutions:
                return

            if idx == len(variables):
                valid = True
                for pos, cells, needed in constraints:
                    mines = sum(1 for c in cells if assignment.get(c, False))
                    all_assigned = all(c in assignment for c in cells)
                    if all_assigned and mines != needed:
                        valid = False
                        break
                if valid:
                    solutions.append(dict(assignment))
                return

            var = variables[idx]
            var_domain = domains.get(var, {True, False})

            for value in sorted(var_domain):
                assignment[var] = value

                consistent = True
                for pos, cells, needed in constraints:
                    if var not in cells:
                        continue
                    mines = sum(1 for c in cells if assignment.get(c, False))
                    unassigned = sum(1 for c in cells if c not in assignment)

                    if mines > needed:
                        consistent = False
                        break
                    if mines + unassigned < needed:
                        consistent = False
                        break

                total_mines = sum(1 for v in assignment.values() if v)
                if total_mines > remaining_mines:
                    consistent = False

                if consistent:
                    backtrack(idx + 1)

                del assignment[var]

        backtrack(0)

        if not solutions:
            return set(), set()

        safe_in_all = set(variables)
        mine_in_all = set(variables)

        for sol in solutions:
            for var in variables:
                if sol.get(var, False):
                    safe_in_all.discard(var)
                else:
                    mine_in_all.discard(var)

        return safe_in_all, mine_in_all
