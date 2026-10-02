# Agentic AI-Based Dump Site Optimization for Autonomous Mining Operations

## Abstract

Mining operations depend on efficient coordination of haul trucks and dump sites. Manual or fixed-rule allocation can respond poorly to changing site conditions, resulting in congestion, uneven utilization, and avoidable delays. This project presents an Agentic AI-based workflow for selecting dump sites and coordinating truck assignments from input images. A YOLOv8 detector identifies trucks, candidate dump areas, and obstacles, while MiDaS estimates relative depth to classify dump fill levels. A Vision Agent structures detections for downstream reasoning. The Planning Agent ranks available dump sites using fill, distance, and accessibility information; the Fleet Agent assigns a suitable available truck. The Path Planner computes a route using A*, and the Safety Agent validates the proposed route against detected obstacles before visualization. The application records assignments and produces an annotated image and JSON result for review. By organizing perception, planning, coordination, routing, and safety as cooperating agents, the prototype demonstrates a modular approach to dump allocation. The current implementation is image-driven and intended as a foundation for future integration with live cameras, fleet telemetry, and operational systems.

## Problem Statement

Traditional dump allocation is often manual or based on fixed rules. These approaches may not adapt well to changing truck positions, dump fill levels, and obstacles. As a result, mining operations can experience congestion, uneven dump-site utilization, longer truck waiting times, and reduced fleet efficiency. A coordinated, perception-driven allocation workflow can help improve these decisions.

## Objectives

- Detect trucks, dump sites, and obstacles using YOLOv8.
- Estimate dump fill levels using MiDaS depth estimation.
- Select an optimal dump site using Agentic AI planning.
- Coordinate truck allocation intelligently across the fleet.
- Generate safe and efficient routes using the A* algorithm.

## Features

| Feature | Purpose |
|---|---|
| YOLOv8-based object detection | Identifies trucks, dump sites, and obstacles in an image. |
| MiDaS depth estimation | Estimates relative depth for dump fill classification. |
| Vision Agent | Groups detections into structured scene data. |
| Planning Agent | Ranks dump sites using fill, distance, and accessibility. |
| Fleet Agent | Assigns an available truck to the selected dump site. |
| Safety Agent | Validates planned routes against detected obstacles. |
| A* Path Planning | Generates a route between a truck and its assigned dump. |
| Real-time dump allocation | Repeats allocation as tasks and dump states progress. |
| Continuous Agentic AI workflow | Orchestrates perception, planning, assignment, and validation. |
| Visualization dashboard | Displays detections, the selected dump, route, and safety result. |

## System Architecture

The application processes an input image through the following workflow:

```text
Input Image
  ↓
YOLO Detector
  ↓
Vision Agent
  ↓
MiDaS Depth Estimation
  ↓
Planning Agent
  ↓
Fleet Agent
  ↓
Safety Agent
  ↓
A* Path Planner
  ↓
Visualization
  ↓
Final Dump Allocation
```

## Project Structure

```text
final_year_project/
├── agents/
├── models/
├── utils/
├── data/
├── outputs/
├── config.py
├── app.py
├── requirements.txt
└── README.md
```

## Technologies Used

- Python
- YOLOv8
- MiDaS
- OpenCV
- NumPy
- PyTorch
- A* Algorithm
- Agentic AI

## Installation

Clone the repository and install its dependencies:

```bash
git clone <repository-url>
cd final_year_project
pip install -r requirements.txt
```

Place the YOLO weights at the path configured in `config.py`, and provide an input image in `data/images/`.

## Running the Project

From the project root, run:

```bash
python app.py
```

## Expected Output

The workflow reports and records:

- Detected trucks and dump sites.
- Estimated dump fill levels.
- The selected dump site and assigned truck.
- The planned route and route distance.
- The route safety result and safety score.
- An annotated output image at `outputs/final_output.jpg`.
- A JSON result file at `outputs/result.json`.

## Future Enhancements

- Multi-camera integration.
- Drone-based monitoring.
- Reinforcement Learning for adaptive planning.
- Real-time IoT sensor integration.
- Digital Twin implementation.
- Cloud deployment.

## Authors

Student Name:  
College:  
Department:  
Guide:

## License

Educational Use Only.
