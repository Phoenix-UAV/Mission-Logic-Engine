# Linux/Ubuntu Setup Guide
**Platform**: Debian-based / Arch-based Linux OS
**Setup Time**: 30-45 minutes  
**Difficulty**: Low  
**Docker**: Optional


## Prerequisites
Before starting, ensure you have:

- Sudo access (administrator rights)
- 10 GB free disk space
- 8 GB RAM (16 GB recommended)
- Stable internet connection
- USB port for LoRa module (for testing)


## Step 1: Update System
```bash
# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install git (if not already installed)
sudo apt install -y git curl wget
```


## Step 2: Install Python and Pip
### Debian-based Systems
Check if you have `python3` installed:
```bash
which python3
```

If no file path is outputted, then install Python 3:
```bash
sudo apt install -y python3-pip python3-dev python3-venv
```

Ensure Python is version 3.14 or newer:
```bash
python3 --version
```

### Arch-based Systems
Run `sudo pacman -S --needed python`.


## Step 3: Fork and clone Repository
1. **Fork the repository**:
   ```bash
   # Go to https://github.com/YOUR-USERNAME/Mission-Logic-Engine.git
   # Click "Fork" button
   ```

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Mission-Logic-Engine.git
   cd Mission-Logic-Engine
   ```


## Step 4: Create Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

You should see `(venv)` at the start of the command prompt, like so: `(venv) user~$`.


## Step 5: Install Python Dependencies
```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install all dependencies
pip install -r requirements.txt
```

If there are any issues installing the packages in `requirements.txt`, please post the issue in our
[GitHub repository](https://github.com/Phoenix-UAV/Mission-Logic-Engine/issues).

## Step 6: Install ROS2 Humble
### Option A: Native ROS2 (Recommended)
ROS2 Humble is officially supported on Ubuntu 22.04:

```bash
# Add ROS2 repository key
sudo curl -sSL https://raw.githubusercontent.com/ros/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# Add ROS2 repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Update packages
sudo apt update

# Install ROS2 Humble Desktop (includes GUI tools)
sudo apt install -y ros-humble-desktop

# Install development tools
sudo apt install -y ros-humble-ros-core python3-colcon-common-extensions

# Add to bashrc for auto-sourcing
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

# Verify installation
ros2 --version

# Expected output: ROS 2 humble
```

### Option B: ROS2 in Docker (If Preferred)

If you prefer Docker (more isolated), see Step 7.

---

## Step 7: Docker Setup (Optional)

If you want ROS2 in Docker instead of native:

### 7.1 Install Docker

```bash
# Install Docker
sudo apt install -y docker.io docker-compose

# Add your user to docker group (so you don't need sudo)
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker

# Verify installation
docker --version
docker run hello-world
```

### 7.2 Build ROS2 Docker Image

```bash
# Navigate to docker directory
cd docker

# Build the Docker image (takes ~10-15 minutes)
docker build -t Mission-Logic-Engine-ros2:latest .

# Verify image was built
docker images | grep Mission-Logic-Engine-ros2
```

### 7.3 Test Docker Setup

```bash
# Run a test container
docker run --rm Mission-Logic-Engine-ros2:latest ros2 --version

# Expected output: ROS 2 rolling
```

---

## Step 8: Install Mission Planner

Mission Planner via Mono:

```bash
# Install Mono runtime
sudo apt install -y mono-runtime libmono-system-windows-forms4.0-cil \
  libmono-system-core4.0-cil libmono-system-management4.0-cil \
  libmono-system-xml-linq4.0-cil

# Download Mission Planner
wget https://firmware.ardupilot.org/Tools/MissionPlanner/MissionPlanner-latest.zip

# Unzip
unzip MissionPlanner-latest.zip -d ~/MissionPlanner

# Create launcher (optional)
cat > ~/.local/share/applications/missionplanner.desktop << EOF
[Desktop Entry]
Name=Mission Planner
Exec=mono ~/MissionPlanner/MissionPlanner.exe
Type=Application
Icon=application-x-ms-dos-executable
Categories=Utility;
EOF

