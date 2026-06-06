# PlantUML Architecture Diagrams - User Guide

## Overview

This document describes four comprehensive PlantUML diagrams that visualize your autonomous fixed-wing UAV GCS architecture. Each diagram focuses on different aspects of the system.

---

## 📊 Diagram Files

### 1. **UAV_GCS_Architecture.puml** - Main Component Architecture
**Purpose**: Complete system overview showing all hardware and software components and their interconnections.

**Contains**:
- UAV components (Pixhawk 6C, Siyi A8 mini, Siyi HM30 Air, LoRa LR900-F)
- Ground station components (LoRa LR900-F, Siyi HM30 Ground)
- Software stack (MAVProxy, Mission Planner, Docker/ROS2, Custom GCS, DroneKit)
- Wireless links (LoRa 915MHz, Siyi 2.4GHz)
- Communication protocol labels

**Best For**:
- Understanding overall system architecture
- Team presentations
- Design review meetings
- Documentation

**Key Features**:
- Detailed component relationships
- Communication protocol annotations
- Latency estimates
- Data rate specifications

---

### 2. **UAV_GCS_DataFlow_Sequences.puml** - Sequence Diagrams with Timing
**Purpose**: Detailed message flows showing how data travels through the system over time.

**Contains 5 scenarios**:

1. **Telemetry Download (UAV → GCS)**
   - Pixhawk → LoRa TX → GCS LoRa RX → MAVProxy → ROS2
   - Shows parallel distribution to Mission Planner, ROS2, and logging
   - Total latency: 150-420ms

2. **Mission Command Upload (GCS → UAV)**
   - Custom GCS → DroneKit → MAVProxy → LoRa TX → Pixhawk
   - Command conversion and transmission
   - Total latency: 150-420ms

3. **Video Stream (UAV → GCS)**
   - Siyi A8 → Siyi HM30 Air → (2.4GHz) → Siyi HM30 Ground → ROS2
   - Video encoding/decoding latencies
   - Total latency: 80-200ms

4. **Parameter Tuning via Mission Planner**
   - Round-trip parameter reads/writes
   - Shows bidirectional communication
   - Demonstrates why tuning takes time (~300-800ms per operation)

5. **Critical Command Execution**
   - ARM and TAKEOFF sequence
   - State confirmation feedback loop
   - Practical example of mission control flow

**Best For**:
- Understanding system timing and latencies
- Debugging communication issues
- Explaining operation flow to non-technical stakeholders
- Performance analysis

**Key Insights**:
- Total round-trip latency for commands: 150-420ms (acceptable for autonomous missions)
- Video latency separate from telemetry (different links)
- Mission Planner operates independently on separate TCP connection
- DroneKit commands flow through MAVProxy like any other client

---

### 3. **ROS2_Architecture_Detail.puml** - ROS2 Middleware Details
**Purpose**: Deep dive into ROS2 pub/sub architecture and message definitions.

**Contains**:

**Publishers** (Data Sources):
- MAVLink Telemetry Publisher → `/vehicle/telemetry` topic
- Video Stream Publisher → `/camera/frames` topic
- System Status Publisher → `/system/status` topic (optional)

**Custom GCS Internals**:
- State Manager: Maintains vehicle state from telemetry
- Vision Pipeline: OpenCV preprocessing + YOLOv8 inference
- Mission Decision Engine: Core autonomy logic
- Logging & Monitoring: Persistent record keeping

**Subscribers** (Consumers):
- DroneKit wrapper: Sends commands back via `/mission/commands`

**Topic Specifications**:
- `/vehicle/telemetry`: 5-10 Hz, BEST_EFFORT QoS
- `/camera/frames`: 20-30 Hz, BEST_EFFORT QoS (drops allowed)
- `/mission/commands`: On-demand, RELIABLE QoS

**Internal Latencies**:
- Telemetry chain: 100-290ms total
- Vision chain: 85-240ms total
- Command chain: 100-340ms total

**Best For**:
- ROS2 development
- Message format specification
- Topic naming and organization
- QoS (Quality of Service) decisions
- Latency budgeting

**Includes**:
- ROS2 topic specifications (message types, fields, frequencies)
- Mission logic pseudocode
- Logging file structure
- Node startup order dependencies

---

### 4. **UAV_GCS_Simplified.puml** - Quick Reference
**Purpose**: Simplified overview for quick reference and presentations.

**Contains**:
- Minimal component boxes
- Essential connections only
- Key latency figures
- Communication summary
- Safety notes

**Best For**:
- Quick team briefings
- Presentations to decision-makers
- Troubleshooting checklists
- On-the-fly reference

**Key Takeaways Provided**:
- Latency budget for each path
- Bandwidth requirements
- Component purposes
- Failsafe mechanisms

---

## 🔄 How Components Communicate

