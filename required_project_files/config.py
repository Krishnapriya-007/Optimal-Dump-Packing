"""Project-wide configuration values.

This file centralizes the parameters that may need to be tuned for different
runtime environments, model versions, or operating constraints without modifying
individual agent implementations.
"""

# YOLO
YOLO_MODEL_PATH = "data/weights/yolov8n.pt"
# Minimum confidence score required for a YOLO detection to be treated as valid.
YOLO_CONFIDENCE_THRESHOLD = 0.5

# MiDaS
MIDAS_MODEL_TYPE = "DPT_Large"
# MiDaS model variant used for relative depth estimation in the dump fill model.

# Dump Fill Classification Thresholds
# Depth values are compared to these thresholds to determine whether a dump is
# empty, partially filled, or fully filled.
EMPTY_THRESHOLD = 0.25
HALF_FILLED_THRESHOLD = 0.65
FULL_THRESHOLD = 0.85

# Planning Agent
# Weighted scoring used by the Planning Agent when ranking dump sites.
DISTANCE_WEIGHT = 1.0
FILL_LEVEL_WEIGHT = 1.0
ACCESSIBILITY_WEIGHT = 1.0

# Fleet Agent
# Maximum number of trucks that the fleet controller may track simultaneously.
MAX_TRUCKS = 10
# Approximate nominal truck speed used as a basic operational parameter.
TRUCK_SPEED = 25.0

# Safety Agent
# Minimum acceptable route safety score before a route is considered acceptable.
MIN_SAFETY_SCORE = 70

# Path Planner
# Grid size used as the planner's spatial resolution for route generation.
GRID_SIZE = 1
# Allow diagonal moves when generating neighboring grid cells for A* routing.
ALLOW_DIAGONAL = True

# Input / Output
# Folder used to store source images for model inference.
INPUT_IMAGE_FOLDER = "data/images"
# Folder used to hold generated output artifacts such as annotated images and JSON logs.
OUTPUT_FOLDER = "outputs"
