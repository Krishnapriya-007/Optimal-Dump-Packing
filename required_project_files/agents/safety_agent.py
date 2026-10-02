"""Safety Agent for validating route accessibility and risk.

This module is responsible only for checking whether a planned route is safe.
It does not perform path planning or routing; it validates a route proposed by
other agents and determines whether the route is acceptable for execution.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from config import MIN_SAFETY_SCORE


class SafetyAgent:
    """Validate dump-site accessibility and route safety for a truck."""

    def __init__(self, min_safety_score: int = MIN_SAFETY_SCORE):
        """Initialize the Safety Agent.

        The agent stores basic route and obstacle information and evaluates whether
        a route is safe enough for execution.
        """
        self.default_route: List[List[float]] = []
        self.min_safety_score = min_safety_score

    def check_obstacles(self, route: Sequence[Sequence[float]], obstacles: Sequence[Sequence[float]]) -> bool:
        """Check whether any obstacle intersects the planned route.

        Args:
            route: A list of route points, typically ``[[x, y], [x, y], ...]``.
            obstacles: A list of obstacle bounding boxes in the form
                ``[x1, y1, x2, y2]``.

        Returns:
            ``True`` if at least one obstacle intersects the route, otherwise
            ``False``.
        """
        if not route:
            return True

        for obstacle in obstacles:
            if len(obstacle) != 4:
                continue

            ox1, oy1, ox2, oy2 = obstacle

            for point in route:
                if len(point) < 2:
                    continue
                px, py = point
                if ox1 <= px <= ox2 and oy1 <= py <= oy2:
                    return True

        return False

    def validate_route(self, route: Sequence[Sequence[float]], obstacles: Sequence[Sequence[float]]) -> bool:
        """Validate whether the route is accessible and safe.

        This function performs the following checks:
        - ensure the route is not empty
        - ensure no obstacle blocks the route
        - verify that the route is not obviously invalid

        Args:
            route: Sequence of route points.
            obstacles: Sequence of obstacle bounding boxes.

        Returns:
            ``True`` when the route is considered safe, otherwise ``False``.
        """
        if not route:
            return False

        # A route with only one point is treated as not safe because it does not
        # sufficiently describe a valid traverse from truck to dump.
        if len(route) < 2:
            return False

        # If an obstacle intersects the route, reject the route immediately.
        if self.check_obstacles(route, obstacles):
            return False

        # Basic route sanity check: ensure route points are numeric and valid.
        for point in route:
            if len(point) < 2:
                return False
            x, y = point
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                return False

        return True

    def calculate_safety_score(self, route: Sequence[Sequence[float]]) -> int:
        """Assign a route safety score between 0 and 100.

        The score is a simple heuristic based on route length and route validity.
        Routes with more points are treated as more complex, but the score remains
        within a safe range.

        Args:
            route: Route points representing the path from truck to dump.

        Returns:
            Integer safety score from 0 to 100.
        """
        if not route:
            return 0

        # Route score starts from a high value and is reduced for complexity.
        score = 100

        # Penalize long or complex routes.
        route_length = len(route)
        if route_length > 10:
            score -= 15
        elif route_length > 5:
            score -= 8

        # Keep the value bounded between 0 and 100.
        return max(0, min(100, score))

    def validate_assigned_route(
        self,
        truck_id: Any,
        dump_id: Any,
        route: Sequence[Sequence[float]],
        obstacles: Sequence[Sequence[float]],
    ) -> Dict[str, Any]:
        """Validate a truck's route to a dump and return a safety decision.

        Args:
            truck_id: ID of the assigned truck.
            dump_id: ID of the selected dump.
            route: Planned route points.
            obstacles: List of obstacle bounding boxes.

        Returns:
            A structured safety result.
        """
        route_is_safe = self.validate_route(route, obstacles)
        score = self.calculate_safety_score(route)

        if route_is_safe and score >= self.min_safety_score:
            return {
                "truck_id": truck_id,
                "dump_id": dump_id,
                "safe": True,
                "safety_score": score,
                "remarks": "Route validated successfully.",
            }

        if route_is_safe:
            return {
                "truck_id": truck_id,
                "dump_id": dump_id,
                "safe": True,
                "safety_score": score,
                "remarks": "Route validated successfully.",
            }

        # Route is unsafe if obstacle intersects or route is invalid.
        return {
            "truck_id": truck_id,
            "dump_id": dump_id,
            "safe": False,
            "safety_score": max(0, score - 30),
            "remarks": "Obstacle detected on planned route.",
        }
