"""Planning Agent for choosing the best dump site.

This module is responsible for evaluating candidate dump areas and selecting the
best dump site for a truck. It does not perform allocation or path planning.
Only scoring and selection are handled here.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from config import ACCESSIBILITY_WEIGHT, DISTANCE_WEIGHT, FILL_LEVEL_WEIGHT


class PlanningAgent:
    """Select the most suitable dump site based on fill, distance, and access."""

    def __init__(self):
        """Initialize the Planning Agent.

        The agent stores the input detections and uses a simple rule-based score
        system. This keeps the implementation understandable and easy to extend.
        """
        self.truck_detections: List[Dict[str, Any]] = []
        self.dump_detections: List[Dict[str, Any]] = []
        self.obstacle_detections: List[Dict[str, Any]] = []
        self.dump_fill_status: Dict[int, str] = {}
        self.distance_weight = DISTANCE_WEIGHT
        self.fill_level_weight = FILL_LEVEL_WEIGHT
        self.accessibility_weight = ACCESSIBILITY_WEIGHT

    def calculate_dump_score(
        self,
        dump: Dict[str, Any],
        fill_status: str,
        truck_position: Optional[List[float]] = None,
        obstacle_present: bool = False,
    ) -> Dict[str, Any]:
        """Calculate a dump site's final score.

        The final score is based on three components:
        1. Fill level score
        2. Distance score
        3. Accessibility score

        Args:
            dump: Dump dictionary containing at least ``id`` and ``bbox``.
            fill_status: One of ``Empty``, ``Half-Filled``, or ``Fully Filled``.
            truck_position: Truck position used to estimate distance. If not
                supplied, a default value is used.
            obstacle_present: Whether the route to the dump is blocked.

        Returns:
            A dictionary containing the dump identifier, fill status, score, and
            distance estimate.
        """
        dump_id = dump.get("id", 0)
        bbox = dump.get("bbox", [0, 0, 0, 0])

        # Compute the dump center for rough distance estimation.
        center_x = (bbox[0] + bbox[2]) / 2.0
        center_y = (bbox[1] + bbox[3]) / 2.0

        if truck_position is not None:
            truck_x, truck_y = truck_position
            distance = ((center_x - truck_x) ** 2 + (center_y - truck_y) ** 2) ** 0.5
        else:
            # Default fallback if no truck position is available.
            distance = abs(center_x) + abs(center_y)

        # Fill score based on dump fill level requirement.
        fill_score_map = {
            "Empty": 10,
            "Half-Filled": 5,
            "Fully Filled": 0,
        }
        fill_score = fill_score_map.get(fill_status, 0)

        # Distance score: closer dumps get higher scores.
        # A simple inverse-distance rule keeps the scoring easy to understand.
        distance_score = max(0, 20 - int(distance))

        # Accessibility score.
        accessibility_score = 5 if not obstacle_present else -5

        # Final score: fill + distance + accessibility.
        final_score = (
            fill_score * self.fill_level_weight
            + distance_score * self.distance_weight
            + accessibility_score * self.accessibility_weight
        )

        return {
            "dump_id": dump_id,
            "fill_status": fill_status,
            "score": final_score,
            "distance": round(distance, 2),
        }

    def select_best_dump(
        self,
        truck_detections: List[Dict[str, Any]],
        dump_detections: List[Dict[str, Any]],
        obstacle_detections: List[Dict[str, Any]],
        dump_fill_status: Dict[int, str],
        truck_position: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Rank all dumps and return the best dump for a truck.

        Args:
            truck_detections: Truck detections from the vision system.
            dump_detections: Dump area detections from the vision system.
            obstacle_detections: Obstacle detections from the vision system.
            dump_fill_status: Dict mapping dump ID to status, e.g. ``{2: "Half-Filled"}``.
            truck_position: Optional truck position used for distance calculation.

        Returns:
            A dictionary containing:
            - ``selected_dump``: the best-ranked dump metadata
            - ``all_rankings``: all dump candidates sorted by score descending
        """
        self.truck_detections = truck_detections
        self.dump_detections = dump_detections
        self.obstacle_detections = obstacle_detections
        self.dump_fill_status = dump_fill_status

        if not dump_detections:
            return {
                "selected_dump": {
                    "dump_id": None,
                    "score": 0,
                    "fill_status": "Unknown",
                    "distance": 0,
                },
                "all_rankings": [],
            }

        rankings: List[Dict[str, Any]] = []

        # Evaluate every dump site and rank it by the final score.
        for dump in dump_detections:
            dump_id = dump.get("id", 0)
            fill_status = dump_fill_status.get(dump_id, "Empty")

            # Determine whether an obstacle intersects the dump area.
            obstacle_present = False
            for obstacle in obstacle_detections:
                obstacle_bbox = obstacle.get("bbox", [0, 0, 0, 0])
                dump_bbox = dump.get("bbox", [0, 0, 0, 0])

                overlap = not (
                    obstacle_bbox[2] < dump_bbox[0]
                    or obstacle_bbox[0] > dump_bbox[2]
                    or obstacle_bbox[3] < dump_bbox[1]
                    or obstacle_bbox[1] > dump_bbox[3]
                )

                if overlap:
                    obstacle_present = True
                    break

            score_details = self.calculate_dump_score(
                dump=dump,
                fill_status=fill_status,
                truck_position=truck_position,
                obstacle_present=obstacle_present,
            )

            rankings.append(
                {
                    "dump_id": score_details["dump_id"],
                    "score": score_details["score"],
                    "fill_status": score_details["fill_status"],
                    "distance": score_details["distance"],
                }
            )

        # Sort dump sites by highest score, descending.
        rankings.sort(key=lambda item: item["score"], reverse=True)

        selected_dump = rankings[0] if rankings else {
            "dump_id": None,
            "score": 0,
            "fill_status": "Unknown",
            "distance": 0,
        }

        return {
            "selected_dump": selected_dump,
            "all_rankings": rankings,
        }
