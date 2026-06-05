
uav=/dev/serial/by-id/* # Location to get to the UAV
uav_name=Phoenix        # Name of the UAV

host=127.0.0.1          # Whatever the stream is going to be on
mp_tcp=14550            # MissionPlanner TCP output port
ros_tcp=14551           # ROS TCP output port
dk_tcp=14552            # DroneKit TCP output port

sudo systemctl stop ModemManager.service
sudo chmod 666 $uav

mavproxy.py --master=$uav --out=$host:$mp_tcp --out=$host:$ros_tcp --out=$host:$dk_tcp --aircraft=$uav_name --nowait
