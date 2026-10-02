"""Continuous Agentic AI workflow orchestrator for dump-site optimization.

This application repeatedly runs the Vision, MiDaS, Planning, Fleet, Path
Planning, and Safety stages until either all trucks have completed their tasks
or all dump sites are fully filled. The orchestration remains in this file only;
individual agents are kept unchanged.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import cv2

from config import INPUT_IMAGE_FOLDER, OUTPUT_FOLDER, YOLO_MODEL_PATH

from agents.fleet_agent import FleetAgent
from agents.planning_agent import PlanningAgent
from agents.safety_agent import SafetyAgent
from agents.vision_agent import VisionAgent
from models.midas_depth import MiDaSDepthEstimator
from models.path_planner import PathPlanner
from models.yolo_detector import YOLODetector
from utils.visualizer import Visualizer


def _advance_fill_status(fill_status: str) -> str:
    """Advance fill status from one stage to the next."""
    status_cycle = ["Empty", "Half-Filled", "Fully Filled"]
    if fill_status not in status_cycle:
        return "Empty"
    current_index = status_cycle.index(fill_status)
    next_index = min(current_index + 1, len(status_cycle) - 1)
    return status_cycle[next_index]


def _save_history(history: List[Dict[str, Any]]) -> None:
    """Persist assignment history to the output JSON file."""
    output_path = os.path.join(OUTPUT_FOLDER, "assignment_history.json")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)


def _save_result(result: Dict[str, Any]) -> None:
    """Persist the complete pipeline result as JSON."""
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    result_path = os.path.join(OUTPUT_FOLDER, "result.json")
    with open(result_path, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)


def run_agent_pipeline(image_path: str) -> Dict[str, Any]:
    """Run the continuous agentic workflow until all tasks are complete.

    The workflow loops as follows:
    1. Vision Agent detects trucks, dump areas, and obstacles.
    2. MiDaS estimates dump fill levels.
    3. Planning Agent selects the best dump site.
    4. Fleet Agent assigns the nearest available truck.
    5. Path Planner computes a safe route.
    6. Safety Agent validates the route.
    7. The truck is marked available again and the dump status is updated.
    8. The loop continues until all dump sites are filled or all trucks are done.

    Args:
        image_path: Path to the input image.

    Returns:
        Final status information for the workflow.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    detector = YOLODetector(YOLO_MODEL_PATH)
    vision_agent = VisionAgent(YOLO_MODEL_PATH, detector=detector)
    planning_agent = PlanningAgent()
    fleet_agent = FleetAgent()
    safety_agent = SafetyAgent()
    visualizer = Visualizer()
    path_planner = PathPlanner()
    try:
        depth_estimator = MiDaSDepthEstimator()
    except Exception as exc:
        depth_estimator = None
        print(f"Warning: MiDaS is unavailable; using fallback fill status ({exc}).")

    assignment_history: List[Dict[str, Any]] = []
    fill_progress: Dict[int, str] = {}
    iteration = 1

    final_image = cv2.imread(image_path)
    if final_image is None:
        raise ValueError(f"Unable to read image: {image_path}")

    while True:
        scene = vision_agent.analyze_scene(image_path)
        trucks = scene.get("trucks", [])
        dump_areas = scene.get("dump_areas", [])
        obstacles = scene.get("obstacles", [])

        if not trucks or not dump_areas:
            print("--------------------------------------")
            print("Iteration:", iteration)
            print("Status: No detections found.")
            print("--------------------------------------")
            break

        try:
            depth_map = depth_estimator.estimate_depth(image_path) if depth_estimator else None
        except Exception:
            depth_map = None

        dump_fill_status: Dict[int, str] = {}
        dump_depth_results: Dict[int, Dict[str, Any]] = {}
        if depth_map is not None:
            for dump in dump_areas:
                dump_id = dump.get("id", 1)
                classification = depth_estimator.classify_dump_fill(depth_map, dump.get("bbox", [0, 0, 0, 0]))
                dump_depth_results[dump_id] = classification
                dump_fill_status[dump_id] = fill_progress.get(
                    dump_id, classification.get("fill_status", "Empty")
                )
        else:
            for dump in dump_areas:
                dump_id = dump.get("id", 1)
                dump_fill_status[dump_id] = fill_progress.get(dump_id, "Half-Filled")
                dump_depth_results[dump_id] = {
                    "dump_id": dump_id,
                    "fill_status": dump_fill_status[dump_id],
                    "depth_inference_available": False,
                }

        # Remove fully filled dumps from active selection.
        active_dumps = [dump for dump in dump_areas if dump_fill_status.get(dump.get("id", 1), "Empty") != "Fully Filled"]
        if not active_dumps:
            print("--------------------------------------")
            print(f"Iteration: {iteration}")
            print("Truck Assigned: None")
            print("Selected Dump: None")
            print("Dump Fill Level: All dumps are full.")
            print("Route Distance: 0")
            print("Safety Score: 0")
            print("--------------------------------------")
            break

        available_trucks = [truck for truck in trucks if truck.get("id") not in fleet_agent.assigned_truck_ids]
        if not available_trucks:
            fleet_agent.assigned_truck_ids.clear()
            available_trucks = trucks

        # Choose the most suitable dump according to the rule-based planner.
        planning_result = planning_agent.select_best_dump(
            truck_detections=available_trucks,
            dump_detections=active_dumps,
            obstacle_detections=obstacles,
            dump_fill_status=dump_fill_status,
            truck_position=None,
        )

        selected_dump = planning_result.get("selected_dump", {})
        selected_dump_id = selected_dump.get("dump_id")

        if selected_dump_id is None:
            print("--------------------------------------")
            print(f"Iteration: {iteration}")
            print("Truck Assigned: None")
            print("Selected Dump: None")
            print("Dump Fill Level: No valid dump selected.")
            print("Route Distance: 0")
            print("Safety Score: 0")
            print("--------------------------------------")
            break

        selected_dump_match = next((dump for dump in active_dumps if dump.get("id") == selected_dump_id), active_dumps[0])
        selected_dump_with_bbox = {
            **selected_dump,
            "bbox": selected_dump_match.get("bbox", [0, 0, 0, 0]),
            "dump_id": selected_dump_id,
        }

        assignment = fleet_agent.assign_truck(available_trucks, selected_dump_with_bbox)
        if assignment.get("status") == "No Available Truck":
            print("--------------------------------------")
            print(f"Iteration: {iteration}")
            print("Truck Assigned: None")
            print("Selected Dump:", selected_dump_id)
            print("Dump Fill Level:", dump_fill_status.get(selected_dump_id, "Unknown"))
            print("Route Distance: 0")
            print("Safety Score: 0")
            print("--------------------------------------")
            break

        truck_id = assignment.get("truck_id")
        assigned_truck = next((truck for truck in trucks if truck.get("id") == truck_id), None)
        if assigned_truck is None:
            break

        truck_bbox = assigned_truck.get("bbox", [0, 0, 0, 0])
        dump_bbox = selected_dump_with_bbox.get("bbox", [0, 0, 0, 0])

        start = [
            (truck_bbox[0] + truck_bbox[2]) / 2.0,
            (truck_bbox[1] + truck_bbox[3]) / 2.0,
        ]
        goal = [
            (dump_bbox[0] + dump_bbox[2]) / 2.0,
            (dump_bbox[1] + dump_bbox[3]) / 2.0,
        ]

        obstacle_points: List[List[float]] = []
        for obstacle in obstacles:
            bbox = obstacle.get("bbox", [0, 0, 0, 0])
            if len(bbox) == 4:
                x1, x2 = sorted((int(bbox[0]), int(bbox[2])))
                y1, y2 = sorted((int(bbox[1]), int(bbox[3])))
                obstacle_points.extend(
                    [[x, y] for x in range(x1, x2 + 1) for y in range(y1, y2 + 1)]
                )

        route = path_planner.find_path(start, goal, obstacle_points)
        route = route if route is not None else [start, goal]

        route_distance = 0.0
        for i in range(1, len(route)):
            prev = route[i - 1]
            curr = route[i]
            route_distance += ((curr[0] - prev[0]) ** 2 + (curr[1] - prev[1]) ** 2) ** 0.5

        safety_result = safety_agent.validate_assigned_route(
            truck_id=truck_id,
            dump_id=selected_dump_id,
            route=route,
            obstacles=[obstacle.get("bbox", [0, 0, 0, 0]) for obstacle in obstacles],
        )

        # Mark truck as available again after dumping is considered complete.
        fleet_agent.assigned_truck_ids.discard(truck_id)

        # Update fill status of the selected dump for the next iteration.
        current_fill = dump_fill_status.get(selected_dump_id, "Empty")
        updated_fill = _advance_fill_status(current_fill)
        dump_fill_status[selected_dump_id] = updated_fill
        fill_progress[selected_dump_id] = updated_fill

        history_entry = {
            "iteration": iteration,
            "detections": {
                "trucks": trucks,
                "dump_areas": dump_areas,
                "obstacles": obstacles,
            },
            "depth_classification": dump_depth_results.get(selected_dump_id, {}),
            "dump_fill_status_before_assignment": current_fill,
            "truck_id": truck_id,
            "dump_id": selected_dump_id,
            "selected_dump": selected_dump_with_bbox,
            "planning_result": planning_result,
            "assignment": assignment,
            "route": route,
            "dump_fill_level": updated_fill,
            "route_distance": round(route_distance, 2),
            "safety_result": safety_result,
            "safety_score": safety_result.get("safety_score", 0),
            "status": safety_result.get("remarks", "Route validated successfully."),
            "safe": safety_result.get("safe", False),
        }
        assignment_history.append(history_entry)
        _save_history(assignment_history)

        # Save annotated output with the latest route and dashboard.
        image = cv2.imread(image_path)
        if image is not None:
            image = visualizer.draw_trucks(image, trucks)
            image = visualizer.draw_dump_areas(image, dump_areas)
            image = visualizer.draw_obstacles(image, obstacles)
            image = visualizer.draw_selected_dump(image, selected_dump_with_bbox)
            image = visualizer.draw_route(image, route)
            dashboard_results = {
                "selected_dump": {
                    **selected_dump_with_bbox,
                    "fill_status": updated_fill,
                    "score": selected_dump.get("score", 0),
                },
                "safety_result": safety_result,
                "route": route,
                "distance": route_distance,
            }
            image = visualizer.display_dashboard(image, dashboard_results)
            final_image = image

        print("--------------------------------------")
        print(f"Iteration: {iteration}")
        print(f"Truck Assigned: {truck_id}")
        print(f"Selected Dump: {selected_dump_id}")
        print(f"Dump Fill Level: {updated_fill}")
        print(f"Route Distance: {round(route_distance, 2)}")
        print(f"Safety Score: {safety_result.get('safety_score', 0)}")
        print("--------------------------------------")

        # Remove completed tasks from the queue once fully filled.
        if updated_fill == "Fully Filled":
            dump_areas = [dump for dump in dump_areas if dump.get("id") != selected_dump_id]
            if not dump_areas:
                print("All dump sites are fully filled. Workflow complete.")
                break

        iteration += 1

        # Stop when all trucks are done or no dump sites remain.
        if not dump_areas:
            break

        if iteration > 100:
            print("Safety stop: maximum iteration cap reached.")
            break

    output_image_path = os.path.join(OUTPUT_FOLDER, "final_output.jpg")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    output_image_path = visualizer.save_final_output(final_image, output_image_path)
    final_result = {
        "status": "Agentic workflow completed",
        "input_image": image_path,
        "history": assignment_history,
        "final_output": output_image_path,
        "result_json": os.path.join(OUTPUT_FOLDER, "result.json"),
    }
    _save_result(final_result)
    print("Pipeline output:")
    print(json.dumps(final_result, indent=2))
    return final_result


if __name__ == "__main__":
    sample_image = os.path.join(INPUT_IMAGE_FOLDER, "sample_scene.jpg")
    run_agent_pipeline(sample_image)
