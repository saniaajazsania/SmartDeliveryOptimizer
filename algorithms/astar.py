"""
algorithms/astar.py
A* Search Algorithm — Informed / Heuristic Search.
Combines actual cost g(n) with heuristic estimate h(n).
f(n) = g(n) + w × h(n), where w is the adjustable heuristic_weight.
Uses Manhattan distance as the heuristic (admissible for 4-directional grids).
"""

import time
import heapq
from typing import List, Tuple

SearchResult = Tuple[List[Tuple[int, int]], int, int, float]


def astar(
    grid,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    heuristic_weight: float = 1.0,
) -> SearchResult:
    """
    Perform A* Search to find an efficient path from start to goal.

    A* uses f(n) = g(n) + w * h(n) where:
      - g(n) = actual cost from start to node n
      - h(n) = Manhattan distance heuristic from n to goal
      - w = heuristic_weight parameter

    Weight behavior:
      - w = 1.0: Standard A* (optimal with admissible heuristic)
      - w > 1.0: More greedy, faster but potentially suboptimal
      - w < 1.0: More like UCS, slower but still optimal

    Args:
        grid: DeliveryGrid instance representing the environment.
        start: Starting position (row, col).
        goal: Target position (row, col).
        heuristic_weight: Weight multiplier for heuristic (range 0.5–3.0).

    Returns:
        Tuple of (path, cost, nodes_explored, time_ms).
        - path: List of positions from start to goal. Empty if no path.
        - cost: Total movement cost (g-value at goal).
        - nodes_explored: Number of nodes popped from priority queue.
        - time_ms: Execution time in milliseconds.
    """
    start_time = time.perf_counter()

    # Edge case: already at goal
    if start == goal:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return [start], 0, 0, elapsed_ms

    # Priority queue: (f_score, tie_breaker, position)
    counter: int = 0
    h_start = _manhattan_distance(start, goal)
    f_start = 0.0 + heuristic_weight * h_start  # g=0 at start
    pq: List[Tuple[float, int, Tuple[int, int]]] = [(f_start, counter, start)]

    # g_score: best known actual cost from start to each node
    g_score: dict = {start: 0}

    # Closed set: nodes that have already been expanded
    closed_set: set = set()

    # Parent pointers for path reconstruction
    parent: dict = {start: None}

    nodes_explored: int = 0

    while pq:
        # Pop node with lowest f-score
        current_f, _, current = heapq.heappop(pq)
        nodes_explored += 1

        # Skip if already expanded (may exist in PQ with stale f-score)
        if current in closed_set:
            continue
        closed_set.add(current)

        # Goal check
        if current == goal:
            path = _reconstruct_path(parent, start, goal)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return path, g_score[goal], nodes_explored, elapsed_ms

        # Expand all valid neighbors
        for neighbor in grid.get_neighbors(current):
            # Skip already-expanded nodes
            if neighbor in closed_set:
                continue

            # Calculate tentative g-score through current node
            move_cost = grid.get_move_cost(neighbor)
            tentative_g = g_score[current] + move_cost

            # If this path to neighbor is better than any previous one
            if tentative_g < g_score.get(neighbor, float("inf")):
                parent[neighbor] = current
                g_score[neighbor] = tentative_g
                h = _manhattan_distance(neighbor, goal)
                f = tentative_g + heuristic_weight * h
                counter += 1
                heapq.heappush(pq, (f, counter, neighbor))

    # No path exists
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return [], -1, nodes_explored, elapsed_ms


def _manhattan_distance(
    a: Tuple[int, int], b: Tuple[int, int]
) -> int:
    """
    Calculate Manhattan distance between two grid positions.
    Admissible and consistent heuristic for 4-directional movement.

    Args:
        a: First position (row, col).
        b: Second position (row, col).

    Returns:
        Manhattan distance (sum of absolute row and column differences).
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _reconstruct_path(
    parent: dict, start: Tuple[int, int], goal: Tuple[int, int]
) -> List[Tuple[int, int]]:
    """
    Trace back through parent pointers to build the path.

    Args:
        parent: Dictionary mapping each node to its predecessor.
        start: The starting node.
        goal: The target node.

    Returns:
        Ordered list of positions from start to goal.
    """
    path: List[Tuple[int, int]] = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent.get(current)
    path.reverse()
    return path