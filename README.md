# ML-Powered Autonomous Robot

An ML-powered autonomous mobile robot developed using ROS1 Noetic,
Gazebo Classic, Python, and Machine Learning.

## Project Objective

Build and simulate an autonomous mobile robot that uses LiDAR sensor
readings and a Machine Learning model to make navigation decisions.

The model predicts one of four actions:
- **forward** — move straight ahead
- **left** — turn left
- **right** — turn right
- **stop** — halt movement

A ROS controller converts predictions into velocity commands using
`geometry_msgs/Twist`. An independent safety layer prevents any forward
movement when an obstacle is closer than `emergency_distance` (0.2 m),
regardless of the ML prediction.

## Technology Stack

- Ubuntu 20.04 LTS
- ROS1 Noetic
- Gazebo Classic 11.15.1
- TurtleBot3 Burger (simulated)
- Python 3.8
- scikit-learn (RandomForestClassifier)
- joblib, pandas, numpy
- Git and GitHub

> ROS2 is NOT part of this project. Continue with ROS1 Noetic.

## Simulation Environment

No physical robot is used. Development is done with TurtleBot3 Burger
in Gazebo Classic.

Installed ROS packages:
- `turtlebot3`
- `turtlebot3-simulations`
- `gazebo_ros`
- `robot_state_publisher`

Required environment variable:
```bash
export TURTLEBOT3_MODEL=burger
```

## Repository Structure

```
ml-powered-autonomous-robot/
├── README.md
├── .gitignore
└── ros_ws/
    └── src/
        └── autonomous_robot/
            ├── package.xml
            ├── CMakeLists.txt
            ├── config/
            │   └── robot_params.yaml
            ├── launch/
            │   ├── autonomous_robot.launch
            │   ├── data_collection.launch
            │   └── ml_obstacle_avoidance.launch
            ├── scripts/
            │   ├── sensor_processor.py
            │   ├── data_collector.py
            │   ├── train_model.py
            │   ├── ml_predictor.py
            │   └── robot_controller.py
            ├── data/
            │   └── training_data.csv
            └── models/
                └── obstacle_avoidance_model.joblib
```

## System Architecture

```
LiDAR (/scan)
    |
    v
sensor_processor.py     → /scan_features (5 sector min distances)
    |
    v
ml_predictor.py         → /ml_action (forward / left / right / stop)
    |
    v
robot_controller.py     → /cmd_vel  [+ emergency safety layer reads /scan directly]
    |
    v
TurtleBot3 in Gazebo
```

### Node Descriptions

| Node | Script | Subscribes | Publishes |
|---|---|---|---|
| `sensor_processor` | `sensor_processor.py` | `/scan` | `/scan_features` |
| `data_collector` | `data_collector.py` | `/scan_features` | `/cmd_vel` |
| `ml_predictor` | `ml_predictor.py` | `/scan_features` | `/ml_action` |
| `robot_controller` | `robot_controller.py` | `/ml_action`, `/scan` | `/cmd_vel` |

## Prerequisites

### 1. ROS1 Noetic
```bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu focal main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
sudo apt update
sudo apt install -y ros-noetic-desktop-full
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 2. TurtleBot3 & Gazebo packages
```bash
sudo apt install -y ros-noetic-turtlebot3 ros-noetic-turtlebot3-simulations
```

### 3. Python ML libraries
```bash
pip3 install scikit-learn joblib pandas numpy
```

## How to Run

### Step 1 — Build the Workspace (one-time)
```bash
cd ~/ml-powered-autonomous-robot/ros_ws
source /opt/ros/noetic/setup.bash
catkin_make
source devel/setup.bash
```

### Step 2 — Launch Simulation (Terminal 1)
```bash
export TURTLEBOT3_MODEL=burger
source ~/ml-powered-autonomous-robot/ros_ws/devel/setup.bash
roslaunch autonomous_robot autonomous_robot.launch
```
Gazebo opens with TurtleBot3 in the world. Leave this running.

### Step 3 — Collect Training Data (Terminal 2)
```bash
source ~/ml-powered-autonomous-robot/ros_ws/devel/setup.bash
roslaunch autonomous_robot data_collection.launch
```
The rule-based teacher policy drives the robot automatically and logs
labeled data to `data/training_data.csv`. Progress is printed every
100 samples. Stop with `Ctrl+C` after 500–1500 samples.

To monitor sample count live:
```bash
watch -n 2 wc -l ~/ml-powered-autonomous-robot/ros_ws/src/autonomous_robot/data/training_data.csv
```

### Step 4 — Train the ML Model (Terminal 2)
```bash
python3 ~/ml-powered-autonomous-robot/ros_ws/src/autonomous_robot/scripts/train_model.py
```
Outputs accuracy, classification report, confusion matrix, and feature
importances. Saves model to `models/obstacle_avoidance_model.joblib`.

> **You only need to train once.** The model is reloaded automatically
> every time `ml_obstacle_avoidance.launch` is started.

### Step 5 — Run Autonomous ML Navigation (Terminal 2)
```bash
source ~/ml-powered-autonomous-robot/ros_ws/devel/setup.bash
roslaunch autonomous_robot ml_obstacle_avoidance.launch
```
The robot navigates autonomously using real-time ML predictions,
protected by the independent emergency stop safety layer.

## Configuration

All tunable parameters are in [`config/robot_params.yaml`](ros_ws/src/autonomous_robot/config/robot_params.yaml):

```yaml
# Sensor processing
safe_max: 3.5          # Distance (m) used for inf/nan LiDAR readings

