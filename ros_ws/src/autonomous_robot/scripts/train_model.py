#!/usr/bin/env python3
"""
Train Model Script (standalone, NOT a ROS node)
Reads training_data.csv, trains a RandomForestClassifier, and saves the model.
"""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib


def main():
    # Paths
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(pkg_dir, 'data', 'training_data.csv')
    models_dir = os.path.join(pkg_dir, 'models')
    model_path = os.path.join(models_dir, 'obstacle_avoidance_model.joblib')

    # Check data file exists
    if not os.path.exists(data_path):
        print("ERROR: Training data file not found: {}".format(data_path))
        sys.exit(1)

    # Load data
    df = pd.read_csv(data_path)
    print("Loaded {} samples from {}".format(len(df), data_path))

    if len(df) < 50:
        print("WARNING: Only {} samples found. Model quality may be poor.".format(len(df)))

    # Features and labels
    feature_columns = ['front', 'front_left', 'front_right', 'left', 'right']
    X = df[feature_columns].values
    y = df['action'].values

    # Print class distribution
    print("\n--- Class Distribution ---")
    for action in sorted(set(y)):
        count = np.sum(y == action)
        print("  {}: {} ({:.1f}%)".format(action, count, 100.0 * count / len(y)))

    # Train/test split (80/20, stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("\nTraining samples: {}  |  Test samples: {}".format(len(X_train), len(X_test)))

    # Train model
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("\n--- Results ---")
    print("Accuracy: {:.4f}".format(accuracy))

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Feature importances
    print("\n--- Feature Importances ---")
    for name, importance in zip(feature_columns, clf.feature_importances_):
        print("  {}: {:.4f}".format(name, importance))

    # Save model
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    joblib.dump(clf, model_path)
    print("\nModel saved to: {}".format(model_path))


if __name__ == '__main__':
    main()
