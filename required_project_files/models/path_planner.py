"""A-Star path planning module for safe route generation.

This module generates the shortest safe path from a truck's current position to a
selected dump site while avoiding obstacle cells. It is intentionally a reusable
utility module and does not include visualization or agent-specific logic.
"""

from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Sequence, Set, Tuple

from config import ALLOW_DIAGONAL, GRID_SIZE


class PathPlanner:
    """Compute a safe shortest path using the A* algorithm."""

    def __init__(self, grid_size: int = GRID_SIZE, allow_diagonal: bool = ALLOW_DIAGONAL):
        """Initialize the planner.

        The planner is parameterized with a simple grid-based movement model: each
        move is allowed in 8 directions (up, down, left, right, and diagonals),
        which is useful for providing a route in a map-like environment.
        """
        self.grid_size = grid_size
        self.allow_diagonal = allow_diagonal
        if allow_diagonal:
            self.directions = [
                (-1, -1), (0, -1), (1, -1),
                (-1,  0),          (1,  0),
                (-1,  1), (0,  1), (1,  1),
            ]
        else:
            self.directions = [
                (0, -1),
                (-1,  0), (1,  0),
                (0,  1),
            ]

    def heuristic(self, node1: Sequence[int], node2: Sequence[int]) -> float:
        """Return the Manhattan or diagonal-inspired heuristic distance.

        Args:
            node1: First coordinate tuple in the form ``(x, y)``.
            node2: Second coordinate tuple in the form ``(x, y)``.

        Returns:
            A heuristic cost estimate between the two nodes.
        """
        x1, y1 = node1
        x2, y2 = node2
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)

        # A simple diagonal-inspired heuristic for grid movement.
        return dx + dy

    def get_neighbors(self, node: Sequence[int]) -> List[Tuple[int, int]]:
        """Return neighboring grid coordinates for a given node.

        Args:
            node: Current coordinate tuple ``(x, y)``.

        Returns:
            A list of valid neighbor coordinates that can be reached in one step.
        """
        x, y = node
        neighbors: List[Tuple[int, int]] = []

        for dx, dy in self.directions:
            neighbors.append((x + dx, y + dy))

        return neighbors

    def find_path(
        self,
        start: Sequence[int],
        goal: Sequence[int],
        obstacles: Sequence[Sequence[int]],
    ) -> Optional[List[List[int]]]:
        """Find the shortest safe path from start to goal using A*.

        Args:
            start: Start coordinate ``(x, y)``.
            goal: Goal coordinate ``(x, y)``.
            obstacles: A list of obstacle coordinates, each in the form ``(x, y)``.

        Returns:
            A list of coordinates representing the path from start to goal, or
            ``None`` if no safe path is available.
        """
        if start == goal:
            return [list(start)]

        start = (int(start[0]), int(start[1]))
        goal = (int(goal[0]), int(goal[1]))
        obstacle_set: Set[Tuple[int, int]] = {
            (int(x), int(y)) for x, y in obstacles
        }

        open_heap: List[Tuple[float, int, Tuple[int, int]]] = []
        heapq.heappush(open_heap, (0, 0, start))

        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        g_score: Dict[Tuple[int, int], float] = {start: 0.0}

        while open_heap:
            _, _, current = heapq.heappop(open_heap)

            if current == goal:
                break

            for neighbor in self.get_neighbors(current):
                if neighbor in obstacle_set:
                    continue

                tentative_g = g_score[current] + 1.0

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_heap, (f_score, len(open_heap), neighbor))

        if goal not in came_from:
            return None

        path: List[List[int]] = []
        current: Optional[Tuple[int, int]] = goal

        while current is not None:
            path.append([current[0], current[1]])
            current = came_from[current]

        path.reverse()
        return path
