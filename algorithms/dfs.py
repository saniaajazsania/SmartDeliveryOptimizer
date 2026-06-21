"""
algorithms/dfs.py
Depth-First Search (DFS) — Uninformed Search Algorithm.
Explores as deep as possible along each branch before backtracking.
Includes a max_depth parameter to limit search depth.
"""

import time
from typing import List, Tuple

SearchResult = Tuple[List[Tuple[int, int]], int, int, float]


def dfs(
    grid,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    max_depth: int = 100,
) -> SearchResult:
    """
    Perform Depth-First Search to find path from start to goal.

    DFS uses a LIFO stack to go deep before going wide. It does NOT
    guarantee the shortest or optimal path. The max_depth parameter
    prevents excessive exploration on large grids.

    Args:
        grid: DeliveryGrid instance representing the environment.
        start: Starting position (row, col).
        goal: Target position (row, col).
        max_depth: Maximum search depth (default 100). Prevents infinite
                   exploration on large/dense grids.

    Returns:
        Tuple of (path, cost, nodes_explored, time_ms).
        - path: List of positions from start to goal. Empty if no path found.
        - cost: Total movement cost along the path.
        - nodes_explored: Number of nodes popped from the stack.
        - time_ms: Execution time in milliseconds.
    """
    start_time = time.perf_counter()

    # Edge case: already at goal
    if start == goal:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return [start], 0, 0, elapsed_ms

    # DFS frontier: LIFO stack
    # Each entry: (current_position, current_depth, path_so_far)
    stack: List[Tuple[Tuple[int, int], int, List[Tuple[int, int]]]] = [
        (start, 0, [start])
    ]

    # Track visited nodes to avoid cycles
    visited: set = set()
    visited.add(start)

    nodes_explored: int = 0

    while stack:
        # Pop the most recently added node (LIFO)
        current, depth, path = stack.pop()
        nodes_explored += 1

        # Goal check
        if current == goal:
            cost = _calculate_path_cost(grid, path)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return path, cost, nodes_explored, elapsed_ms

        # Respect depth limit — stop going deeper if exceeded
        if depth >= max_depth:
            continue

        # Get neighbors and iterate in reverse for consistent left-to-right order
        neighbors = grid.get_neighbors(current)
        for neighbor in reversed(neighbors):
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append((neighbor, depth + 1, path + [neighbor]))

    # No path found within depth limit
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return [], -1, nodes_explored, elapsed_ms


def _calculate_path_cost(
    grid, path: List[Tuple[int, int]]
) -> int:
    """
    Sum the movement costs along a path (excluding the starting cell).

    Args:
        grid: DeliveryGrid instance.
        path: List of positions forming the path.

    Returns:
        Total cumulative movement cost.
    """
    total_cost: int = 0
    for i in range(1, len(path)):
        total_cost += grid.get_move_cost(path[i])
    return total_cost