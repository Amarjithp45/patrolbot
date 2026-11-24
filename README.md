# PatrolBot: Autonomous Mobile Robot Navigation & Patrol Stack (ROS 2 Humble + Nav2)

An end-to-end autonomous mobile robot (AMR) system featuring 2D SLAM mapping, Nav2 autonomous navigation, AMCL localization, costmap safety tuning, and a custom multi-waypoint patrol mission controller.

Designed to demonstrate core mobile robotics competencies: coordinate transform trees (TF2), sensor fusion, costmap inflation tuning, path planning, and behavior execution.

---

## System Architecture

```
+------------------------------------------------------------------------+
|                          PatrolBot Architecture                        |
|                                                                        |
|  [ Mission Controller (patrol_node.py) ]                               |
|        │ Uses Nav2 Simple Commander API                                |
|        │ Waypoint sequencing, telemetry monitoring, recovery handling  |
|        ▼                                                               |
|  [ Nav2 Navigation Stack ]                                             |
|        ├── Behavior Tree Navigator (NavigateToPose)                    |
|        ├── Global Planner (NavFn / Dijkstra / A*)                      |
|        ├── Local Controller (DWB Local Planner / Trajectory Rollout)   |
|        ├── Costmaps (Global & Local Inflation + Obstacle Layers)       |
|        └── Localization (AMCL Particle Filter)                         |
|        ▲                                                               |
|        │ /scan (2D LiDAR), /odom (Wheel Odometry), /tf Transform Tree  |
|  [ Gazebo Physics Simulation (TurtleBot3 Waffle) ]                     |
+------------------------------------------------------------------------+
```

---

## Features

- **Realistic Simulation**: TurtleBot3 Waffle differential-drive platform simulated in Gazebo with 360° 2D LiDAR, wheel encoders, and IMU.
- **2D SLAM Mapping**: Real-time occupancy grid mapping using Cartographer / SLAM Toolbox with loop closure.
- **Autonomous Navigation (Nav2)**:
  - Adaptive Monte Carlo Localization (AMCL) against static occupancy maps.
  - Global path planning avoiding static and dynamic obstacles.
  - Local trajectory generation with collision-checking costmap buffers.
- **Patrol Mission Controller**:
  - Multi-waypoint autonomous patrol sequence across discrete security sectors.
  - Real-time telemetry streaming (distance to target, mission duration).
  - Sensor sweep inspection pauses at designated checkpoints.
  - Safe exception handling and auto-return to home docking station.

---

## Prerequisites & Installation

### Environment
- **OS**: Ubuntu 22.04 LTS (Native or Windows 11 via WSL2 with WSLg)
- **ROS Distribution**: ROS 2 Humble Hawksbill

### Setup
Run the automated bootstrap script:
```bash
bash setup_ros2_humble.sh
source ~/.bashrc
```

---

## Quickstart Guide

### 1. Launch Gazebo Simulation
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### 2. (Optional) Run SLAM & Map the Environment
```bash
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True
ros2 run turtlebot3_teleop teleop_keyboard
# Once mapped, save with:
ros2 run nav2_map_server map_saver_cli -f my_map
```

### 3. Launch Nav2 Autonomous Navigation
```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=$(pwd)/my_map.yaml
```
*In RViz, use **2D Pose Estimate** to set initial robot pose.*

### 4. Run the Autonomous Patrol Mission
```bash
python3 patrol_node.py
```

---

## Technical Learnings & Engineering Decisions

- **Costmap Inflation Tuning**: Balances robot safety margins against corridor traversability. Overly conservative inflation radii cause planners to declare narrow passages impassable; balanced decay parameters allow smooth clearance through tight obstacle fields.
- **Waypoint Tolerance Optimization**: For patrol and exploration tasks, decoupling strict terminal heading (yaw) alignment from spatial $(X, Y)$ goal tolerance drastically reduces unnecessary in-place rotations, wheel slip, and controller timeouts.
- **Mission Resilience**: The mission controller intercepts `TaskResult.FAILED` and `TaskResult.CANCELED` states, triggering local recovery and continuing surveillance rounds rather than halting the system.

---

## License
MIT License.
