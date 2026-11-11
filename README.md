# ML-Powered Autonomous Robot

An ML-powered autonomous mobile robot developed using ROS1 Noetic,
Gazebo Classic, Python and Machine Learning.

## Project Objective

Build and simulate an autonomous mobile robot that uses LiDAR sensor
readings and a Machine Learning model to make navigation decisions.

The initial objective is obstacle avoidance using a supervised
classification model.

The model will predict actions such as:
- forward
- left
- right
- stop

A ROS controller will convert predictions into velocity commands
using geometry_msgs/Twist.

A separate safety layer will prevent movement when an obstacle is
too close, regardless of the ML prediction.

## Technology Stack

- Ubuntu Linux (version not yet recorded)
- ROS1 Noetic
- Gazebo Classic 11.15.1
- TurtleBot3 Burger
- Python
- scikit-learn
- PyTorch (for future extensions)
- Git and GitHub

ROS2 is NOT part of this project. Continue with ROS1 Noetic.

## Simulation Environment

No physical robot is available. Development is being done using
TurtleBot3 Burger in Gazebo Classic.

Installed ROS packages include:
- turtlebot3
- turtlebot3-simulations
- gazebo_ros
- robot_state_publisher

Gazebo world launch command:

roslaunch turtlebot3_gazebo turtlebot3_world.launch

Environment variable:

TURTLEBOT3_MODEL=burger

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
            │   └── .gitkeep
            └── models/
                └── .gitkeep
```

The ROS package was created with:

```bash
catkin_create_pkg autonomous_robot rospy std_msgs sensor_msgs geometry_msgs
```

## Completed Work

1. Created GitHub repository.
2. Configured Git username and email.
3. Initialized the local Git repository and pushed the initial commit.
4. Created the ROS Catkin workspace at ros_ws/.
5. Built the Catkin workspace successfully using catkin_make.
6. Created the autonomous_robot ROS package.
7. Verified the package using `rospack find autonomous_robot`.
8. Installed TurtleBot3 and its simulation packages.
9. Successfully launched TurtleBot3 Burger in Gazebo Classic.
10. Inspected ROS topics and confirmed `/scan`, `/cmd_vel`, `/odom`, `/tf`.
11. Confirmed `/scan` publishes `sensor_msgs/LaserScan`.
12. Inspected LiDAR readings (360 readings, 0.12 - 3.5 m range, frame_id `base_scan`).
13. Confirmed LiDAR frame_id is `base_scan`.
14. Confirmed `/robot_description` parameter exists.
15. Confirmed `robot_state_publisher` is installed.
16. **Resolved TF Frame issue**: Created `autonomous_robot.launch` combining Gazebo simulation with `robot_state_publisher` to publish `/tf_static` transforms. Verified `base_link` -> `base_scan` transform via `tf_echo`.
17. Created configuration parameter file `config/robot_params.yaml`.
18. Implemented `sensor_processor.py` to extract 5-sector minimum distances (`front`, `front_left`, `front_right`, `left`, `right`) and publish to `/scan_features`.
19. Implemented `data_collector.py` with rule-based teacher policy to drive the robot and log labeled CSV dataset to `data/training_data.csv`.
20. Implemented `train_model.py` standalone script to train a `RandomForestClassifier` on collected data, evaluate accuracy and confusion matrix, and save to `models/obstacle_avoidance_model.joblib`.
21. Implemented `ml_predictor.py` to load trained model and publish real-time action predictions to `/ml_action`.
22. Implemented `robot_controller.py` with an independent emergency stop safety layer that overrides ML commands when obstacles are closer than `emergency_distance` (0.2 m).
23. Created `data_collection.launch` and `ml_obstacle_avoidance.launch`.
24. Configured `CMakeLists.txt` with `catkin_install_python` and verified workspace build.

## TF Frame Issue: Resolved

The `base_scan` frame is defined in the TurtleBot3 URDF as a fixed joint child of `base_link`.
The standard `turtlebot3_world.launch` did not start `robot_state_publisher`, so only `odom -> base_footprint` was broadcast.

**Resolution:**
The project master launch file `autonomous_robot.launch` includes both `turtlebot3_world.launch` and launches `robot_state_publisher` at 50 Hz. This publishes all static transforms from `/robot_description` to `/tf_static`, establishing the full transform chain:
`odom -> base_footprint -> base_link -> base_scan`

Verified with:
```bash
rosrun tf tf_echo base_link base_scan
```
Result: Translation `[-0.032, 0.000, 0.172]`, Rotation `[0.000, 0.000, 0.000, 1.000]`.

## How to Run the System

### 1. Build and Source the Workspace

```bash
cd ~/ml-powered-autonomous-robot/ros_ws
source /opt/ros/noetic/setup.bash
catkin_make
source devel/setup.bash
```

### 2. Launch Simulation (Gazebo + TF Publisher)

In Terminal 1:
```bash
export TURTLEBOT3_MODEL=burger
source ~/ml-powered-autonomous-robot/ros_ws/devel/setup.bash
roslaunch autonomous_robot autonomous_robot.launch
```

### 3. Step A: Collect Training Data (Teacher Policy)

In Terminal 2:
```bash
source ~/ml-powered-autonomous-robot/ros_ws/devel/setup.bash
roslaunch autonomous_robot data_collection.launch
```
Let the robot explore the environment and accumulate samples (logged every 100 samples). Stop with `Ctrl+C` when sufficient data (e.g., 500-1500 samples) has been collected. Data is saved in:
`ros_ws/src/autonomous_robot/data/training_data.csv`

### 4. Step B: Train the Machine Learning Model

In Terminal 2 (after stopping data collection):
```bash
python3 ~/ml-powered-autonomous-robot/ros_ws/src/autonomous_robot/scripts/train_model.py
```
This script will:
- Display sample count and class distribution
- Split data 80/20 train/test (stratified)
- Train a `RandomForestClassifier` (100 trees)
- Print test set accuracy, classification report, and confusion matrix
- Print feature importances
- Save the trained model to `ros_ws/src/autonomous_robot/models/obstacle_avoidance_model.joblib`

### 5. Step C: Run Autonomous ML Obstacle Avoidance

In Terminal 2:
```bash
source ~/ml-powered-autonomous-robot/ros_ws/devel/setup.bash
roslaunch autonomous_robot ml_obstacle_avoidance.launch
```
The robot will now navigate autonomously using real-time predictions from the trained model, guarded by the independent safety layer.

## Planned Architecture

LiDAR (/scan)
    |
    v
Sensor Processing Node
    |
    v
ML Prediction Node
    |
    v
Safety Layer
    |
    v
Robot Controller
    |
    v
/cmd_vel
    |
    v
TurtleBot3 in Gazebo

## Important Development Instructions

- Continue using ROS1 Noetic.
- Do not migrate to ROS2.
- Do not change the operating system.
- The user does not have a physical robot; use Gazebo simulation.
- Teach and implement the project incrementally.
- Explain important ROS commands and code.
- Do not assume a step is complete without verifying it.
- Keep the repository organized and commit meaningful milestones.
- Do not overwrite existing workspace configuration without inspecting it.
- Add an emergency obstacle-stop safety condition independent of ML predictions.

## GitHub

Repository:
https://github.com/bhavyasoni707/ml-powered-autonomous-robot
