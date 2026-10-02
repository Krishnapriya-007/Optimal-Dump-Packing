"""Fleet Agent for assigning trucks to selected dump sites.

This module is responsible only for choosing the most suitable truck for a dump
site after the Planning Agent has ranked candidate dump areas. It does not
handle routing, collision checks, or path validation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from config import MAX_TRUCKS, TRUCK_SPEED


class FleetAgent:
    """Assign the nearest available truck to a selected dump site."""

    def __init__(self, max_trucks: int = MAX_TRUCKS, truck_speed: float = TRUCK_SPEED):
        """Initialize the Fleet Agent.

        The Fleet Agent keeps track of trucks that are already assigned so that it
        can avoid multi-assigning the same truck to multiple dumps.
        """
        self.assigned_truck_ids: set[int] = set()
        self.max_trucks = max_trucks
        self.truck_speed = truck_speed

    def calculate_distance(self, truck_bbox: List[float], dump_bbox: List[float]) -> float:
        """Compute the Euclidean distance between a truck and a dump site.

        Args:
            truck_bbox: Truck bounding box as ``[x1, y1, x2, y2]``.
            dump_bbox: Dump bounding box as ``[x1, y1, x2, y2]``.

        Returns:
            The distance between the centers of the two boxes.
        """
        truck_center_x = (truck_bbox[0] + truck_bbox[2]) / 2.0
        truck_center_y = (truck_bbox[1] + truck_bbox[3]) / 2.0
        dump_center_x = (dump_bbox[0] + dump_bbox[2]) / 2.0
        dump_center_y = (dump_bbox[1] + dump_bbox[3]) / 2.0

        distance = ((truck_center_x - dump_center_x) ** 2 + (truck_center_y - dump_center_y) ** 2) ** 0.5
        return float(distance)

    def assign_truck(
        self,
        trucks: List[Dict[str, Any]],
        selected_dump: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Assign the nearest available truck to the selected dump site.

        Selection rules:
        1. Only consider trucks that are not already assigned.
        2. Pick the truck with the minimum distance to the selected dump.
        3. If no eligible trucks exist, return a no-available-truck message.

        Args:
            trucks: List of truck detections from the Vision Agent.
            selected_dump: Selected dump site from the Planning Agent.

        Returns:
            A dictionary describing the truck assignment, or a no-availability
            status if no suitable truck exists.
        """
        if not trucks:
            return {"status": "No Available Truck"}

        if not selected_dump:
            return {"status": "No Available Truck"}

        dump_bbox = selected_dump.get("bbox", [0, 0, 0, 0])
        dump_id = selected_dump.get("dump_id", selected_dump.get("id", 0))

        available_trucks: List[Dict[str, Any]] = []

        # Ignore trucks already assigned for a different dump.
        for truck in trucks:
            truck_id = truck.get("id")
            if truck_id in self.assigned_truck_ids:
                continue
            available_trucks.append(truck)

        if not available_trucks:
            return {"status": "No Available Truck"}

        best_match: Optional[Dict[str, Any]] = None
        best_distance: Optional[float] = None

        # Choose the truck with the minimum distance to the dump.
        for truck in available_trucks:
            truck_bbox = truck.get("bbox", [0, 0, 0, 0])
            distance = self.calculate_distance(truck_bbox, dump_bbox)

            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_match = {
                    "truck_id": truck.get("id"),
                    "distance": distance,
                    "bbox": truck_bbox,
                }

        if best_match is None or best_distance is None:
            return {"status": "No Available Truck"}

        assigned_truck_id = best_match["truck_id"]
        self.assigned_truck_ids.add(assigned_truck_id)

        return {
            "truck_id": assigned_truck_id,
            "dump_id": dump_id,
            "distance": round(best_distance, 2),
            "status": "Assigned",
        }
