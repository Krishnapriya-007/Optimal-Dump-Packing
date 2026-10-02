"""YOLO object detection module for the dump-site optimization project.

This module provides a lightweight, standalone wrapper around Ultralytics
YOLOv8 so it can later be reused by the Vision Agent without embedding any
agent-specific logic.
"""

from __future__ import annotations

from typing import Any, Dict, List

import cv2
from ultralytics import YOLO

from config import YOLO_CONFIDENCE_THRESHOLD, YOLO_MODEL_PATH


class YOLODetector:
    """Simple wrapper for loading and running YOLOv8 object detection.

    The class is intentionally kept independent from the rest of the project so
    it can be reused by a Vision Agent or any other component that needs object
    detection from a local image.
    """

    def __init__(self, model_path: str | None = None):
        """Initialize the YOLOv8 model from the provided model path.

        Args:
            model_path: Path to the YOLO weights file. For this project, it is
                expected to be a local file such as
                ``data/weights/yolov8n.pt``.
        """
        self.model_path = model_path or YOLO_MODEL_PATH
        self.confidence_threshold = YOLO_CONFIDENCE_THRESHOLD
        self.model = YOLO(self.model_path)

    def detect(self, image_path: str) -> List[Dict[str, Any]]:
        """Run YOLO inference on an image and return detected objects.

        Args:
            image_path: Path to the input image file.

        Returns:
            A list of dictionaries with the following keys:
            - ``class``: detected class name
            - ``confidence``: detection confidence score
            - ``bbox``: bounding box in the form ``[x1, y1, x2, y2]``

        Notes:
            This method converts the YOLO result to a project-friendly format and
            leaves the actual agent orchestration to the higher-level Vision Agent.
        """
        # Load the input image using OpenCV.
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Unable to load image: {image_path}")

        # Run inference with the loaded YOLO model.
        results = self.model(image, verbose=False)

        detections: List[Dict[str, Any]] = []

        # The `results` object contains multiple predictions. Each prediction
        # includes boxes, class IDs, confidences, and names.
        for result in results:
            # Extract class IDs and names for all boxes in the current result.
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                # `xyxy` gives coordinates in pixel space as [x1, y1, x2, y2].
                x1, y1, x2, y2 = map(float, box.xyxy[0].tolist())
                conf = float(box.conf[0])
                if conf < self.confidence_threshold:
                    continue
                class_id = int(box.cls[0])
                class_name = result.names.get(class_id, str(class_id))

                detections.append(
                    {
                        "class": class_name,
                        "confidence": conf,
                        "bbox": [x1, y1, x2, y2],
                    }
                )

        return detections
