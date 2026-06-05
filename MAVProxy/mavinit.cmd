REM UAV variables
SET uav=COMx
SET uav_name=Phoenix

REM MAVLink stream host (default=127.0.0.1)
SET host=127.0.0.1

REM Output ports
SET mp_port=14550
SET ros_port=14551
SET dk_port=14552


REM Internal

mavproxy --master=%uav% --out=%host%:%mp_port% --out=%host%:%ros_port% --out=%host%:%dk_port% --aircraft=%uav_name% --nowait
