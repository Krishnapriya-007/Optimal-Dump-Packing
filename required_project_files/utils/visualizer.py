"""Visualization utilities for the dump-site optimization workflow.

This module is responsible only for drawing detections, dump selection, and the
final route on images using OpenCV. It is kept separate from the agent logic so
it can be reused in future workflows or demos.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

import cv2
import numpy as np


class Visualizer:
    """Draw the dump-site optimization pipeline on an image."""

    def draw_trucks(self, image: np.ndarray, trucks: Sequence[Dict[str, Any]]) -> np.ndarray:
        """Draw truck bounding boxes on the image.

        Args:
            image: Source image as a NumPy array.
            trucks: List of truck dictionaries with ``id`` and ``bbox`` keys.

        Returns:
            A modified image with truck rectangles and labels.
        """
        image_copy = image.copy()
        for truck in trucks:
            bbox = truck.get("bbox", [0, 0, 0, 0])
            truck_id = truck.get("id", "T")
            if len(bbox) != 4:
                continue

            x1, y1, x2, y2 = [int(v) for v in bbox]
            cv2.rectangle(image_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                image_copy,
                f"Truck {truck_id}",
                (x1, max(0, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )
        return image_copy

    def draw_dump_areas(self, image: np.ndarray, dump_areas: Sequence[Dict[str, Any]]) -> np.ndarray:
        """Draw dump-area bounding boxes on the image.

        Args:
            image: Source image as a NumPy array.
            dump_areas: List of dump dictionaries with ``id`` and ``bbox`` keys.

        Returns:
            A modified image with dump rectangles and labels.
        """
        image_copy = image.copy()
        for dump in dump_areas:
            bbox = dump.get("bbox", [0, 0, 0, 0])
            dump_id = dump.get("id", "D")
            if len(bbox) != 4:
                continue

            x1, y1, x2, y2 = [int(v) for v in bbox]
            cv2.rectangle(image_copy, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(
                image_copy,
                f"Dump {dump_id}",
                (x1, max(0, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2,
            )
        return image_copy

    def draw_obstacles(self, image: np.ndarray, obstacles: Sequence[Dict[str, Any]]) -> np.ndarray:
        """Draw obstacle bounding boxes on the image.

        Args:
            image: Source image as a NumPy array.
            obstacles: List of obstacle dictionaries with ``bbox`` keys.

        Returns:
            A modified image with obstacle rectangles and labels.
        """
        image_copy = image.copy()
        for obstacle in obstacles:
            bbox = obstacle.get("bbox", [0, 0, 0, 0])
            if len(bbox) != 4:
                continue

            x1, y1, x2, y2 = [int(v) for v in bbox]
            cv2.rectangle(image_copy, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(
                image_copy,
                "Obstacle",
                (x1, max(0, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2,
            )
        return image_copy

    def draw_selected_dump(self, image: np.ndarray, selected_dump: Optional[Dict[str, Any]]) -> np.ndarray:
        """Highlight the selected dump area with a yellow rectangle.

        Args:
            image: Source image as a NumPy array.
            selected_dump: Selected dump dictionary with ``id`` and ``bbox``.

        Returns:
            A modified image with the selected dump highlighted.
        """
        image_copy = image.copy()
        if not selected_dump:
            return image_copy

        bbox = selected_dump.get("bbox", [0, 0, 0, 0])
        dump_id = selected_dump.get("dump_id", selected_dump.get("id", "D"))
        if len(bbox) != 4:
            return image_copy

        x1, y1, x2, y2 = [int(v) for v in bbox]
        cv2.rectangle(image_copy, (x1, y1), (x2, y2), (0, 255, 255), 3)
        cv2.putText(
            image_copy,
            f"Selected Dump {dump_id}",
            (x1, max(0, y1 - 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )
        return image_copy

    def draw_route(self, image: np.ndarray, path: Sequence[Sequence[float]]) -> np.ndarray:
        """Draw the A* path over the image as a green polyline.

        Args:
            image: Source image as a NumPy array.
            path: List of coordinate points in the form ``[[x, y], ...]``.

        Returns:
            Modified image with the path overlay.
        """
        image_copy = image.copy()
        if not path:
            return image_copy

        points = [(int(x), int(y)) for x, y in path]
        if len(points) >= 2:
            cv2.polylines(image_copy, [np.array(points, dtype=np.int32)], False, (0, 255, 0), 3)

        # Mark the first and last points to make the route easy to interpret.
        if points:
            cv2.circle(image_copy, points[0], 5, (0, 255, 0), -1)
            cv2.circle(image_copy, points[-1], 5, (0, 255, 0), -1)

        return image_copy

    def display_dashboard(self, image: np.ndarray, results: Dict[str, Any]) -> np.ndarray:
        """Overlay the final analysis results on the image.

        Args:
            image: Source image as a NumPy array.
            results: Dictionary containing data such as selected dump, route, and
                safety information.

        Returns:
            A modified image showing the final dashboard overlay.
        """
        image_copy = image.copy()
        height, width = image_copy.shape[:2]

        # Create a translucent panel at the top-left of the image.
        overlay = image_copy.copy()
        cv2.rectangle(overlay, (10, 10), (width - 10, 170), (30, 30, 30), -1)
        cv2.addWeighted(overlay, 0.7, image_copy, 0.3, 0, image_copy)

        selected_dump = results.get("selected_dump")
        if selected_dump:
            fill_status = selected_dump.get("fill_status", "Unknown")
            score = selected_dump.get("score", 0)
            dump_id = selected_dump.get("dump_id", "N/A")
            cv2.putText(
                image_copy,
                f"Dump ID: {dump_id}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )
            cv2.putText(
                image_copy,
                f"Fill Status: {fill_status}",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )
            cv2.putText(
                image_copy,
                f"Score: {score}",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

        safety_result = results.get("safety_result")
        if safety_result:
            safe = safety_result.get("safe", False)
            safety_score = safety_result.get("safety_score", 0)
            color = (0, 255, 0) if safe else (0, 0, 255)
            label = "Safe" if safe else "Unsafe"
            cv2.putText(
                image_copy,
                f"Safety: {label} ({safety_score})",
                (20, 130),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

        return image_copy

    def save_final_output(self, image: np.ndarray, output_path: str = "outputs/final_output.jpg") -> str:
        """Save the final visualization to disk.

        Args:
            image: Final annotated image.
            output_path: Target path for saving the output file.

        Returns:
            The saved output path.
        """
        output_dir = output_path.rsplit("/", 1)[0] if "/" in output_path else "."
        import os
        os.makedirs(output_dir, exist_ok=True)

        cv2.imwrite(output_path, image)
        return output_path
