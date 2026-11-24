#!/usr/bin/env python3
"""
Robust Autonomous Patrol Bot Mission Controller
Features:
- Natural heading angles aligned with the direction of travel
- Open corridor navigation
- Fallback & graceful recovery logic
- Real-time mission telemetry streaming
"""

import time
import math
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy
from rclpy.duration import Duration


def create_pose(navigator: BasicNavigator, x: float, y: float, yaw_deg: float) -> PoseStamped:
    """Helper function to create a PoseStamped message."""
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = 0.0

    yaw_rad = math.radians(yaw_deg)
    pose.pose.orientation.z = math.sin(yaw_rad / 2.0)
    pose.pose.orientation.w = math.cos(yaw_rad / 2.0)
    return pose


def main():
    rclpy.init()
    navigator = BasicNavigator()

    print("\n=======================================================")
    print("      Robust Autonomous Patrol Bot - Mission Start     ")
    print("=======================================================")

    print("[INFO] Checking Nav2 lifecycle status...")
    navigator.waitUntilNav2Active()
    print("[INFO] Nav2 active! Planners, costmaps & controllers online.")

    # Waypoints with natural forward headings aligned to the travel direction
    # This prevents in-place wheel spin and controller timeout at goal arrival
    patrol_checkpoints = [
        {"name": "Sector 1 (North-East Corridor)", "x": 0.8, "y": 0.8, "yaw": 90.0},
        {"name": "Sector 2 (North-West Corridor)", "x": -0.8, "y": 0.8, "yaw": 180.0},
        {"name": "Sector 3 (South-West Corridor)", "x": -0.8, "y": -0.8, "yaw": 270.0},
        {"name": "Sector 4 (South-East Corridor)", "x": 0.8, "y": -0.8, "yaw": 0.0},
    ]

    home_base = {"name": "Charging Base Station", "x": 0.0, "y": -1.2, "yaw": 90.0}

    successful_visits = 0

    print(f"\n[INFO] Commencing patrol across {len(patrol_checkpoints)} sectors...\n")

    for idx, cp in enumerate(patrol_checkpoints, 1):
        print(f"-------------------------------------------------------")
        print(f"[MISSION] Checkpoint {idx}/{len(patrol_checkpoints)}: {cp['name']}")
        print(f"          Target: x={cp['x']}, y={cp['y']}, heading={cp['yaw']}°")
        
        goal_pose = create_pose(navigator, cp["x"], cp["y"], cp["yaw"])
        navigator.goToPose(goal_pose)

        while not navigator.isTaskComplete():
            feedback = navigator.getFeedback()
            if feedback:
                dist = feedback.distance_remaining
                nav_time = Duration.from_msg(feedback.navigation_time).nanoseconds / 1e9
                print(f"  -> Driving: {dist:.2f}m to goal | Time: {nav_time:.1f}s   ", end="\r")
            time.sleep(0.3)

        result = navigator.getResult()

        if result == TaskResult.SUCCEEDED:
            successful_visits += 1
            print(f"\n[SUCCESS] Reached {cp['name']}!")
            print(f"          Conducting 2-second security sensor sweep...")
            time.sleep(2.0)
        elif result == TaskResult.CANCELED:
            print(f"\n[WARNING] Mission canceled by operator.")
            break
        elif result == TaskResult.FAILED:
            print(f"\n[NOTICE] Checkpoint {cp['name']} approach obstructed.")
            print(f"         Recovering gracefully and routing to next checkpoint...")
            time.sleep(1.0)

    # Return to Dock
    print("\n-------------------------------------------------------")
    print(f"[MISSION COMPLETE] Patrol finished! ({successful_visits}/{len(patrol_checkpoints)} sectors secured)")
    print(f"[MISSION] Returning to {home_base['name']}...")

    home_pose = create_pose(navigator, home_base["x"], home_base["y"], home_base["yaw"])
    navigator.goToPose(home_pose)

    while not navigator.isTaskComplete():
        feedback = navigator.getFeedback()
        if feedback:
            print(f"  -> Returning: {feedback.distance_remaining:.2f}m to dock   ", end="\r")
        time.sleep(0.3)

    if navigator.getResult() == TaskResult.SUCCEEDED:
        print("\n[SUCCESS] Robot successfully docked at Home Base Station!")
    else:
        print("\n[NOTICE] Docking approach obstructed, stopped safely.")

    print("=======================================================\n")
    rclpy.shutdown()


if __name__ == '__main__':
    main()
