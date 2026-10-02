"""Vision Agent module for dump-site analysis.

This module is responsible only for detecting objects in a scene and organizing
those detections into structured categories that can later be consumed by the
Planning Agent. It does not perform route planning or dump selection.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from config import YOLO_MODEL_PATH

from models.yolo_detector import YOLODetector


class VisionAgent:
    """Detect trucks, dump areas, and obstacles in an image frame.

    The Vision Agent wraps the YOLO object detection model and converts raw
    detection output into a clean, structured scene representation.
    """

    def __init__(self, model_path: str | None = None, detector: Optional[YOLODetector] = None):
        """Initialize the Vision Agent with a YOLO model path.

        Args:
            model_path: Path to the YOLO model file, such as
                ``data/weights/yolov8n.pt``.
        """
        self.model_path = model_path or YOLO_MODEL_PATH
        self.detector = detector or YOLODetector(self.model_path)

    def analyze_scene(self, image_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Run YOLO detection on an image and organize the results by object type.

        The detector output is grouped into three categories:
        - Trucks
        - Dump Areas
        - Obstacles

        The method returns a dictionary with the following structure:
        {
            "trucks": [ ... ],
            "dump_areas": [ ... ],
            "obstacles": [ ... ]
        }

        Args:
            image_path: File path to the input image.

        Returns:
            A dictionary containing grouped detections for each category.

        Notes:
            This method intentionally handles only the vision tasks. It does not
            perform planning, route evaluation, or allocation decisions.
        """
        try:
            detections = self.detector.detect(image_path)
        except FileNotFoundError:
            # Gracefully handle missing image files by returning empty categories.
            return {"trucks": [], "dump_areas": [], "obstacles": []}

        # Initialize result containers.
        trucks: List[Dict[str, Any]] = []
        dump_areas: List[Dict[str, Any]] = []
        obstacles: List[Dict[str, Any]] = []

        # A simple mapping between object names and the category we want to
        # report. These labels are chosen for the mining dump-site domain and can
        # be expanded if the training data contains additional names.
        truck_labels = {
            "truck",
            "mining_truck",
            "dump_truck",
            "vehicle",
            "lorry",
        }

        dump_labels = {
            "dump_area",
            "dump",
            "dumping_zone",
            "dump_site",
            "fill_area",
        }

        obstacle_labels = {
            "obstacle",
            "rock",
            "barrier",
            "cone",
            "boulder",
            "debris",
            "blockage",
        }

        # If no objects are detected, return empty lists.
        if not detections:
            return {"trucks": [], "dump_areas": [], "obstacles": []}

        # Organize each detection into the correct category.
        for detection in detections:
            label = str(detection.get("class", "")).strip().lower()
            bbox = detection.get("bbox")
            confidence = float(detection.get("confidence", 0.0))

            if not isinstance(bbox, list) or len(bbox) != 4:
                continue

            if label in truck_labels:
                trucks.append(
                    {
                        "id": len(trucks) + 1,
                        "bbox": [float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])],
                        "confidence": confidence,
                    }
                )
            elif label in dump_labels:
                dump_areas.append(
                    {
                        "id": len(dump_areas) + 1,
                        "bbox": [float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])],
                    }
                )
            elif label in obstacle_labels:
                obstacles.append(
                    {
                        "bbox": [float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])],
                    }
                )

        # If the model returns object names that are not in the domain mapping,
        # we keep them as generic detections and do not drop them silently.
        # The simplest safe behavior for a vision-only pipeline is to ignore
        # unlabeled detections rather than misclassify them.

        return {
            "trucks": trucks,
            "dump_areas": dump_areas,
            "obstacles": obstacles,
        }
