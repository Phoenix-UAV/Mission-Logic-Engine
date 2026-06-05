set -u

uav=/dev/serial/by-id/* # Location to get to the UAV
uav_name=Phoenix        # Name of the UAV

# Output ports use UDP
host=127.0.0.1  # Whatever the stream is going to be on
mp_port=14550   # MissionPlanner output port
ros_port=14551  # ROS output port
dk_port=14552   # DroneKit output port

echo "The script requires permission to automatically stop ModemManager.service and add permissions to the port connected to the UAV transmitter. Pressing CTRL+C will cancel the password input and move to the next instruction."
echo "Attempting to stop ModemManager.service..."
sudo systemctl stop ModemManager.service

echo "Attempting to change mode of ${uav} to 666..."
sudo chmod 666 ${uav}

mavproxy.py --master=${uav} --out=${host}:${mp_port} --out=${host}:${ros_port} --out=${host}:${dk_port} --aircraft=${uav_name} --nowait
