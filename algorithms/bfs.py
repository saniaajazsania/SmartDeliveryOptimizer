"""
algorithms/bfs.py
Breadth-First Search (BFS) — Uninformed Search Algorithm.
Explores all nodes at the current depth before moving deeper.
Guarantees shortest path in terms of number of steps (unweighted).
"""

import time
from collections import deque
from typing import List, Tuple

# Type alias for consistent return type across all algorithms
SearchResult = Tuple[List[Tuple[int, int]], int, int, float]


def bfs(grid, start: Tuple[int, int], goal: Tuple[int, int]) -> SearchResult:
    """
    Perform Breadth-First Search to find path from start to goal.

    BFS uses a FIFO queue to explore nodes level by level. It guarantees
    the shortest path in an unweighted graph (minimum number of steps).
    Note: BFS does NOT account for variable movement costs (traffic zones).

    Args:
        grid: DeliveryGrid instance representing the environment.
        start: Starting position (row, col).
        goal: Target position (row, col).

    Returns:
        Tuple of (path, cost, nodes_explored, time_ms).
        - path: List of positions from start to goal. Empty if no path.
        - cost: Total movement cost (sum of cell costs along path).
        - nodes_explored: Number of nodes dequeued and examined.
        - time_ms: Execution time in milliseconds.
    """
    start_time = time.perf_counter()

    # Edge case: already at goal
    if start == goal:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return [start], 0, 0, elapsed_ms

    # BFS frontier: FIFO queue
    queue: deque = deque()
    queue.append(start)

    # Visited set to prevent revisiting nodes (cycles)
    visited: set = set()
    visited.add(start)

    # Parent map for reconstructing the path after goal is found
    parent: dict = {start: None}

    # Track how many nodes we actually examine
    nodes_explored: int = 0

    while queue:
        # Dequeue the first node (FIFO order)
        current: Tuple[int, int] = queue.popleft()
        nodes_explored += 1

        # Goal check
        if current == goal:
            path = _reconstruct_path(parent, start, goal)
            cost = _calculate_path_cost(grid, path)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return path, cost, nodes_explored, elapsed_ms

        # Expand: add all unvisited neighbors to the queue
        for neighbor in grid.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    # No path exists between start and goal
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return [], -1, nodes_explored, elapsed_ms


def _reconstruct_path(
    parent: dict, start: Tuple[int, int], goal: Tuple[int, int]
) -> List[Tuple[int, int]]:
    """
    Trace back through parent pointers to build the path from start to goal.

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
    path.reverse()  # Reverse to get start→goal order
    return path


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