### Telemetry Path (UAV → GCS)
```
Pixhawk 6C
  ↓ (UART, 57600 baud)
LoRa Module (UAV)
  ↓ (915 MHz RF, 100-200ms air time)
LoRa Module (GCS)
  ↓ (USB/COM3 serial)
MAVProxy
  ├→ TCP:14550 (Mission Planner)
  ├→ TCP:14551 (ROS2 Telemetry Pub)
  └→ TCP:14552 (DroneKit)
```

**Total Latency**: LoRa air time (100-200ms) + processing (50-220ms) = **150-420ms**

### Video Path (UAV → GCS)
```
Siyi A8 Mini Camera
  ↓ (GigE Ethernet, 1Gbps)
Siyi HM30 Air (Video Encoder)
  ↓ (2.4GHz proprietary RF, 20-100ms latency)
Siyi HM30 Ground (Receiver)
  ↓ (Ethernet)
ROS2 Video Publisher
  ↓ (ROS2 topic subscription)
Custom GCS Software
```

**Total Latency**: Siyi link (20-100ms) + processing (60-140ms) = **80-240ms**

### Command Path (GCS → UAV)
```
Custom GCS Software (Mission Logic)
  ↓ (ROS2 topic publish)
DroneKit-Python
  ↓ (Convert to MAVLink)
MAVProxy (TCP:14552)
  ↓ (USB/COM3 serial)
LoRa Module (GCS)
  ↓ (915 MHz RF, 100-200ms air time)
LoRa Module (UAV)
  ↓ (UART)
Pixhawk 6C Flight Controller
```

**Total Latency**: LoRa air time (100-200ms) + processing (50-140ms) = **150-340ms**

---

## ⚙️ Component Responsibilities

| Component | Role | Key Features |
|-----------|------|--------------|
| **Pixhawk 6C** | Flight control | Autopilot, autonomous flight, sensor fusion |
| **LoRa LR900-F** | Long-range telemetry | 30km range, 2.1 KB/s, low power |
| **Siyi A8 Mini** | Video capture | GigE output, 1080p, real-time |
| **Siyi HM30** | Video transmission | Proprietary 2.4GHz, low latency (~50ms) |
| **MAVProxy** | Telemetry hub | Multiplexes clients, prevents serial conflicts |
| **Mission Planner** | Flight tuning | Parameter management, pre/post-flight analysis |
| **ROS2** | Middleware | Pub/sub abstraction, sensor decoupling |
| **Custom GCS** | Autonomy brain | Mission logic, CV inference, decision-making |
| **DroneKit** | Command interface | High-level flight control API |

---

## 🔌 Physical Connections

### Ground Station (Windows PC)

**USB Ports**:
- COM3/USB: LoRa LR900-F module (serial adapter)

**Ethernet Ports**:
- Siyi HM30 Ground unit (video receiver)

**Software Ports** (TCP/IP localhost):
- 14550: Mission Planner ↔ MAVProxy (telemetry monitoring)
- 14551: ROS2 Telemetry Publisher ↔ MAVProxy (telemetry input)
- 14552: DroneKit ↔ MAVProxy (command output)

### Docker Container (ROS2)

**External Connections**:
- TCP:14551 to MAVProxy (incoming telemetry)
- Ethernet from Siyi HM30 (incoming video)
- TCP:14552 to MAVProxy (outgoing commands)

**Internal Topics** (ROS Domain):
- `/vehicle/telemetry` - Flight state
- `/camera/frames` - Video frames
- `/mission/commands` - Control commands
- `/system/status` - Optional diagnostics

---

## 📈 Latency Analysis

### Mission-Critical Latencies

| Path | Min | Typical | Max | Acceptable? |
|------|-----|---------|-----|-------------|
| Telemetry (DOWN) | 120ms | 250ms | 420ms | ✅ Yes (non-critical) |
| Video | 50ms | 140ms | 240ms | ✅ Yes (CV inference time) |
| Command (UP) | 120ms | 250ms | 340ms | ✅ Yes (autonomous pre-planning) |
| Parameter Tuning | 300ms | 550ms | 800ms | ⚠️ Slow (requires patience) |

### Processing Breakdown

**Per Command Cycle**:
1. Telemetry reception & parsing: 50-100ms
2. State update in GCS: 10-50ms
3. Vision inference (if needed): 30-50ms
4. Decision logic execution: 20-100ms
5. DroneKit conversion: 10-20ms
6. MAVProxy forwarding: 5-10ms
7. LoRa transmission: 100-200ms
8. Pixhawk processing: 20-50ms

**Total**: 245-580ms per decision cycle

---

## 🛡️ Safety & Reliability Features

### Built-in Safeguards

1. **Pixhawk Failsafes**:
   - Geofencing (hardware-enforced)
   - Battery low threshold → RTH
   - GPS loss → RTH or hover
   - RC loss → RTH or land
   - LoRa loss → RTH (configurable timeout)

