# RescueMesh Use Cases

## Overview

Each use case defines a complete mission scenario with objectives, terrain characteristics, recommended agents, expected failures, and outputs.

---

## 1. Collapsed Building Search

**Priority**: Life Safety

### Mission Objective
Rapidly map unstable voids and detect signs of human presence in partially collapsed structures where traditional search methods are too dangerous or time-consuming.

### Terrain Characteristics
- Collapsed building with unstable voids and confined spaces
- GPS denied or unreliable inside structure
- Radio attenuation through concrete and steel
- Dark with dust obscuration
- Unstable structure, sharp debris, potential secondary collapse

### Recommended Agents

**Survey Drone (Drone A)**
- LiDAR for 3D mapping
- Thermal camera
- RGB camera
- High endurance battery

**Detection Drone (Drone B)**
- Microphone array for audio detection
- CO2 sensor
- WiFi/Bluetooth scanner
- Relay capability

**Deep Penetration (Drone C)**
- Compact design for narrow passages
- Thermal camera
- Audio sensor
- NFC black-box module

**Relay Node**
- High-power radio
- Mesh networking
- Extended battery or wired power

### Expected Sensors
- LiDAR
- Thermal imaging
- Microphone array
- CO2 sensor
- WiFi/Bluetooth scanner
- RGB camera
- IMU
- Battery monitor

### Failure Risks
- Dust occlusion → LiDAR/camera degradation
- Radio packet loss → Intermittent communications
- Battery drain → Accelerated consumption in hovering
- Tactical relay decision → Drone lands to serve as relay

### Expected Outputs
- 3D void map (point cloud)
- Thermal anomaly detections
- Voice-like audio events
- WiFi/Bluetooth device signals
- Relay topology map
- Recommended access routes for human rescuers
- AI-ranked detection list for human review

### AI Prompt Templates
```json
{
  "mission_type": "collapsed_building_search",
  "priority": "life_safety",
  "agent_role": "thermal_audio_analyst",
  "inputs": ["thermal_frames", "audio_segments", "wifi_bluetooth_scan", "3d_void_map"],
  "questions": [
    "Identify possible human presence",
    "Rank detections by confidence",
    "Highlight hazards blocking rescuer access",
    "Suggest next drone waypoint"
  ]
}
```

---

## 2. Cave Rescue

**Priority**: Mapping and Path Discovery

### Mission Objective
Map unknown cave systems to locate lost or injured persons and identify safe access routes for rescue teams.

### Terrain Characteristics
- Natural or abandoned mine tunnels
- GPS completely denied
- Radio attenuation through rock
- Narrow passages and vertical drops
- Water hazards
- Low light

### Recommended Agents
- Survey drone with LiDAR
- Ground crawler for uneven terrain
- Static relay nodes for communications
- Thermal/audio detection drone

### Expected Sensors
- LiDAR
- IMU
- Temperature
- Humidity
- Audio
- Atmospheric sensors

### Failure Risks
- GPS denial
- Radio total loss in deep sections
- Water damage
- Tight passage blocking

### Expected Outputs
- Tunnel map
- Safe route estimate
- Relay placement map
- Vertical profile
- Water depth measurements

---

## 3. Flooded Structure

**Priority**: Amphibious Inspection

### Mission Objective
Inspect partially flooded buildings or underground structures to map obstructions and identify safe/unsafe zones.

### Terrain Characteristics
- Standing or flowing water
- Submerged debris
- Corrosion risk
- Low visibility underwater
- Buoyancy challenges

### Recommended Agents
- Amphibious drone
- Underwater sonar
- Surface relay drone
- Ground robot for dry sections

### Expected Sensors
- Pressure
- Sonar
- Temperature
- Water quality sensors
- Camera (above water)

### Failure Risks
- Water ingress
- Corrosion
- Loss of buoyancy control
- Visibility issues

### Expected Outputs
- Water depth model
- Obstruction map
- Safe passage routes
- Recoverable asset list

---

## 4. Industrial Confined Space Inspection

**Priority**: Hazardous Material Assessment

### Mission Objective
Inspect industrial facilities with hazardous materials or confined spaces without exposing human personnel.

### Terrain Characteristics
- Confined spaces with limited access
- Potentially toxic atmosphere
- Heat or radiation
- Complex geometry
- Electromagnetic interference

### Recommended Agents
- Small inspection drone
- Gas sensors
- Radiation detectors
- Relay nodes

### Expected Sensors
- Gas sensors (CO, CO2, H2S, CH4)
- Thermal camera
- Radiation detector
- Camera with lighting
- Air quality sensors

### Failure Risks
- Toxic atmosphere damage
- Heat damage
- EM interference
- Loss of orientation

### Expected Outputs
- Hazard map
- Gas concentration readings
- Recommended PPE for human entry
- Structural condition report

---

## Use Case Template

When creating a new use case, define:

- **Mission objective**: Clear statement of primary goal
- **Terrain type**: Environment description
- **Expected hazards**: Known risks
- **Recommended agents**: Suggested hardware types
- **Recommended sensors**: Required sensor suite
- **Communications assumptions**: Expected signal conditions
- **Failure risks**: Anticipated failure modes
- **Performance expectations**: Success criteria
- **Expected outputs**: Deliverables
- **AI prompt templates**: Structured prompt formats
- **Report sections**: Required documentation
