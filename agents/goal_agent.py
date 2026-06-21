"""
agents/goal_agent.py
Goal-Based Agent — uses A* to visit all delivery points.
Implements nearest-neighbor ordering strategy.
Fulfills: "Agent-Based Solutions → Goal-Based Agent" requirement.
"""

import time
from typing import List, Tuple, Dict, Any

# Import all 5 algorithms
from algorithms.bfs import bfs
from algorithms.dfs import dfs
from algorithms.ucs import ucs
from algorithms.astar import astar
from algorithms.hill_climbing import hill_climbing

AgentResult = Dict[str, Any]


class GoalBasedAgent:
    """
    Goal-Based Agent that plans routes to visit ALL delivery points.

    Strategy:
        1. Order deliveries using nearest-neighbor heuristic
        2. Use selected search algorithm for each leg (start→d1→d2→...)
        3. Aggregate results: total path, cost, nodes, time

    The agent perceives the grid state and delivery locations,
    then formulates a plan to achieve the goal of delivering
    all packages efficiently.
    """

    def __init__(self, grid, algorithm: str = "A*", **kwargs) -> None:
        """Initialize the Goal-Based Agent.

        Args:
            grid: DeliveryGrid environment instance.
            algorithm: Name of search algorithm to use.
            **kwargs: Algorithm parameters (heuristic_weight, max_depth, etc.)
        """
        self.grid = grid
        self.algorithm_name = algorithm
        self.params = kwargs

    def plan_and_execute(self) -> AgentResult:
        """Plan route to all deliveries and execute.

        Returns:
            Dictionary with keys: path, total_cost, nodes_explored,
            time_ms, algorithm, deliveries_visited, legs (per-leg details).
        """
        start_time = time.perf_counter()

        # Step 1: Determine visitation order using nearest-neighbor
        order = self._nearest_neighbor_order()

        # Step 2: Run algorithm for each leg
        full_path: List[Tuple[int, int]] = []
        total_cost: int = 0
        total_nodes: int = 0
        legs: List[Dict] = []
        deliveries_visited: int = 0

        for i, target in enumerate(order):
            leg_start = full_path[-1] if full_path else self.grid.start
            path, cost, nodes, _ = self._run_algorithm(leg_start, target)

            if not path:
                # Failed to reach this delivery
                legs.append({
                    "from": leg_start, "to": target,
                    "path": [], "cost": -1, "nodes": nodes, "success": False
                })
                continue

            # Remove first point to avoid duplication when concatenating
            if full_path:
                path = path[1:]

            full_path.extend(path)
            total_cost += cost
            total_nodes += nodes
            deliveries_visited += 1
            legs.append({
                "from": leg_start, "to": target,
                "path_length": len(path),
                "cost": cost, "nodes": nodes, "success": True
            })

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "path": full_path,
            "total_cost": total_cost,
            "nodes_explored": total_nodes,
            "time_ms": elapsed_ms,
            "algorithm": self.algorithm_name,
            "deliveries_visited": deliveries_visited,
            "total_deliveries": len(self.grid.delivery_points),
            "legs": legs,
        }

    def _nearest_neighbor_order(self) -> List[Tuple[int, int]]:
        """Order delivery points by nearest-neighbor from current position.

        Returns:
            Ordered list of delivery point coordinates.
        """
        remaining = list(self.grid.delivery_points)
        ordered: List[Tuple[int, int]] = []
        current = self.grid.start

        while remaining:
            # Find the closest delivery point by Manhattan distance
            closest = min(remaining, key=lambda d: _manhattan(current, d))
            ordered.append(closest)
            remaining.remove(closest)
            current = closest

        return ordered

    def _run_algorithm(
        self, start: Tuple[int, int], goal: Tuple[int, int]
    ) -> Tuple[List[Tuple[int, int]], int, int, float]:
        """Run the selected search algorithm for one leg.

        Args:
            start: Leg start position.
            goal: Leg target position.

        Returns:
            (path, cost, nodes_explored, time_ms)
        """
        algo = self.algorithm_name.lower()

        if algo == "bfs":
            return bfs(self.grid, start, goal)
        elif algo == "dfs":
            return dfs(
                self.grid, start, goal,
                max_depth=self.params.get("max_depth", 100)
            )
        elif algo == "ucs":
            return ucs(self.grid, start, goal)
        elif algo == "a*":
            return astar(
                self.grid, start, goal,
                heuristic_weight=self.params.get("heuristic_weight", 1.0)
            )
        elif algo == "hill climbing":
            return hill_climbing(
                self.grid, start, goal,
                max_iterations=self.params.get("max_iterations", 500)
            )
        else:
            # Default to A*
            return astar(self.grid, start, goal)


def _manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """Manhattan distance helper."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])