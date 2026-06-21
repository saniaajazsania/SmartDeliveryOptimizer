"""
algorithms/hill_climbing.py
Hill Climbing — Local Search Algorithm (Informed).
Uses greedy step selection with random restarts and sideways moves.
Evaluates neighbors using f(n) = g(n) + h(n) at each step.
Note: Hill Climbing does NOT guarantee optimal or complete solutions.
"""

import time
import random
from typing import List, Tuple

SearchResult = Tuple[List[Tuple[int, int]], int, int, float]


def hill_climbing(
    grid,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    max_iterations: int = 500,
) -> SearchResult:
    """
    Perform Hill Climbing search to find a path from start to goal.

    Hill Climbing is a local search that greedily moves to the best-scoring
    neighbor at each step. It includes:
      - Random restarts: Multiple attempts to escape local minima
      - Sideways moves: Accept equal-cost moves to traverse plateaus
      - Stochastic perturbation: Random moves when stuck

    Important: This algorithm may FAIL to find a path even when one exists.
    This is intentional — it demonstrates the limitation of local search
    for pathfinding compared to systematic search algorithms.

    Args:
        grid: DeliveryGrid instance representing the environment.
        start: Starting position (row, col).
        goal: Target position (row, col).
        max_iterations: Total iterations across all restarts (default 500).

    Returns:
        Tuple of (path, cost, nodes_explored, time_ms).
        - path: List of positions. Empty if no path found.
        - cost: Total movement cost. -1 if failed.
        - nodes_explored: Total nodes evaluated across restarts.
        - time_ms: Execution time in milliseconds.
    """
    start_time = time.perf_counter()

    # Edge case: already at goal
    if start == goal:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return [start], 0, 0, elapsed_ms

    best_path: List[Tuple[int, int]] = []
    best_cost: int = float("inf")
    total_nodes: int = 0

    # Determine number of random restarts based on max_iterations
    num_restarts: int = max(1, min(max_iterations // 100, 15))
    iters_per_restart: int = max_iterations // num_restarts

    # Try multiple restarts to improve chances of finding a path
    for _ in range(num_restarts):
        path, cost, nodes = _single_climb(grid, start, goal, iters_per_restart)
        total_nodes += nodes

        # Keep the best result found across all restarts
        if path and cost < best_cost:
            best_path = path
            best_cost = cost

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    if not best_path:
        return [], -1, total_nodes, elapsed_ms

    return best_path, best_cost, total_nodes, elapsed_ms


def _single_climb(
    grid,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    max_iters: int,
) -> Tuple[List[Tuple[int, int]], int, int]:
    """
    Execute a single hill climbing attempt from start toward goal.

    At each step:
      1. Evaluate all neighbors using f(n) = g(n) + h(n)
      2. Move to the neighbor with the lowest f-score (if improving)
      3. Allow sideways moves (equal f-score) up to a limit
      4. Apply random perturbation when stuck to escape local minima

    Args:
        grid: DeliveryGrid instance.
        start: Starting position.
        goal: Target position.
        max_iters: Maximum iterations for this single climb.

    Returns:
        Tuple of (path, cost, nodes_explored).
        path is empty and cost is -1 if goal was not reached.
    """
    current: Tuple[int, int] = start
    path: List[Tuple[int, int]] = [start]
    cost: int = 0
    nodes: int = 0

    # Track cells visited in this path to reduce cycling
    visited_in_path: set = set()
    visited_in_path.add(start)

    # Sideways move counter and limit (for plateau traversal)
    sideways_count: int = 0
    max_sideways: int = 30

    for _ in range(max_iters):
        # Success: reached the goal
        if current == goal:
            return path, cost, nodes

        nodes += 1
        neighbors = grid.get_neighbors(current)

        if not neighbors:
            break  # Dead end with no valid neighbors

        # Prefer unvisited neighbors to reduce cycling
        unvisited = [n for n in neighbors if n not in visited_in_path]
        candidates = unvisited if unvisited else neighbors

        # Current evaluation score: actual cost + heuristic to goal
        current_h = _manhattan(current, goal)
        current_eval: float = cost + current_h

        # Evaluate every candidate neighbor
        best_neighbor: Tuple[int, int] | None = None
        best_eval: float = float("inf")
        best_move_cost: int = 0

        for n in candidates:
            mc = grid.get_move_cost(n)
            new_cost = cost + mc
            h = _manhattan(n, goal)
            eval_score = new_cost + h

            if eval_score < best_eval:
                best_eval = eval_score
                best_neighbor = n
                best_move_cost = mc

        if best_neighbor is None:
            break

        # Decision: improving move, sideways move, or stuck
        if best_eval < current_eval:
            # IMPROVING: Always accept moves that decrease f-score
            cost += best_move_cost
            current = best_neighbor
            path.append(current)
            visited_in_path.add(current)
            sideways_count = 0

        elif sideways_count < max_sideways:
            # SIDEWAYS: Accept equal-cost moves to cross plateaus
            cost += best_move_cost
            current = best_neighbor
            path.append(current)
            visited_in_path.add(current)
            sideways_count += 1

        else:
            # STUCK: Apply random perturbation to escape local minima
            rand_neighbor = random.choice(candidates)
            cost += grid.get_move_cost(rand_neighbor)
            current = rand_neighbor
            path.append(current)
            visited_in_path.add(current)
            sideways_count = 0

    # Goal not reached within iteration limit
    return [], -1, nodes


def _manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """
    Calculate Manhattan distance between two grid positions.

    Args:
        a: First position (row, col).
        b: Second position (row, col).

    Returns:
        Manhattan distance (sum of absolute differences).
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])