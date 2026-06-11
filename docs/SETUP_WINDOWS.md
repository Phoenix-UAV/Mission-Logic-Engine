# Windows Setup Guide

**Platform**: Windows 10 / Windows 11  
**Setup Time**: 1-2 hours  
**Difficulty**: Medium  
**Docker Required**: Yes (for ROS2)

---

## 📋 Prerequisites

Before starting, ensure you have:

- [ ] Administrator access to your Windows machine
- [ ] 10 GB free disk space
- [ ] 8 GB RAM (16 GB recommended)
- [ ] Stable internet connection (for downloads)
- [ ] USB port for LoRa module (for testing)

---

## 🔧 Step 1: Install Core Tools

### 1.1 Install Git

1. Download from https://git-scm.com/download/win
2. Run installer with default settings
3. Verify installation:
   ```powershell
   git --version
   ```

### 1.2 Install Python 3.11

1. Download from https://www.python.org/downloads/ (Python 3.11)
2. **IMPORTANT**: Check "Add Python 3.11 to PATH" during installation
3. Choose "Install Now" for default setup
4. Verify installation:
   ```powershell
   python --version
   pip --version
   ```

### 1.3 Install Docker Desktop

1. Download from https://www.docker.com/products/docker-desktop
2. Run installer with default settings
3. During installation, ensure **WSL 2** backend is selected
4. Restart computer when prompted
5. Verify installation:
   ```powershell
   docker --version
   docker run hello-world
   ```

### 1.4 Install Visual Studio Code (Optional but Recommended)

1. Download from https://code.visualstudio.com/
2. Install with default settings
3. Install extensions:
   - Python
   - PlantUML
   - Docker
   - Git Graph

---

## 🚀 Step 2: Clone Repository (If you already did this from reading the README file, skip this part!)

```powershell
# Navigate to desired directory
cd C:\Users\YourUsername\Documents
# List contents to verify
dir
```
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
# List contents to verify
dir

Expected output:
```
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----         6/15/2026  10:30 AM                docs
d-----         6/15/2026  10:30 AM                src
d-----         6/15/2026  10:30 AM                tests
d-----         6/15/2026  10:30 AM                docker
-a----         6/15/2026  10:30 AM           5432 README.md
-a----         6/15/2026  10:30 AM           2148 requirements.txt
-a----         6/15/2026  10:30 AM           1256 setup.py
```

---

## 📦 Step 3: Create Python Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# You should see (venv) in your prompt now
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📥 Step 4: Install Python Dependencies

```powershell
# Make sure you're in the Mission-Logic-Engine directory with venv activated
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify key packages installed
pip list | Select-String -Pattern "dronekit|opencv|ultralytics|mavproxy"
```

Expected output:
```
dronekit              2.9.2
dronekit-sitl         3.3.0
opencv-python         4.8.0
ultralytics           8.0.0
mavproxy              1.8.73
```

---

## 🐳 Step 5: Setup Docker for ROS2

### 5.1 Configure Docker Settings

1. Open Docker Desktop
2. Go to Settings → Resources
3. Ensure at least 4 CPU cores and 4 GB RAM are allocated
4. Click "Apply & Restart"

### 5.2 Build ROS2 Docker Image

```powershell
# Navigate to docker directory
cd docker

# Build the Docker image (takes ~10-15 minutes)
docker build -t Mission-Logic-Engine-ros2:latest .

# Verify image was built
docker images | Select-String "Mission-Logic-Engine-ros2"
```

### 5.3 Test Docker Setup

```powershell
# Run a test container
docker run --rm Mission-Logic-Engine-ros2:latest ros2 --version

# Expected output: ROS 2 rolling 20XX-XX-XX (or similar)
```

---

## ⚙️ Step 6: Install Mission Planner

Mission Planner is used for **pre-flight tuning and post-flight analysis only** (not for flight control).

### 6.1 Download and Install

1. Visit https://ardupilot.org/planner/docs/mission-planner-installation.html
2. Download latest Windows installer
3. Run installer with default settings
4. Verify installation by launching Mission Planner

### 6.2 (Optional) Install MAVProxy

```powershell
# MAVProxy is already installed via pip, but verify
mavproxy.py --version

# Expected output: MAVProxy 1.8.73
```

---

## 🔌 Step 7: Setup Hardware Connections (for Real Hardware Testing)

### 7.1 LoRa Module Connection

1. Connect LoRa LR900-F module to USB port
2. Note the COM port number (Device Manager → Ports → COM3, etc.)
3. Test connection:
   ```powershell
   # Find COM port
   [System.IO.Ports.SerialPort]::GetPortNames()
   ```

### 7.2 Siyi HM30 Ground Unit

1. Connect Siyi HM30 Ground receiver to network via Ethernet
2. Connect power supply
3. Wait for boot (LED indicators should show status)
4. Test connection:
   ```powershell
   ping 192.168.1.100  # Adjust IP if needed
   ```

