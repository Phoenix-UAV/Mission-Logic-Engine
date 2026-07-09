#!/bin/bash
# Script to start all GCS components

echo "Starting Drone GCS on Linux..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"


source venv/bin/activate

# Source ROS2 (if native install)
source /opt/ros/humble/setup.bash

# Start MAVProxy in background
echo "Starting MAVProxy..."
mavproxy.py --master=/dev/ttyUSB0:57600 \
  --out=127.0.0.1:14550 \
  --out=127.0.0.1:14551 \
  --out=127.0.0.1:14552 &
MAVPROXY_PID=$!

# Wait for MAVProxy to start
sleep 2

# Start ROS2 nodes
echo "Starting ROS2 nodes..."
if command -v ros2 &> /dev/null; then
    ros2 launch custom_gcs gcs.launch.py &
    ROS2_PID=$!
else
    echo "ROS2 not found. Starting in Docker instead..."
    docker run -it --rm --network=host Mission-Logic-Engine-ros2:latest ros2 launch custom_gcs gcs.launch.py &
    ROS2_PID=$!
fi

echo "All components started."
echo "MAVProxy PID: $MAVPROXY_PID"
echo "ROS2 PID: $ROS2_PID"
echo ""
echo "Press Ctrl+C to stop all components."

# Wait for both processes
wait $MAVPROXY_PID $ROS2_PID