from scripts.discover_ros2_topics import classify_topic, classify_topics


def test_classify_odom_topics() -> None:
    assert classify_topic("/odom") == "odom"
    assert classify_topic("/robot/odometry") == "odom"


def test_classify_imu_topic() -> None:
    assert classify_topic("/imu/data") == "imu"


def test_classify_low_state_topic() -> None:
    assert classify_topic("/low_state") == "low_state"


def test_classify_robot_state_topic() -> None:
    assert classify_topic("/robot_state") == "robot_state"


def test_classify_battery_topic() -> None:
    assert classify_topic("/battery_state") == "battery"


def test_classify_cmd_vel_as_command() -> None:
    # Command keywords are intentionally matched before velocity keywords.
    assert classify_topic("/cmd_vel") == "command"


def test_classify_loco_topic() -> None:
    assert classify_topic("/walk/loco") == "loco"


def test_classify_unknown_topic() -> None:
    assert classify_topic("/camera/image_raw") == "unknown"


def test_classify_topics_groups_results() -> None:
    grouped = classify_topics(["/odom", "/imu/data", "/cmd_vel", "/camera/image_raw"])

    assert grouped["odom"] == ["/odom"]
    assert grouped["imu"] == ["/imu/data"]
    assert grouped["command"] == ["/cmd_vel"]
    assert grouped["unknown"] == ["/camera/image_raw"]