2. **GCS Watchdog**:
   - Monitor MAVProxy heartbeat
   - Monitor ROS2 node health
   - Timeout triggers emergency landing

3. **Logging & Auditing**:
   - MAVProxy logs all MAVLink messages (.tlog, .bin)
   - ROS2 logs all topics (custom .csv files)
   - Mission Planner records flight data
   - Post-flight analysis possible

4. **Multiplexing Safety**:
   - MAVProxy prevents serial port conflicts
   - Only one client can arm/disarm (enforced by flight controller)
   - Command queueing prevents race conditions

---

## 🔧 How to Use These Diagrams

### For Design Review
1. Start with **Simplified** diagram for 1-minute overview
2. Use **Main Architecture** diagram for detailed component questions
3. Refer to **ROS2 Detail** for middleware-specific design choices

### For Development
1. Use **DataFlow Sequences** to understand timing requirements
2. Reference **ROS2 Detail** for topic names and message formats
3. Use **Main Architecture** to verify hardware connections

### For Troubleshooting
1. Check **DataFlow Sequences** to understand where data is lost
2. Verify component connections in **Main Architecture**
3. Check ROS2 topics in **ROS2 Detail** for subscription issues

### For Documentation
1. Use **Simplified** for high-level overviews
2. Use **Main Architecture** for technical documentation
3. Use **DataFlow** for explaining system behavior
4. Use **ROS2 Detail** for developer guides

---

## 📝 Component Communication Checklist

- [ ] LoRa modules paired and configured (915 MHz)
- [ ] Pixhawk 6C TELEM1 wired to LoRa TX/RX (UART)
- [ ] Siyi A8 mini GigE output connected to Siyi HM30 Air
- [ ] Siyi HM30 Ground receiver powered and in range
- [ ] Ground LoRa module appears on COM3 (USB serial)
- [ ] MAVProxy configured to read COM3 at 57600 baud
- [ ] Mission Planner can connect to MAVProxy TCP:14550
- [ ] Docker container can reach MAVProxy on TCP:14551
- [ ] ROS2 Telemetry Publisher running and publishing `/vehicle/telemetry`
- [ ] ROS2 Video Publisher running and publishing `/camera/frames`
- [ ] Custom GCS subscribing to both topics
- [ ] DroneKit able to send to MAVProxy TCP:14552
- [ ] Siyi HM30 Ground Ethernet connected to GCS network
- [ ] Video frames arriving in ROS2 at 20-30 Hz

---

## 🚀 Quick Start Verification

1. **Terminal 1**: Start MAVProxy
   ```bash
   mavproxy.py --master=COM3:57600 --out=127.0.0.1:14550 --out=127.0.0.1:14551 --out=127.0.0.1:14552
   ```

2. **Check**: MAVProxy shows connected to Pixhawk

3. **Terminal 2**: Launch ROS2 nodes
   ```bash
   ros2 launch custom_gcs gcs.launch.py
   ```

4. **Check**: ROS2 nodes show topics published
   ```bash
   ros2 topic list
   # Should show: /vehicle/telemetry, /camera/frames, /mission/commands
   ```

5. **Terminal 3**: Verify telemetry
   ```bash
   ros2 topic echo /vehicle/telemetry
   # Should show 5-10 Hz updates
   ```

6. **Terminal 4**: Verify video
   ```bash
   ros2 topic echo /camera/frames --once | head
   # Should show image data with timestamp
   ```

7. **Mission Planner**: Verify connection to TCP:14550
   - Should see live telemetry
   - Should be able to read parameters
   - Should see arm status

---

## 📚 Related Documentation

- **ROS2 Configuration**: See ROS2_Architecture_Detail.puml
- **Hardware Connections**: See UAV_GCS_Architecture.puml
- **Timing Analysis**: See UAV_GCS_DataFlow_Sequences.puml
- **Quick Reference**: See UAV_GCS_Simplified.puml

---

## 📞 Troubleshooting Guide

**"MAVProxy won't connect to LoRa module"**
- Check COM port number (may not be COM3)
- Verify USB driver installed
- Try different baud rate

**"ROS2 topics not publishing"**
- Verify MAVProxy is running first
- Check TCP port 14551 is listening
- Check Docker network settings (host vs bridge)

**"No video in ROS2"**
- Verify Siyi HM30 Ground is powered
- Check Ethernet cable connection
- Verify video receiver on correct IP range

**"Commands not reaching Pixhawk"**
- Verify Mission Planner can ARM/DISARM (tests uplink)
- Check LoRa module antenna is connected
- Verify both LoRa modules are powered

---

## Version Information

- **Created**: 2026
- **Architecture**: Pixhawk 6C + ArduPlane + LoRa LR900-F + Siyi A8 mini + HM30 + ROS2
- **Updated**: Removed WiFi HaLow (Doppler effects on moving UAVs)
- **Current Status**: Ready for development

