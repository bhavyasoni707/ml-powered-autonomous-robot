#!/usr/bin/env python3
"""
Data Collector Node
Subscribes to /scan_features, applies a rule-based teacher policy to determine
action labels, publishes cmd_vel, and saves each sample as a CSV row.
"""

import os
import csv
import rospy
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Twist


class DataCollector:
    def __init__(self):
        rospy.init_node('data_collector', anonymous=False)

        # Parameters
        self.front_threshold = rospy.get_param('~front_threshold', 0.5)
        self.side_threshold = rospy.get_param('~side_threshold', 0.35)
        self.linear_speed = rospy.get_param('~linear_speed', 0.15)
        self.angular_speed = rospy.get_param('~angular_speed', 0.8)

        # CSV setup
        pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(pkg_dir, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.csv_path = os.path.join(data_dir, 'training_data.csv')

        # Create CSV with header if it doesn't exist
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['front', 'front_left', 'front_right', 'left', 'right', 'action'])

        self.sample_count = 0

        # Publishers and subscribers
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        rospy.Subscriber('/scan_features', Float32MultiArray, self.features_callback)

        # Ensure zero twist on shutdown
        rospy.on_shutdown(self.shutdown_hook)

        rospy.loginfo("DataCollector initialized (front_thresh=%.2f, side_thresh=%.2f)",
                      self.front_threshold, self.side_threshold)

    def _teacher_policy(self, front, front_left, front_right, left, right):
        """Rule-based teacher policy to determine action."""
        if front < self.front_threshold:
            if left > right:
                return 'left'
            else:
                return 'right'
        elif front_left < self.side_threshold:
            return 'right'
        elif front_right < self.side_threshold:
            return 'left'
        else:
            return 'forward'

    def _action_to_twist(self, action):
        """Convert action string to Twist message."""
        twist = Twist()
        if action == 'forward':
            twist.linear.x = self.linear_speed
            twist.angular.z = 0.0
        elif action == 'left':
            twist.linear.x = 0.05
            twist.angular.z = self.angular_speed
        elif action == 'right':
            twist.linear.x = 0.05
            twist.angular.z = -self.angular_speed
        else:  # stop
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        return twist

    def features_callback(self, msg):
        if len(msg.data) < 5:
            return

        front, front_left, front_right, left, right = msg.data[:5]

        # Determine action from teacher policy
        action = self._teacher_policy(front, front_left, front_right, left, right)

        # Publish cmd_vel
        twist = self._action_to_twist(action)
        self.cmd_pub.publish(twist)

        # Save to CSV
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([front, front_left, front_right, left, right, action])

        self.sample_count += 1
        if self.sample_count % 100 == 0:
            rospy.loginfo("Collected %d samples", self.sample_count)

    def shutdown_hook(self):
        """Publish zero twist on shutdown."""
        rospy.loginfo("Shutting down DataCollector. Total samples: %d", self.sample_count)
        self.cmd_pub.publish(Twist())

    def run(self):
        rospy.spin()


if __name__ == '__main__':
    try:
        node = DataCollector()
        node.run()
    except rospy.ROSInterruptException:
        pass
