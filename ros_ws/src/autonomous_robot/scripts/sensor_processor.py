#!/usr/bin/env python3
"""
Sensor Processor Node
Subscribes to /scan (LaserScan), extracts 5 regional minimum distances,
and publishes them to /scan_features (Float32MultiArray).
"""

import math
import rospy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32MultiArray


class SensorProcessor:
    def __init__(self):
        rospy.init_node('sensor_processor', anonymous=False)

        self.safe_max = rospy.get_param('~safe_max', 3.5)

        self.features_pub = rospy.Publisher('/scan_features', Float32MultiArray, queue_size=10)
        rospy.Subscriber('/scan', LaserScan, self.scan_callback)

        rospy.loginfo("SensorProcessor initialized (safe_max=%.2f)", self.safe_max)

    def _clean_ranges(self, ranges):
        """Replace inf and nan values with safe_max."""
        cleaned = []
        for r in ranges:
            if math.isinf(r) or math.isnan(r):
                cleaned.append(self.safe_max)
            else:
                cleaned.append(r)
        return cleaned

    def _sector_min(self, ranges, indices):
        """Return the minimum value from the given index list."""
        values = [ranges[i] for i in indices if i < len(ranges)]
        return min(values) if values else self.safe_max

    def scan_callback(self, msg):
        ranges = self._clean_ranges(list(msg.ranges))
        n = len(ranges)

        if n == 0:
            return

        # Define sector indices (based on 360 readings)
        # front: [340:360] + [0:21] (~±20°)
        front_indices = list(range(340, min(360, n))) + list(range(0, min(21, n)))
        # front_left: [20:61]
        front_left_indices = list(range(20, min(61, n)))
        # front_right: [300:341]
        front_right_indices = list(range(300, min(341, n)))
        # left: [60:121]
        left_indices = list(range(60, min(121, n)))
        # right: [240:301]
        right_indices = list(range(240, min(301, n)))

        front = self._sector_min(ranges, front_indices)
        front_left = self._sector_min(ranges, front_left_indices)
        front_right = self._sector_min(ranges, front_right_indices)
        left = self._sector_min(ranges, left_indices)
        right = self._sector_min(ranges, right_indices)

        features_msg = Float32MultiArray()
        features_msg.data = [front, front_left, front_right, left, right]
        self.features_pub.publish(features_msg)

    def run(self):
        rospy.spin()


if __name__ == '__main__':
    try:
        node = SensorProcessor()
        node.run()
    except rospy.ROSInterruptException:
        pass
