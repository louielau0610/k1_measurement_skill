# Booster K1 Platform Scaffold

Booster K1 is the hardware-validated reference platform for M20 because it wraps the completed M19C ROS2 odometer measurement path.

- Primary state source: `/odometer_state`
- Secondary yaw source: `/low_state.imu_state.rpy`
- Required robot-side setup: `source /opt/booster/BoosterRos2Interface/install/setup.bash`
- Validated command path: `kPrepare -> kWalking -> Move(vx, 0, 0)`
- Gold profile: `outputs/real_k1_validation_m19/k1_gold_profile_v1.json`

This scaffold does not execute robot motion by default. Use the existing M19C robot-side runner for live K1 trials.
