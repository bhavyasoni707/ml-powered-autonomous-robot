#!/usr/bin/env python3
"""
Robot Controller Node
Subscribes to /ml_action and /scan. Publishes to /cmd_vel.
Includes an emergency safety layer that overrides ML actions when obstacles
are too close.
"""

import math
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class RobotController:
    def __init__(self):
        rospy.init_node('robot_controller', anonymous=False)

        # Parameters
        self.emergency_distance = rospy.get_param('~emergency_distance', 0.2)
        self.linear_speed = rospy.get_param('~linear_speed', 0.15)
        self.angular_speed = rospy.get_param('~angular_speed', 0.8)
        self.control_rate = rospy.get_param('~control_rate', 10)

        # State
        self.current_action = 'stop'
        self.latest_scan = None
        self.in_emergency = False

        # Publisher
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        # Subscribers
        rospy.Subscriber('/ml_action', String, self.action_callback)
        rospy.Subscriber('/scan', LaserScan, self.scan_callback)

        # Shutdown hook
        rospy.on_shutdown(self.shutdown_hook)

        rospy.loginfo("RobotController initialized (emergency_dist=%.2f, rate=%d Hz)",
                      self.emergency_distance, self.control_rate)

    def action_callback(self, msg):
        self.current_action = msg.data

    def scan_callback(self, msg):
        self.latest_scan = msg

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

    def _check_emergency(self, scan):
        """
        Safety layer: check front ±15° for obstacles closer than emergency_distance.
        Returns (is_emergency, twist_override).
        """
        ranges = list(scan.ranges)
        n = len(ranges)
        if n == 0:
            return False, None

        # Clean ranges: replace inf/nan
        cleaned = []
        for r in ranges:
            if math.isinf(r) or math.isnan(r):
                cleaned.append(10.0)  # large safe value
            else:
                cleaned.append(r)

        # Front ±15°: indices [n-15:n] + [0:16]
        front_indices = list(range(max(0, n - 15), n)) + list(range(0, min(16, n)))
        front_min = min(cleaned[i] for i in front_indices)

        if front_min < self.emergency_distance:
            # Emergency: stop forward motion, turn toward more open side
            # Compare left vs right summed ranges
            # Left side: indices roughly 0-180
            # Right side: indices roughly 180-360
            left_sum = sum(cleaned[i] for i in range(0, n // 2))
            right_sum = sum(cleaned[i] for i in range(n // 2, n))

            twist = Twist()
            twist.linear.x = 0.0
            if left_sum >= right_sum:
                twist.angular.z = self.angular_speed  # turn left (more open)
            else:
                twist.angular.z = -self.angular_speed  # turn right (more open)
            return True, twist

        return False, None

    def run(self):
        rate = rospy.Rate(self.control_rate)

        while not rospy.is_shutdown():
            if self.latest_scan is not None:
                is_emergency, emergency_twist = self._check_emergency(self.latest_scan)

                if is_emergency:
                    if not self.in_emergency:
                        rospy.logwarn("EMERGENCY STOP: Obstacle within %.2f m!", self.emergency_distance)
                        self.in_emergency = True
                    self.cmd_pub.publish(emergency_twist)
                else:
                    if self.in_emergency:
                        rospy.loginfo("Emergency cleared. Resuming ML control.")
                        self.in_emergency = False
                    twist = self._action_to_twist(self.current_action)
                    self.cmd_pub.publish(twist)

            rate.sleep()

    def shutdown_hook(self):
        """Publish zero twist on shutdown."""
        rospy.loginfo("Shutting down RobotController.")
        self.cmd_pub.publish(Twist())


if __name__ == '__main__':
    try:
        node = RobotController()
        node.run()
    except rospy.ROSInterruptException:
        pass