# Teacher policy (data collection)
front_threshold: 0.5   # (m) Obstacle in front triggers turn
side_threshold: 0.35   # (m) Obstacle on side triggers correction
linear_speed: 0.15     # (m/s) Forward speed
angular_speed: 0.8     # (rad/s) Turning speed

# Safety layer
emergency_distance: 0.2  # (m) Hard stop threshold
control_rate: 10          # (Hz) Controller loop rate
```

## Completed Milestones

1. Created GitHub repository and configured Git.
2. Initialized local Git repository and pushed initial commit.
3. Created ROS Catkin workspace at `ros_ws/`.
4. Built the Catkin workspace with `catkin_make`.
5. Created the `autonomous_robot` ROS package.
6. Installed TurtleBot3 and simulation packages.
7. Successfully launched TurtleBot3 Burger in Gazebo Classic.
8. Confirmed ROS topics: `/scan`, `/cmd_vel`, `/odom`, `/tf`.
9. Confirmed `/scan` publishes `sensor_msgs/LaserScan` (360 readings, 0.12–3.5 m).
10. Confirmed LiDAR frame_id is `base_scan`.
11. **Resolved TF Frame issue**: `autonomous_robot.launch` now includes `robot_state_publisher` to publish `/tf_static`, establishing `odom → base_footprint → base_link → base_scan`.
12. Created `config/robot_params.yaml` for all tunable parameters.
13. Implemented `sensor_processor.py` — 5-sector LiDAR feature extraction.
14. Implemented `data_collector.py` — rule-based teacher policy, CSV logging.
15. Implemented `train_model.py` — RandomForestClassifier training and evaluation.
16. Implemented `ml_predictor.py` — real-time model inference on `/scan_features`.
17. Implemented `robot_controller.py` — ML action execution with emergency safety layer.
18. Created all three launch files.
19. Configured `CMakeLists.txt` with `catkin_install_python`.
20. **Collected 1192 training samples** using the teacher policy in Gazebo.
21. **Trained and saved** `RandomForestClassifier` model (`obstacle_avoidance_model.joblib`).
22. **Verified full autonomous ML pipeline** running end-to-end in simulation.

## TF Frame Issue — Resolved

The `base_scan` frame is defined in the TurtleBot3 URDF as a fixed joint
child of `base_link`. The standard `turtlebot3_world.launch` did not start
`robot_state_publisher`, so only `odom → base_footprint` was broadcast.

**Resolution:** `autonomous_robot.launch` includes both `turtlebot3_world.launch`
and launches `robot_state_publisher` at 50 Hz, publishing all static transforms
from `/robot_description` to `/tf_static`, establishing the full chain:
`odom → base_footprint → base_link → base_scan`

Verified with:
```bash
rosrun tf tf_echo base_link base_scan
```
Result: Translation `[-0.032, 0.000, 0.172]`, Rotation `[0.000, 0.000, 0.000, 1.000]`.

## Important Development Notes

- Continue using **ROS1 Noetic** — do not migrate to ROS2.
- No physical robot — use Gazebo simulation only.
- Do not change the operating system.
- Only retrain the model if new training data is collected.
- The safety layer in `robot_controller.py` is independent of ML — it always overrides if an obstacle is within `emergency_distance`.
- Keep commits meaningful and milestone-based.

## GitHub

Repository: https://github.com/bhavyasoni707/ml-powered-autonomous-robot
