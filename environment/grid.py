"""
environment/grid.py
DeliveryGrid class for the Smart Delivery Route Optimizer.
Represents a grid-based city map with roads, obstacles, delivery points, and traffic zones.
"""

import random
from typing import List, Tuple, Optional


class DeliveryGrid:
    """
    Represents the delivery environment as a 2D grid.

    Cell Types:
        0 = Open road      (movement cost = 1)
        1 = Obstacle       (impassable)
        2 = Delivery point (movement cost = 1)
        3 = Traffic zone   (movement cost = 3)

    Attributes:
        rows (int): Number of rows in the grid.
        cols (int): Number of columns in the grid.
        grid (List[List[int]]): 2D array representing the grid.
        start (Tuple[int, int]): Starting position (warehouse at top-left).
        delivery_points (List[Tuple[int, int]]): List of delivery point coordinates.
    """

    # Cell type constants for readability
    ROAD = 0
    OBSTACLE = 1
    DELIVERY = 2
    TRAFFIC = 3

    def __init__(
        self,
        size: int = 20,
        obstacle_density: float = 0.2,
        traffic_density: float = 0.05,
        num_deliveries: int = 5,
        seed: Optional[int] = None,
    ) -> None:
        """
        Initialize and generate a delivery grid with random obstacles and deliveries.

        Args:
            size: Grid dimension (size x size square grid).
            obstacle_density: Fraction of cells that are obstacles (0.0 to 0.5).
            traffic_density: Fraction of cells that are traffic zones.
            num_deliveries: Number of delivery points to place on the grid.
            seed: Random seed for reproducibility. None for truly random.
        """
        self.rows: int = size
        self.cols: int = size
        self.start: Tuple[int, int] = (0, 0)
        self.delivery_points: List[Tuple[int, int]] = []

        # Set random seed if provided for reproducible scenarios
        if seed is not None:
            random.seed(seed)

        # Generate the grid layout
        self._generate_grid(obstacle_density, traffic_density, num_deliveries)

    # ------------------------------------------------------------------ #
    #                        GRID GENERATION                              #
    # ------------------------------------------------------------------ #

    def _generate_grid(
        self,
        obstacle_density: float,
        traffic_density: float,
        num_deliveries: int,
    ) -> None:
        """
        Generate the grid with obstacles, traffic zones, and delivery points.
        Retries generation until all delivery points are reachable from start.

        Args:
            obstacle_density: Fraction of obstacle cells.
            traffic_density: Fraction of traffic zone cells.
            num_deliveries: Number of delivery points to place.
        """
        max_attempts: int = 100

        for _ in range(max_attempts):
            # Step 1: Initialize entire grid as open road
            self.grid: List[List[int]] = [
                [self.ROAD for _ in range(self.cols)] for _ in range(self.rows)
            ]

            # Step 2: Randomly place obstacles (avoid start area)
            num_obstacles = int(self.rows * self.cols * obstacle_density)
            self._place_cells(self.OBSTACLE, num_obstacles, exclude_start_area=True)

            # Step 3: Randomly place traffic zones
            num_traffic = int(self.rows * self.cols * traffic_density)
            self._place_cells(self.TRAFFIC, num_traffic, exclude_start_area=True)

            # Step 4: Randomly place delivery points
            self.delivery_points = []
            self._place_deliveries(num_deliveries)

            # Step 5: Verify all delivery points are reachable from (0,0)
            if self._check_connectivity():
                return  # Valid grid found

        # Fallback: if no valid grid found, force connectivity
        self._fix_connectivity()

    def _place_cells(
        self, cell_type: int, count: int, exclude_start_area: bool = False
    ) -> None:
        """
        Randomly place cells of a given type on the grid.

        Args:
            cell_type: The cell type constant (OBSTACLE or TRAFFIC).
            count: Number of cells to place.
            exclude_start_area: If True, avoid placing near (0,0).
        """
        placed: int = 0
        while placed < count:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)

            # Protect the start position and its immediate neighbors
            if exclude_start_area and r <= 1 and c <= 1:
                continue

            # Only place on empty road cells
            if self.grid[r][c] == self.ROAD:
                self.grid[r][c] = cell_type
                placed += 1

    def _place_deliveries(self, count: int) -> None:
        """
        Place delivery points on empty road cells.

        Args:
            count: Number of delivery points to place.
        """
        placed: int = 0
        while placed < count:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)

            # Cannot place on start position
            if (r, c) == self.start:
                continue

            if self.grid[r][c] == self.ROAD:
                self.grid[r][c] = self.DELIVERY
                self.delivery_points.append((r, c))
                placed += 1

    # ------------------------------------------------------------------ #
    #                      CONNECTIVITY CHECKS                            #
    # ------------------------------------------------------------------ #

    def _check_connectivity(self) -> bool:
        """
        Check if all delivery points are reachable from start using BFS.

        Returns:
            True if every delivery point is reachable from (0,0), False otherwise.
        """
        if not self.delivery_points:
            return True

        # BFS from start to find all reachable cells
        visited: set = set()
        queue: List[Tuple[int, int]] = [self.start]
        visited.add(self.start)

        while queue:
            current = queue.pop(0)
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        # Verify every delivery point is in the visited set
        for dp in self.delivery_points:
            if dp not in visited:
                return False
        return True

    def _fix_connectivity(self) -> None:
        """
        Force connectivity by clearing obstacles along straight-line paths
        from start to any unreachable delivery point.
        """
        for dp in self.delivery_points:
            if not self._is_reachable(self.start, dp):
                # Carve a path from start to this delivery point
                r, c = self.start
                r2, c2 = dp
                while (r, c) != (r2, c2):
                    if self.grid[r][c] == self.OBSTACLE:
                        self.grid[r][c] = self.ROAD
                    # Step toward target diagonally
                    if r < r2:
                        r += 1
                    elif r > r2:
                        r -= 1
                    if c < c2:
                        c += 1
                    elif c > c2:
                        c -= 1
                # Ensure the delivery point cell itself is correct
                self.grid[r2][c2] = self.DELIVERY

    def _is_reachable(
        self, start: Tuple[int, int], goal: Tuple[int, int]
    ) -> bool:
        """
        Check if a specific goal cell is reachable from start using BFS.

        Args:
            start: Starting position (row, col).
            goal: Target position (row, col).

        Returns:
            True if goal is reachable from start, False otherwise.
        """
        visited: set = set()
        queue: List[Tuple[int, int]] = [start]
        visited.add(start)

        while queue:
            current = queue.pop(0)
            if current == goal:
                return True
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False

    # ------------------------------------------------------------------ #
    #                        GRID QUERIES                                 #
    # ------------------------------------------------------------------ #

    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get valid neighboring positions using 4-directional movement.

        Args:
            pos: Current position as (row, col).

        Returns:
            List of valid neighboring positions (up, down, left, right).
        """
        r, c = pos
        neighbors: List[Tuple[int, int]] = []
        # Four directional moves: up, down, left, right
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in moves:
            nr, nc = r + dr, c + dc
            # Check grid boundaries
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                # Check cell is not an obstacle
                if self.grid[nr][nc] != self.OBSTACLE:
                    neighbors.append((nr, nc))
        return neighbors

    def get_move_cost(self, pos: Tuple[int, int]) -> int:
        """
        Get the movement cost for entering a specific cell.

        Args:
            pos: Target cell position (row, col).

        Returns:
            Movement cost: 1 for road/delivery, 3 for traffic zone.
        """
        cell_type = self.grid[pos[0]][pos[1]]
        if cell_type == self.TRAFFIC:
            return 3
        return 1  # ROAD and DELIVERY both cost 1

    def is_valid_pos(self, pos: Tuple[int, int]) -> bool:
        """
        Check if a position is within bounds and not an obstacle.

        Args:
            pos: Position to check (row, col).

        Returns:
            True if position is valid for movement, False otherwise.
        """
        r, c = pos
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.grid[r][c] != self.OBSTACLE
        return False

    def get_cell_type(self, pos: Tuple[int, int]) -> int:
        """
        Get the cell type constant at a given position.

        Args:
            pos: Position to query (row, col).

        Returns:
            Cell type integer (0=road, 1=obstacle, 2=delivery, 3=traffic).
        """
        return self.grid[pos[0]][pos[1]]