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

ml-powered-autonomous-robot/
├── README.md
├── .gitignore
└── ros_ws/
    └── src/
        └── autonomous_robot/
            ├── package.xml
            └── CMakeLists.txt

The ROS package was created with:

catkin_create_pkg autonomous_robot rospy std_msgs sensor_msgs geometry_msgs

## Completed Work

1. Created GitHub repository.
2. Configured Git username and email.
3. Initialized the local Git repository and pushed the initial commit.
4. Created the ROS Catkin workspace at ros_ws/.
5. Built the Catkin workspace successfully using catkin_make.
6. Created the autonomous_robot ROS package.
7. Verified the package using rospack find autonomous_robot.
8. Installed TurtleBot3 and its simulation packages.
9. Successfully launched TurtleBot3 Burger in Gazebo Classic.
10. Inspected ROS topics and confirmed:
    - /scan
    - /cmd_vel
    - /odom
    - /tf
11. Confirmed /scan publishes sensor_msgs/LaserScan.
12. Inspected LiDAR readings:
    - approximately 360 readings
    - angle_min approximately 0 radians
    - angle_max approximately 2*pi radians
    - angle_increment approximately 0.0175 radians
    - range_min 0.12 m
    - range_max 3.5 m
    - infinity values occur when no valid obstacle return is detected.
13. Confirmed LiDAR frame_id is base_scan.
14. Confirmed /robot_description parameter exists.
15. Confirmed robot_state_publisher is installed.

## Current Issue: TF Frames

The expected sensor transform is not currently available.

Observed:
- /tf publishes odom -> base_footprint.
- base_scan was not found by tf_echo.
- /tf_static was not present in the observed topic list.
- rosnode list showed /gazebo, /gazebo_gui and /rosout.
- robot_state_publisher was not running.
- /robot_description exists.

The TurtleBot3 launch file was inspected:

/opt/ros/noetic/share/turtlebot3_gazebo/launch/turtlebot3_world.launch

It:
1. Starts Gazebo.
2. Loads the TurtleBot3 URDF into /robot_description.
3. Spawns the robot using gazebo_ros/spawn_model.

It does NOT start robot_state_publisher.

The robot_state_publisher package exists at:

/opt/ros/noetic/share/robot_state_publisher

Do not modify files inside /opt/ros/noetic/.
Prefer adding the required configuration to this project's own launch files.

## Immediate Next Tasks

1. Diagnose the missing TF transforms.
2. Add robot_state_publisher to the project's launch configuration correctly.
3. Verify that base_scan becomes available through TF.
4. Create the project launch directory and launch file.
5. Create sensor_processor.py to subscribe to /scan.
6. Extract useful LiDAR features such as front, left and right obstacle distances.
7. Collect labeled training data using a rule-based teacher policy.
8. Train a RandomForestClassifier.
9. Evaluate the model using a test set and confusion matrix.
10. Create ml_predictor.py to load the trained model and predict actions.
11. Create robot_controller.py to publish velocity commands to /cmd_vel.
12. Test obstacle avoidance in Gazebo.

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
