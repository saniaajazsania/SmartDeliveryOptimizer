"""
algorithms/ucs.py
Uniform Cost Search (UCS) — Uninformed Search Algorithm.
Finds the optimal (minimum-cost) path considering variable movement costs.
Uses a min-heap priority queue ordered by cumulative path cost.
"""

import time
import heapq
from typing import List, Tuple

SearchResult = Tuple[List[Tuple[int, int]], int, int, float]


def ucs(grid, start: Tuple[int, int], goal: Tuple[int, int]) -> SearchResult:
    """
    Perform Uniform Cost Search to find the minimum-cost path.

    UCS always expands the node with the lowest cumulative cost from start.
    It is optimal when all step costs are non-negative (true in our grid).
    Unlike BFS, UCS correctly handles variable costs (road=1, traffic=3).

    Args:
        grid: DeliveryGrid instance representing the environment.
        start: Starting position (row, col).
        goal: Target position (row, col).

    Returns:
        Tuple of (path, cost, nodes_explored, time_ms).
        - path: List of positions from start to goal. Empty if no path.
        - cost: Optimal total movement cost.
        - nodes_explored: Number of nodes popped from the priority queue.
        - time_ms: Execution time in milliseconds.
    """
    start_time = time.perf_counter()

    # Edge case: already at goal
    if start == goal:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return [start], 0, 0, elapsed_ms

    # Priority queue: (cumulative_cost, tie_breaker, position)
    # Tie-breaker counter ensures deterministic behavior when costs are equal
    counter: int = 0
    pq: List[Tuple[int, int, Tuple[int, int]]] = [(0, counter, start)]

    # Best known cost to reach each node (for pruning suboptimal paths)
    cost_so_far: dict = {start: 0}

    # Parent pointers for path reconstruction
    parent: dict = {start: None}

    nodes_explored: int = 0

    while pq:
        # Pop the node with the lowest cumulative cost
        current_cost, _, current = heapq.heappop(pq)
        nodes_explored += 1

        # Skip if we've already found a cheaper path to this node
        if current_cost > cost_so_far.get(current, float("inf")):
            continue

        # Goal check — first time we pop goal, it's optimal
        if current == goal:
            path = _reconstruct_path(parent, start, goal)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return path, current_cost, nodes_explored, elapsed_ms

        # Expand neighbors
        for neighbor in grid.get_neighbors(current):
            # Calculate cost to reach this neighbor through current path
            move_cost = grid.get_move_cost(neighbor)
            new_cost = current_cost + move_cost

            # If this is cheaper than any previously known path to neighbor
            if new_cost < cost_so_far.get(neighbor, float("inf")):
                cost_so_far[neighbor] = new_cost
                parent[neighbor] = current
                counter += 1
                heapq.heappush(pq, (new_cost, counter, neighbor))

    # No path exists
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return [], -1, nodes_explored, elapsed_ms


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