---

## ✅ Step 8: Verify Installation

### 8.1 Test Python Environment

```powershell
# Activate venv if not already active
.\venv\Scripts\Activate.ps1

# Test key imports
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python -c "import dronekit; print('DroneKit OK')"
python -c "import ultralytics; print('YOLOv8 OK')"
python -c "import mavproxy; print('MAVProxy OK')"
```

Expected output:
```
OpenCV: 4.8.0
DroneKit OK
YOLOv8 OK
MAVProxy OK
```

### 8.2 Test Docker Environment

```powershell
# Test ROS2 in Docker
docker run --rm Mission-Logic-Engine-ros2:latest ros2 topic list
```

### 8.3 Test MAVProxy

```powershell
# Start MAVProxy with SITL (no hardware needed)
mavproxy.py --master=127.0.0.1:5760 --out=127.0.0.1:14550

# In another PowerShell window, test telemetry
python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 14550)); print('Connected')"

# Stop MAVProxy (Ctrl+C in first window)
```

---

## 🐛 Troubleshooting

### Problem: "Python is not recognized"

**Solution**: Python is not in your PATH. Reinstall Python and **check "Add Python to PATH"** during installation.

### Problem: "Docker is not running"

**Solution**: 
1. Check Docker Desktop is running (system tray)
2. If not, click Docker icon in system tray
3. Wait for "Docker Desktop is running" message

### Problem: "pip install fails with 'permission denied'"

**Solution**: Ensure you've activated the virtual environment:
```powershell
.\venv\Scripts\Activate.ps1
```

### Problem: "COM port not found for LoRa module"

**Solution**:
1. Open Device Manager
2. Check "Ports (COM & LPT)"
3. Plug/unplug USB cable to identify correct port
4. Install CH340 driver if needed: https://sparks.gogo.co.nz/ch340.html

### Problem: "Docker build fails with disk space error"

**Solution**: 
1. Ensure 10 GB free disk space: `dir C:\`
2. Clean Docker: `docker system prune -a`
3. Clear pip cache: `pip cache purge`
4. Try build again

---

## 🚀 Next Steps

Once installation is verified:

1. **Start MAVProxy Hub**:
   ```powershell
   # Terminal 1
   mavproxy.py --master=COM3:57600 --out=127.0.0.1:14550 --out=127.0.0.1:14551 --out=127.0.0.1:14552
   ```

2. **Start ROS2 Container**:
   ```powershell
   # Terminal 2
   docker run -it --rm --network=host Mission-Logic-Engine-ros2:latest
   # Inside container: ros2 launch custom_gcs gcs.launch.py
   ```

3. **Open Mission Planner**:
   - Connect to localhost:14550
   - Verify telemetry stream

4. **Read Documentation**:
   - [First Flight Guide](../docs/guides/FIRST_FLIGHT.md)
   - [ROS2 Architecture](../docs/architecture/PLANTUML_DIAGRAMS_GUIDE.md)

---

## 📝 Create a Windows Batch Script (Optional but Convenient)

Create `start_gcs.bat` in repo root:

```batch
@echo off
echo Starting Drone GCS on Windows...

REM Activate Python virtual environment
call venv\Scripts\activate.bat

REM Start MAVProxy in a new window
echo Starting MAVProxy...
start "MAVProxy" cmd /k mavproxy.py --master=COM3:57600 --out=127.0.0.1:14550 --out=127.0.0.1:14551 --out=127.0.0.1:14552

REM Wait for MAVProxy to start
timeout /t 3

REM Start Docker ROS2 container
echo Starting ROS2 Docker container...
start "ROS2" cmd /k docker run -it --rm --network=host Mission-Logic-Engine-ros2:latest bash

REM Open Mission Planner (if installed)
echo Mission Planner should be opened manually or run from start menu

echo.
echo All components starting. Check windows above.
```

Then run: `.\start_gcs.bat`

---

## 🆘 Need Help?

- **Installation problems**: Check troubleshooting section above
- **Docker issues**: See [Troubleshooting Docker](../docs/troubleshooting/DOCKER.md)
- **Code issues**: Check GitHub Issues
- **General questions**: Open GitHub Discussion or Discord

---

## ✅ Windows Setup Checklist

- [ ] Git installed and working
- [ ] Python 3.11 installed with PATH configured
- [ ] Docker Desktop installed and running
- [ ] Virtual environment created and activated
- [ ] Python dependencies installed (pip list check)
- [ ] Docker image built successfully
- [ ] Mission Planner installed
- [ ] Hardware connections tested (if available)
- [ ] All verification tests passed
- [ ] Read next steps documentation

---

**Windows setup complete! You're ready to run the custom GCS software.** 🎉

Next: [SETUP_LINUX.md](SETUP_LINUX.md) (if needed) or read [FIRST_FLIGHT.md](../docs/guides/FIRST_FLIGHT.md)

---

*Last updated: June 2026*
