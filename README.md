# Mission-Logic-Engine
Custom Mission Planning Interface.

## Instructions:
- Make a branch with title your name and the part of the project you are working on.
- work only on your branch main will be protected.

# Autonomous Fixed-Wing UAV Ground Control System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![ROS2](https://img.shields.io/badge/ROS2-Humble-blue.svg)](https://docs.ros.org/en/humble/)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04+-orange.svg)]()

A modular, ROS2-based ground control system for autonomous fixed-wing UAVs using Pixhawk 6C flight controller, LoRa telemetry, Siyi A8 mini camera, and real-time computer vision inference.

## 🎯 Project Overview

This repository contains a complete architecture for controlling autonomous fixed-wing aircraft with:

- **Flight Control**: Pixhawk 6C with ArduPlane firmware
- **Telemetry**: MicoAir LR900-F LoRa modules (100-400ms latency, 30km range)
- **Video Streaming**: Siyi A8 mini camera with HM30 encoders (20-100ms latency)
- **Ground Station**: ROS2-based custom autonomy software in Docker
- **Logging & Analysis**: Mission Planner integration with MAVProxy
- **Computer Vision**: OpenCV + YOLOv8 nano for object detection
- **Sensor Fusion**: Multi-sensor state estimation for robust flight

## 📋 System Requirements

### Minimum Hardware
- **Ground PC**: 
  - CPU: Dual-core processor (quad-core recommended)
  - RAM: 8GB (16GB recommended for CV inference)
  - Storage: 256GB SSD
  - USB ports: 2+ (for LoRa module, optional serial adapter)
  - Ethernet: 1 port (for Siyi HM30 video receiver)

### Supported Operating Systems
- **Windows 10/11** (21H2+) with Docker Desktop
- **Ubuntu 22.04 LTS** or **24.04 LTS** (native or Docker)
- ~~**macOS 12+** with Docker Desktop (limited support)~~

---

## 🚀 Quick Start

### For Each Team Member

1. **Fork the repository**:
   ```bash
   # Go to https://github.com/YOUR-USERNAME/Mission-Logic-Engine.git
   # Click "Fork" button
   ```

2. **Clone their fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Mission-Logic-Engine.git
   cd Mission-Logic-Engine
   ```

3. **Follow OS-specific setup**:
   - Windows: `SETUP_WINDOWS.md`
   - Linux: `SETUP_LINUX.md`
   - ~~macOS: `SETUP_MACOS.md`~~

4. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/Phoenix-UAV/Mission-Logic-Engine.git
   ```

5. **Create a branch**:
   ```bash
   git checkout -b feature/their-feature
   ```

6. **They make changes and submit PR** (see CONTRIBUTING.md)

### 2. Run OS-Specific Setup

Choose your operating system:

#### **Windows 10/11**
```bash
# Run the setup script
# NOT YET SET UP. TODO. DISCUSS NEXT MEETING - ROHAN 6/6/26
.\scripts\setup_windows.bat

# Or manually follow: docs/SETUP_WINDOWS.md
```

#### **Ubuntu 22.04/24.04 LTS**
```bash
# Make script executable
# NOT YET SET UP. TODO. DISCUSS NEXT MEETING - ROHAN 6/6/26
chmod +x scripts/setup_linux.sh

# Run setup
./scripts/setup_linux.sh

# Or manually follow: docs/SETUP_LINUX.md
```

#### **macOS 12+**
```bash
# Make script executable
# NOT YET SET UP. TODO. DISCUSS NEXT MEETING, if we even need it... - ROHAN 6/6/26
chmod +x scripts/setup_macos.sh

# Run setup
./scripts/setup_macos.sh
## NOT YET SET UP. TODO. DISCUSS NEXT MEETING, if even need it... - ROHAN 6/6/26
# Or manually follow: docs/SETUP_MACOS.md
```

### 3. Verify Installation

```bash
# Check Python environment
python --version  # Should be 3.11+

# Check Docker (if using Docker)
docker --version
docker run hello-world

# Check ROS2 (Linux)
source /opt/ros/humble/setup.bash
ros2 --version
```

### 4. Hardware Setup
1. **Connect LoRa Module**: USB serial adapter to ground PC
2. **Connect Siyi HM30 Ground Unit**: Ethernet to PC network
3. **Power up UAV**: Ensure Pixhawk 6C and Siyi A8 mini are powered
4. See [Hardware Setup Guide](docs/HARDWARE_SETUP.md) for details [TODO NOT SET UP YET. DISCUSS NEXT MEETING - ROHAN 6/6/26]

