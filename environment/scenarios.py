"""
environment/scenarios.py
Pre-defined test scenarios for the Smart Delivery Route Optimizer.
Each scenario defines grid parameters for systematic evaluation
across varying difficulty levels (Easy → Full Hard).
"""

from typing import Dict, Any

# 10 test scenarios covering easy to very hard configurations
SCENARIOS: Dict[str, Dict[str, Any]] = {
    "Scenario 1: Easy (10x10)": {
        "size": 10,
        "num_deliveries": 2,
        "obstacle_density": 0.10,
        "traffic_density": 0.02,
        "seed": 42,
        "description": "10x10 grid, 2 deliveries, 10% obstacles — Easy",
    },
    "Scenario 2: Easy-Med (15x15)": {
        "size": 15,
        "num_deliveries": 3,
        "obstacle_density": 0.15,
        "traffic_density": 0.03,
        "seed": 123,
        "description": "15x15 grid, 3 deliveries, 15% obstacles — Easy-Medium",
    },
    "Scenario 3: Medium (15x15)": {
        "size": 15,
        "num_deliveries": 4,
        "obstacle_density": 0.20,
        "traffic_density": 0.03,
        "seed": 256,
        "description": "15x15 grid, 4 deliveries, 20% obstacles — Medium",
    },
    "Scenario 4: Medium (20x20)": {
        "size": 20,
        "num_deliveries": 5,
        "obstacle_density": 0.20,
        "traffic_density": 0.04,
        "seed": 456,
        "description": "20x20 grid, 5 deliveries, 20% obstacles — Medium",
    },
    "Scenario 5: Med-Hard (20x20)": {
        "size": 20,
        "num_deliveries": 6,
        "obstacle_density": 0.25,
        "traffic_density": 0.05,
        "seed": 789,
        "description": "20x20 grid, 6 deliveries, 25% obstacles — Medium-Hard",
    },
    "Scenario 6: Heavy Traffic (20x20)": {
        "size": 20,
        "num_deliveries": 4,
        "obstacle_density": 0.15,
        "traffic_density": 0.30,
        "seed": 1001,
        "description": "20x20 grid, 4 deliveries, 30% traffic — Heavy Traffic",
    },
    "Scenario 7: Many Stops (20x20)": {
        "size": 20,
        "num_deliveries": 8,
        "obstacle_density": 0.20,
        "traffic_density": 0.04,
        "seed": 1337,
        "description": "20x20 grid, 8 deliveries, 20% obstacles — Many Stops",
    },
    "Scenario 8: Large Grid (25x25)": {
        "size": 25,
        "num_deliveries": 6,
        "obstacle_density": 0.25,
        "traffic_density": 0.04,
        "seed": 2048,
        "description": "25x25 grid, 6 deliveries, 25% obstacles — Large Grid",
    },
    "Scenario 9: Dense Map (20x20)": {
        "size": 20,
        "num_deliveries": 5,
        "obstacle_density": 0.35,
        "traffic_density": 0.03,
        "seed": 3141,
        "description": "20x20 grid, 5 deliveries, 35% obstacles — Dense Map",
    },
    "Scenario 10: Full Hard (25x25)": {
        "size": 25,
        "num_deliveries": 10,
        "obstacle_density": 0.20,
        "traffic_density": 0.05,
        "seed": 4096,
        "description": "25x25 grid, 10 deliveries, 20% obstacles — Full Hard",
    },
}