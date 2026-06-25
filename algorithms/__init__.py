from .uninformed.bfs import BFSAlgorithm
from .uninformed.dfs import DFSAlgorithm
from .informed.astar import AStarSearch
from .informed.greedy import GreedyBestFirst
from .local_search.hill_climbing import HillClimbing
from .local_search.simulated_annealing import SimulatedAnnealing
from .nondeterministic.and_or_search import AndOrSearch
from .nondeterministic.belief_state import BeliefStateSearch
from .csp.ac3 import AC3Algorithm
from .csp.backtracking import BacktrackingCSP
from .adversarial.minimax import MinimaxAgent
from .adversarial.alpha_beta import AlphaBetaAgent

ALGORITHM_MAP = {
    "bfs": BFSAlgorithm,
    "dfs": DFSAlgorithm,
    "astar": AStarSearch,
    "greedy": GreedyBestFirst,
    "hill_climbing": HillClimbing,
    "simulated_annealing": SimulatedAnnealing,
    "and_or": AndOrSearch,
    "belief_state": BeliefStateSearch,
    "ac3": AC3Algorithm,
    "backtracking": BacktrackingCSP,
    "minimax": MinimaxAgent,
    "alpha_beta": AlphaBetaAgent
}

def create_algorithm(key, board):
    AlgoClass = ALGORITHM_MAP.get(key)
    if AlgoClass:
        return AlgoClass(board)
    return None