### 5. Launch the System

```bash
# Terminal 1: Start MAVProxy (external process, MUST run first)
mavproxy.py --master=COM3:57600 --out=127.0.0.1:14550 --out=127.0.0.1:14551 --out=127.0.0.1:14552

# Terminal 2: Launch Docker container with ROS2
docker-compose up -d

# Terminal 3: Verify ROS2 is running
docker exec Mission-Logic-Engine ros2 topic list
# Should show: /vehicle/telemetry, /camera/frames, /mission/commands, /system/status
```

## Starting MAVProxy
### Using the Bash Script
To use the script:
1. In `MAVProxy/mavinit.sh`, Change the variable `uav` to the directory connected to the UAV telemetry.
2. From the base directory, run `./MAVProxy/mavinit.sh`.

## Configuring MAVProxy
To configure MAVProxy, use the files `Phoenix/mavinit.scr` and `MAVProxy/mavinit.sh`.

### 6. Launch Mission Planner (Optional)

Connect to TCP:14550 for monitoring and parameter tuning.

---

## 📂 Project Structure

```
Mission-Logic-Engine/
├── docs/
│   ├── ARCHITECTURE.md              # System design document
│   ├── SETUP_WINDOWS.md             # Windows setup guide
│   ├── SETUP_LINUX.md               # Linux setup guide
│   ├── SETUP_MACOS.md               # macOS setup guide
│   ├── HARDWARE_SETUP.md            # Hardware connection guide
│   ├── API_REFERENCE.md             # ROS2 API reference
│   ├── TROUBLESHOOTING.md           # Common issues & solutions
│   └── diagrams/
│       ├── UAV_GCS_Architecture.puml
│       ├── UAV_GCS_DataFlow_Sequences.puml
│       └── ROS2_Architecture_Detail.puml
│
├── docker/
│   ├── Dockerfile                   # ROS2 + dependencies image
│   ├── docker-compose.yml           # Compose configuration
│   └── .dockerignore
│
├── ros2_ws/                         # ROS2 workspace
│   ├── src/
│   │   ├── custom_gcs/
│   │   │   ├── custom_gcs/
│   │   │   │   ├── gcs_node.py      # Main GCS node
│   │   │   │   ├── mission_logic.py # Decision engine
│   │   │   │   ├── vision_pipeline.py
│   │   │   │   └── state_manager.py
│   │   │   ├── launch/
│   │   │   │   └── gcs.launch.py
│   │   │   ├── package.xml
│   │   │   └── setup.py
│   │   └── telemetry_bridge/
│   └── .gitignore
│
├── scripts/
│   ├── setup_windows.bat            # Windows setup automation
│   ├── setup_linux.sh               # Linux setup automation
│   ├── setup_macos.sh               # macOS setup automation
│   └── README.md
│
├── config/
│   ├── default_config.yaml
│   ├── hardware_config.yaml
│   └── mavproxy.conf
│
├── tests/
│   ├── test_mavlink.py
│   ├── test_vision.py
│   └── README.md
│
├── .github/
│   ├── CONTRIBUTING.md
│   └── workflows/
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md (this file)
```

---

## 🛠️ Development Workflow by OS

### Linux/Ubuntu (Native - Recommended)

```bash
# 1. Setup
git clone <repo>
cd Mission-Logic-Engine
./scripts/setup_linux.sh

# 2. Build ROS2 workspace
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build
source install/setup.bash

# 3. Start MAVProxy
mavproxy.py --master=/dev/ttyUSB0:57600 --out=127.0.0.1:14550 --out=127.0.0.1:14551 --out=127.0.0.1:14552

# 4. Launch GCS (new terminal)
ros2 launch custom_gcs gcs.launch.py

# 5. Monitor telemetry (new terminal)
ros2 topic echo /vehicle/telemetry
```

### Windows (Docker - Recommended)

```powershell
# 1. Setup
git clone <repo>
cd Mission-Logic-Engine
.\scripts\setup_windows.bat

# 2. Start Docker container
docker-compose up -d

# 3. Start MAVProxy (Windows native)
mavproxy.py --master=COM3:57600 --out=127.0.0.1:14550 --out=127.0.0.1:14551 --out=127.0.0.1:14552

# 4. Launch GCS (in Docker)
docker exec -it Mission-Logic-Engine bash
ros2 launch custom_gcs gcs.launch.py

# 5. Monitor telemetry (another PowerShell)
docker exec Mission-Logic-Engine ros2 topic echo /vehicle/telemetry
```

