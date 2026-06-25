import random
from ..base import Algorithm

# Bộ giải quyết ràng buộc CSP hoàn chỉnh sử dụng thuật toán quay lui và phân chia biến.
class BacktrackingCSP(Algorithm):
    def __init__(self, board):
        super().__init__(board)
        self.name = "Backtracking CSP"
        self.category = "CSP / Constraint"
        self.category_index = 5
        self.description = (
            "Xử lý minesweeper như Bài toán thỏa mãn ràng buộc (CSP). "
            "Biến: ô chưa mở. Miền: {MÌN, AN TOÀN}. "
            "Ràng buộc: mỗi ô số phải có đúng N mìn lân cận. "
            "Quay lui: gán giá trị, kiểm tra ràng buộc, quay lui khi vi phạm. "
            "Dùng MRV để chọn biến. Đây là bộ giải HOÀN CHỈNH."
        )

    # Vòng lặp giải chính gom nhóm biến biên thành các thành phần độc lập và giải bằng quay lui.
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
            constraints = self._build_constraints(frontier_set)

            if not constraints:
                safest = self.get_safest_cell()
                if safest:
                    self.do_reveal(safest[0], safest[1])
                continue

            constrained_cells = set()
            for _, cells, _ in constraints:
                constrained_cells.update(cells)

            variables = sorted(constrained_cells)

            if len(variables) > 25:
                groups = self._partition_variables(variables, constraints)
            else:
                groups = [variables]

            all_solutions_safe = set(frontier_set)
            all_solutions_mine = set(frontier_set)
            has_solution = False

            for group in groups:
                group_set = set(group)
                group_constraints = [
                    (pos, [c for c in cells if c in group_set], needed)
                    for pos, cells, needed in constraints
                    if any(c in group_set for c in cells)
                ]
                group_constraints = [(p, cells, n) for p, cells, n in group_constraints if cells]

                remaining_mines = self.board.num_mines - len(self.board.flagged)

                solutions = self._backtrack_solve(
                    group, group_constraints, remaining_mines
                )

                if solutions:
                    has_solution = True
                    group_safe = set(group)
                    group_mine = set(group)

                    for solution in solutions:
                        mines_in_sol = set(cell for cell, val in solution.items() if val)
                        safe_in_sol = set(cell for cell, val in solution.items() if not val)
                        group_safe &= safe_in_sol
                        group_mine &= mines_in_sol

                    all_solutions_safe = (all_solutions_safe & group_safe) | \
                                          (all_solutions_safe - group_set)
                    all_solutions_mine = (all_solutions_mine & group_mine) | \
                                          (all_solutions_mine - group_set)
                else:
                    all_solutions_safe -= group_set
                    all_solutions_mine -= group_set

            all_solutions_safe &= frontier_set
            all_solutions_mine &= frontier_set

            for cell in all_solutions_mine:
                if not self.board.is_flagged(cell[0], cell[1]):
                    self.do_flag(cell[0], cell[1])

            revealed_any = False
            for cell in all_solutions_safe:
                if not self.board.is_revealed(cell[0], cell[1]) and \
                   not self.board.is_flagged(cell[0], cell[1]):
                    result = self.do_reveal(cell[0], cell[1])
                    if result is not None:
                        revealed_any = True

            if not revealed_any and not all_solutions_mine:
                safest = self.get_safest_cell()
                if safest:
                    self.do_reveal(safest[0], safest[1])
                else:
                    unrevealed = self.board.get_all_unrevealed_unflagged()
                    if unrevealed:
                        cell = rng.choice(unrevealed)
                        self.do_reveal(cell[0], cell[1])

    # Tạo danh sách ràng buộc cho các ô biên dựa trên ô số lân cận.
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

    # Phân chia các biến biên thành các nhóm độc lập bằng Union-Find.
    def _partition_variables(self, variables, constraints):
        parent = {v: v for v in variables}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        for _, cells, _ in constraints:
            cells_in_vars = [c for c in cells if c in parent]
            for i in range(1, len(cells_in_vars)):
                union(cells_in_vars[0], cells_in_vars[i])

        groups = {}
        for v in variables:
            root = find(v)
            if root not in groups:
                groups[root] = []
            groups[root].append(v)

        result = []
        for group in groups.values():
            if len(group) > 20:
                for i in range(0, len(group), 15):
                    result.append(group[i:i+15])
            else:
                result.append(group)

        return result

    # Khởi chạy thuật toán quay lui tìm tất cả lời giải hợp lệ cho một nhóm biến.
    def _backtrack_solve(self, variables, constraints, max_mines):
        solutions = []
        assignment = {}
        MAX_SOLUTIONS = 200
        self._bt_nodes = 0
        MAX_NODES = 5000

        def get_mrv_variable():
            # MRV heuristic
            unassigned = [v for v in variables if v not in assignment]
            if not unassigned:
                return None

            best_var = None
            min_remaining = float('inf')

            for var in unassigned:
                constraint_tightness = 0
                for _, cells, needed in constraints:
                    if var in cells:
                        assigned_mines = sum(1 for c in cells
                                             if assignment.get(c, False) and c in assignment)
                        assigned_safe = sum(1 for c in cells
                                            if c in assignment and not assignment[c])
                        unassigned_in_constraint = sum(1 for c in cells if c not in assignment)
                        remaining = needed - assigned_mines
                        if unassigned_in_constraint > 0:
                            constraint_tightness += 1.0 / unassigned_in_constraint

                if constraint_tightness < min_remaining:
                    min_remaining = constraint_tightness
                    best_var = var

            return best_var if best_var else unassigned[0]

        def is_consistent():
            for _, cells, needed in constraints:
                assigned_mines = sum(1 for c in cells
                                     if c in assignment and assignment[c])
                unassigned_count = sum(1 for c in cells if c not in assignment)
                assigned_safe = sum(1 for c in cells
                                    if c in assignment and not assignment[c])

                if assigned_mines > needed:
                    return False
                if assigned_mines + unassigned_count < needed:
                    return False
                total = len(cells)
                if total - assigned_safe < needed:
                    return False

            total_mines = sum(1 for v in assignment.values() if v)
            if total_mines > max_mines:
                return False

            return True

        def backtrack():
            self._bt_nodes += 1
            self.metrics['nodes_explored'] += 1

            if self._bt_nodes > MAX_NODES:
                return
            if len(solutions) >= MAX_SOLUTIONS:
                return

            var = get_mrv_variable()
            if var is None:
                if self._check_full_assignment(assignment, constraints):
                    solutions.append(dict(assignment))
                return

            for value in [False, True]:
                assignment[var] = value

                if is_consistent():
                    backtrack()

                del assignment[var]

        backtrack()
        return solutions

    # Kiểm tra xem một phân bổ mìn hoàn chỉnh có thỏa mãn tất cả các ràng buộc hay không.
    def _check_full_assignment(self, assignment, constraints):
        for _, cells, needed in constraints:
            mines_count = sum(1 for c in cells if assignment.get(c, False))
            if mines_count != needed:
                return False
        return True
