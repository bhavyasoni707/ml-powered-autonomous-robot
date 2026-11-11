#!/usr/bin/env python3
"""
ML Predictor Node
Loads a trained model and predicts obstacle avoidance actions from scan features.
Publishes predicted action to /ml_action (String).
"""

import os
import rospy
import numpy as np
import joblib
from std_msgs.msg import Float32MultiArray, String


class MLPredictor:
    def __init__(self):
        rospy.init_node('ml_predictor', anonymous=False)

        # Model path (configurable via private param)
        pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_model_path = os.path.join(pkg_dir, 'models', 'obstacle_avoidance_model.joblib')
        model_path = rospy.get_param('~model_path', default_model_path)

        # Load model
        if not os.path.exists(model_path):
            rospy.logfatal("Model file not found: %s", model_path)
            rospy.signal_shutdown("Model file not found")
            return

        self.model = joblib.load(model_path)
        rospy.loginfo("Loaded model from: %s", model_path)

        # Publisher and subscriber
        self.action_pub = rospy.Publisher('/ml_action', String, queue_size=10)
        rospy.Subscriber('/scan_features', Float32MultiArray, self.features_callback)

        rospy.loginfo("MLPredictor initialized and ready")

    def features_callback(self, msg):
        if len(msg.data) < 5:
            return

        features = np.array(msg.data[:5]).reshape(1, -1)
        prediction = self.model.predict(features)[0]

        action_msg = String()
        action_msg.data = str(prediction)
        self.action_pub.publish(action_msg)

    def run(self):
        rospy.spin()


if __name__ == '__main__':
    try:
        node = MLPredictor()
        node.run()
    except rospy.ROSInterruptException:
        pass