# Test run (from MissionPlanner directory)
cd ~/MissionPlanner
mono MissionPlanner.exe &
```


## Step 9: Setup Hardware Connections (Optional)

### 9.1 LoRa Module Connection
1. Connect LoRa LR900-F module via USB
2. Check device listing:
   ```bash
   ls /dev/tty*
   # Should show /dev/ttyUSB0 or similar
   ```
3. Set permissions (if needed):
   ```bash
   sudo usermod -a -G dialout $USER
   newgrp dialout
   ```

### 9.2 Siyi HM30 Ground Unit

1. Connect Siyi HM30 Ground receiver via Ethernet
2. Configure network (usually automatic DHCP)
3. Test connection:
   ```bash
   ping 192.168.1.100  # Adjust IP if needed
   ```

---

## Step 10: Verify Installation

### 10.1 Test Python Environment

```bash
# Activate venv
source venv/bin/activate

# Test key imports
python3 -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python3 -c "import dronekit; print('DroneKit OK')"
python3 -c "import ultralytics; print('YOLOv8 OK')"
python3 -c "import mavproxy; print('MAVProxy OK')"
```

Expected output:
```
OpenCV: 4.8.0
DroneKit OK
YOLOv8 OK
MAVProxy OK
```

### 10.2 Test ROS2 (if native install)

```bash
# Source ROS2
source /opt/ros/humble/setup.bash

# Test ROS2
ros2 doctor

# Expected output: [OK] ...
```

### 10.3 Test Docker (if using)

```bash
# Test ROS2 in Docker
docker run --rm Mission-Logic-Engine-ros2:latest ros2 topic list
```

### 10.4 Test MAVProxy

```bash
# Activate venv
source venv/bin/activate

# Test MAVProxy
mavproxy.py --version

# Expected output: MAVProxy 1.8.73
```

---

## Step 11: Running Startup Scripts
### 11.1 Main Startup Script
Make the `start_gcs.sh` script executable:

```bash
chmod +x start_gcs.sh
```

### 11.2 Run Startup Script

```bash
./start_gcs.sh
```

---

## Troubleshooting

### Problem: "ros2 command not found"

**Solution**: Make sure to source ROS2:
```bash
source /opt/ros/humble/setup.bash
```

Or add to `~/.bashrc`:
```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### Problem: "Permission denied" for serial port

**Solution**: Add your user to dialout group:
```bash
sudo usermod -a -G dialout $USER
newgrp dialout
```

### Problem: "ImportError: No module named 'dronekit'"

**Solution**: Make sure virtual environment is activated:
```bash
source venv/bin/activate
pip install dronekit
```

### Problem: "Docker: permission denied"

**Solution**: Add user to docker group:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Problem: "/dev/ttyUSB0: No such device"

**Solution**: 
1. Check LoRa module is connected: `lsusb`
2. Find actual device: `ls /dev/tty*`
3. Update COM port in startup scripts

### Problem: "apt install fails" 

**Solution**: Update package list first:
```bash
sudo apt update
sudo apt upgrade -y
```

---

## Linux Quick Commands

```bash
# Activate Python venv
source venv/bin/activate

# Deactivate venv
deactivate

# Source ROS2
source /opt/ros/humble/setup.bash

# Run tests
pytest tests/

# Check code style
black src/
pylint src/

# Start MAVProxy
mavproxy.py --master=/dev/ttyUSB0:57600 --out=127.0.0.1:14550

# Launch ROS2 node
ros2 launch custom_gcs gcs.launch.py

# Start Docker container
docker run -it --rm --network=host Mission-Logic-Engine-ros2:latest bash
```


## Next Steps

Once installation is verified:

1. **Start MAVProxy Hub**:
   ```bash
   source venv/bin/activate
   mavproxy.py --master=/dev/ttyUSB0:57600 \
     --out=127.0.0.1:14550 \
     --out=127.0.0.1:14551 \
     --out=127.0.0.1:14552
   ```

2. **Start ROS2 Nodes** (in another terminal):
   ```bash
   source venv/bin/activate
   source /opt/ros/humble/setup.bash
   ros2 launch custom_gcs gcs.launch.py
   ```

3. **Open Mission Planner** (optional, in another terminal):
   ```bash
   cd ~/MissionPlanner
   mono MissionPlanner.exe &
   ```

4. **Read Documentation**:
   - [First Flight Guide](../docs/guides/FIRST_FLIGHT.md)
   - [ROS2 Architecture](../docs/architecture/PLANTUML_DIAGRAMS_GUIDE.md)


---

*Last updated: June 2026*