### macOS (Docker)

```bash
# 1. Setup
git clone <repo>
cd Mission-Logic-Engine
chmod +x scripts/setup_macos.sh
./scripts/setup_macos.sh

# 2. Follow Docker workflow from Windows section
docker-compose up -d
# ... rest of Docker workflow
```

---

## 🔌 Hardware Configuration

Edit `config/hardware_config.yaml`:

```yaml
# Serial ports (OS-specific)
lora:
  port: "/dev/ttyUSB0"        # Linux/macOS
  # port: "COM3"              # Windows (find in Device Manager)
  baudrate: 57600
  
# Video receiver
siyi_hm30:
  ip_address: "192.168.1.100"
  port: 554

# ROS2 settings
ros2:
  domain_id: 0
  telemetry_rate_hz: 10
  video_rate_hz: 30
  
# Safety parameters
mission:
  max_altitude_m: 120
  max_range_km: 10
  battery_min_voltage: 10.5
```

---

## 📊 System Performance

### Latencies
- **Telemetry**: 150-420ms (LoRa + processing)
- **Video**: 80-200ms (Siyi + inference)
- **Commands**: 150-420ms (LoRa + processing)

### Bandwidth
- **Telemetry**: 2.1 KB/s
- **Video**: 5-15 Mbps (compressed)
- **Range**: 10-30km (line-of-sight)

---

## 🔒 Safety Features

✅ Hardware geofencing (Pixhawk 6C)  
✅ Automatic RTH on battery low / GPS loss / LoRa loss  
✅ Watchdog timers for system health  
✅ Complete telemetry logging (MAVProxy + ROS2)  
✅ Command queueing (no race conditions)  

---

## 📖 Key Documentation

| Document | Purpose |
|----------|---------|
| [SETUP_WINDOWS.md](docs/SETUP_WINDOWS.md) | Detailed Windows installation |
| [SETUP_LINUX.md](docs/SETUP_LINUX.md) | Detailed Linux installation |
| [SETUP_MACOS.md](docs/SETUP_MACOS.md) | Detailed macOS installation (TODO -Rohan 6/6/26)|
| [ARCHITECTURE.md](docs/diagrams/PLANTUML_DIAGRAMS_GUIDE.md) | System design & data flows |
| [HARDWARE_SETUP.md](docs/HARDWARE_SETUP.md) | Physical connections (TODO -Rohan 6/6/26)|
| [API_REFERENCE.md](docs/API_REFERENCE.md) | ROS2 topics & messages (TODO -Rohan 6/6/26)|
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues & fixes (TODO -Rohan 6/6/26)|

---

## 🤝 Contributing

1. See [CONTRIBUTING.md](.github/CONTRIBUTING.md)
2. Fork the repository
3. Create a feature branch (`git checkout -b feature/your-feature`)
4. Commit changes (`git commit -m 'Add feature'`)
5. Push to branch (`git push origin feature/your-feature`)
6. Open a Pull Request

---

## 📞 Troubleshooting

### LoRa Module Not Found

**Linux:**
```bash
ls -la /dev/tty*
dmesg | tail  # Check for USB connection
```

**Windows:**
```powershell
Get-WmiObject Win32_SerialPort
# Look for your LoRa adapter, note the COM port
```

### MAVProxy Connection Issues

```bash
# Test MAVProxy without ROS2
mavproxy.py --master=<PORT>:<BAUD> --console
# Look for "bad header" (indicates data flowing)
```

### ROS2 Topics Not Showing

```bash
# Verify MAVProxy is running
netstat -an | grep 14551  # Should show LISTENING

# Check Docker logs
docker logs Mission-Logic-Engine

# Restart Docker container
docker-compose restart
```

---

## 📚 Research References

Implemented research from:
- "Autonomous Drone Communication Using LoRa and MAVLink" (CSUN Thesis)
- "A Modular System Architecture for UAV Swarms Using ROS 2" (2025)
- "LightUAV-YOLO: Lightweight Object Detection for UAVs" (2024)

See [RESEARCH_PAPERS.md](docs/RESEARCH_PAPERS.md) for full bibliography.

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

**Last Updated**: January 2026  
**Status**: Active Development  
**Python**: 3.11+  
**ROS2**: Humble  
**Tested**: Ubuntu 22.04/24.04, Windows 11, macOS 13+
