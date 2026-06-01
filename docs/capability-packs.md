# RescueMesh Capability Packs

## Overview

Capability packs are modular sensor and equipment bundles that enhance mission simulation realism and operator decision-making. Each pack models real-world hardware capabilities, constraints, and trade-offs.

---

## 1. Low-Light / Night-Vision / Illumination Pack

### Purpose
Model visual sensing in darkness, low-light, or obscured environments (caves, night operations, smoke, dust, flooded structures).

### Equipment Included
- **Low-light RGB camera**: Sensitive visible-light camera
- **Infrared-assisted view**: NIR illumination + camera
- **Thermal camera**: Long-wave IR (LWIR) sensing
- **Visible spotlight**: White LED illumination
- **IR illuminator**: Near-infrared (850nm/940nm) illumination
- **Strobe/beacon light**: Flashing marker for agent location
- **Photo-light mode**: High-intensity still capture
- **Video-light mode**: Continuous moderate illumination

### Simulation Parameters
```json
{
  "lighting_state": {
    "current_mode": "low_light_rgb|ir_assisted|thermal|visible_spotlight|ir_only",
    "light_active": true,
    "light_intensity_percent": 75,
    "battery_cost_percent_per_second": 0.08,
    "image_confidence": 0.85,
    "confidence_penalty_factors": {
      "dust": 0.35,
      "smoke": 0.45,
      "moisture": 0.25,
      "reflection_glare": 0.30
    }
  }
}
```

### Operator Controls
- **Light On / Light Off**: Toggle active illumination
- **IR Mode**: Switch to infrared-assisted view
- **Thermal Mode**: Switch to thermal camera
- **Low-Light RGB**: Passive ambient light capture
- **Capture Still**: High-quality photo with flash/boost
- **Strobe Beacon**: Emergency location marker

### Simulation Logic
- Darkness reduces visible camera confidence to 0.1-0.3
- Active visible light restores confidence to 0.7-0.9 but costs 0.05-0.1% battery/second
- IR illumination provides 0.6-0.8 confidence at lower battery cost (0.03-0.06% battery/second)
- Thermal view remains effective (0.7-0.9 confidence) regardless of ambient light
- Water/metallic surfaces cause reflection glare penalty when using active light
- Dust/smoke reduces visible/IR confidence more than thermal
- Last-good-frame shown when signal drops during illuminated capture

### Media Generated
- `cave_low_light_frame_sector_passage1_12m45s.jpg`
- `ir_assisted_narrow_squeeze_08m30s.jpg`
- `thermal_survivor_candidate_chamber2_15m20s.jpg`
- `underwater_murky_spotlight_on_09m15s.jpg`
- `industrial_hotspot_thermal_equipment_room_04m50s.jpg`
- `last_good_frame_before_signal_loss_11m35s.jpg`

### UI Display
```
┌─ Lighting & Visual Mode ────────────────┐
│ Current Mode: IR-Assisted                │
│ Light Status: ● ON (IR Illuminator)      │
│ Battery Cost: 0.04%/sec                  │
│ Image Confidence: 68% (dust penalty)     │
│                                          │
│ [Light Off] [Thermal] [Visible]          │
│ [Capture Still] [Strobe Beacon]          │
└──────────────────────────────────────────┘
```

---

## 2. Two-Way Talkback / Survivor Communication Pack

### Purpose
Simulate two-way audio communication from mission control through deployed agents to possible survivor locations.

### Equipment Included
- **Speaker module**: Directional or omnidirectional speaker on drone/relay/probe
- **Microphone array**: Ambient audio capture for response detection
- **Message playback**: Pre-recorded or operator voice messages
- **Response listening window**: Post-message audio monitoring period

### Simulation Parameters
```json
{
  "talkback_capability": {
    "talkback_available": true,
    "speaker_available": true,
    "microphone_available": true,
    "selected_agent_id": "drone-a",
    "route_to_survivor_sector": "chamber-2",
    "audio_link_quality": 0.72,
    "operator_message": "If you can hear me, tap three times.",
    "message_sent_at_seconds": 185.5,
    "response_listening_window_seconds": 30,
    "survivor_response_detected": true,
    "response_confidence": 0.68,
    "transcript_placeholder": "[Tapping detected: 3 distinct impacts]"
  }
}
```

### Message Presets
- "If you can hear me, tap three times."
- "Stay calm. Help is on the way."
- "Can you move or respond?"
- "We are trying to maintain contact."
- "Emergency services are approaching your location."
- "Do not move if you are injured."

### Operator Controls
- **Select Agent**: Choose drone/relay with speaker/mic
- **Select Message**: Preset or custom message
- **Push to Talk** (simulation): Send message to selected agent
- **Listen for Response**: Enable 30-second listening window

### Simulation Logic
- Talkback only available through agents with speaker/microphone capability
- Audio link quality depends on signal strength and mesh health
- Message may be: delivered (100%), delayed (partial), degraded (noisy), failed (no link)
- Response detection simulated based on scenario events
- Survivor response may be: tapping, voice, movement noise, or no response
- Human review always required before concluding survivor contact

### Media Generated
- `talkback_message_sent_chamber2_08m15s_audio_spectrogram.png`
- `response_tapping_detected_08m47s_waveform.png`

### UI Display
```
┌─ Talkback Communication ────────────────────────┐
│ Available Agents: ▼ Cave Scout Drone (drone-a)  │
│ Location: Chamber 2 (-42m depth)                │
│ Audio Link Quality: ████████░░ 72%              │
│                                                  │
│ Message: ▼ Tap three times if you hear me       │
│ [Custom Message...]                             │
│                                                  │
│ [● Push to Talk]  [Listen for Response]         │
│                                                  │
│ Status: Message sent at 08:15                   │
│ Response: ✓ Tapping detected at 08:47           │
│ Confidence: 68% (human review required)         │
│                                                  │
│ ⚠ Simulation only. Not real survivor contact.   │
└──────────────────────────────────────────────────┘
```

### Safety Wording
All talkback features must include:
- "Simulation only - not real survivor contact"
- "Human review required"
- "Authorized rescue communications only"
- No claims of real telephony or device control

---

## 3. Seismic / Acoustic Ground Sensor Kit

### Purpose
Deploy ground-contact sensors to detect tapping, knocking, structural vibration, and movement in collapsed buildings, caves, or confined spaces.

### Equipment Included
- **Seismic sensor node**: Ground-contact vibration sensor
- **Acoustic ground sensor**: Contact microphone for structure-borne sound
- **Knock/tapping classifier**: Pattern recognition for human-generated signals
- **Multi-sensor triangulation**: Correlate detections across multiple nodes
- **Background noise monitor**: Ambient vibration/noise level

### Sensor States
- `undeployed`: Sensor carried by agent or in inventory
- `deployed`: Sensor placed at location
- `listening`: Active monitoring
- `noise_contaminated`: High background interference
- `signal_detected`: Possible human cue detected
- `triangulation_ready`: Multiple sensors correlating
- `failed`: Sensor malfunction
- `recoverable`: Can be retrieved

### Simulation Parameters
```json
{
  "seismic_sensor": {
    "sensor_id": "seismic-node-1",
    "state": "listening",
    "location": "chamber-1",
    "position": {"x_m": 12.5, "y_m": 8.3, "z_m": -15.0},
    "deployed_at_seconds": 145,
    "background_noise_level": 0.35,
    "detection_threshold": 0.50,
    "detections": [
      {
        "detected_at_seconds": 220,
        "type": "tapping",
        "confidence": 0.72,
        "frequency_hz": 4.5,
        "pattern": "3 distinct impacts, 1.2s intervals",
        "human_cue_probability": 0.78,
        "classification": "possible_human_tapping"
      }
    ],
    "triangulation_available": false,
    "recommended_action": "Deploy second sensor to improve localisation"
  }
}
```

### Simulation Logic
- Seismic sensors detect ground vibration and structure-borne sound
- Tapping/knocking classified by frequency, pattern, regularity
- Human cues: rhythmic tapping, intentional patterns (e.g., 3 knocks)
- Structural noise: random vibration, settling, water flow, mechanical hum
- Background noise reduces detection confidence
- Multiple sensors enable triangulation and false-positive reduction
- Operator can request "quiet period" to reduce contamination

### Media Generated
- `seismic_waveform_tapping_detected_chamber1_05m40s.png`
- `acoustic_spectrogram_knock_pattern_06m15s.png`
- `multi_sensor_correlation_triangulation_07m30s.png`

### UI Display
```
┌─ Seismic / Acoustic Ground Monitoring ──────────┐
│ Deployed Sensors: 2 active, 0 failed            │
│                                                  │
│ ● Seismic Node 1 - Chamber 1 (-15m)             │
│   Status: Listening                             │
│   Background Noise: ████░░░░░░ 35%              │
│   Detection: ✓ Tapping (3 impacts, 1.2s)       │
│   Confidence: 72% - Possible human cue          │
│   [View Waveform]                               │
│                                                  │
│ ● Seismic Node 2 - Chamber 2 (-18m)             │
│   Status: Listening                             │
│   Background Noise: ██████░░░░ 58%              │
│   Detection: Structural settling                │
│                                                  │
│ Recommendation: Deploy 3rd sensor for           │
│ triangulation of Chamber 1 source               │
│                                                  │
│ [Request Quiet Period] [Deploy Sensor]          │
└──────────────────────────────────────────────────┘
```

---

## 4. Water / Hydrophone Acoustic Kit

### Purpose
Monitor underwater acoustic signatures in flooded structures, underground rivers, submerged compartments, and water-filled caves.

### Equipment Included
- **Hydrophone**: Underwater acoustic sensor
- **Water-flow acoustic sensor**: Detect rivers, springs, leaks
- **Underwater knock/ping detector**: Submerged survivor signaling
- **Leak/pump noise detector**: Mechanical water sounds
- **Turbulence/cavitation monitor**: Water movement classification

### Sensor States
- `undeployed`: Sensor in agent payload
- `deployed_surface`: Floating at water surface
- `deployed_submerged`: Fully underwater
- `listening`: Active monitoring
- `turbulence_contaminated`: High water noise
- `signal_detected`: Acoustic signature detected
- `failed`: Sensor malfunction
- `recoverable`: Can be retrieved

### Simulation Parameters
```json
{
  "hydrophone": {
    "sensor_id": "hydrophone-1",
    "state": "deployed_submerged",
    "location": "flooded_corridor_b",
    "position": {"x_m": 8.2, "y_m": 15.5, "z_m": -6.5},
    "water_depth_m": 6.5,
    "deployed_at_seconds": 180,
    "detections": [
      {
        "detected_at_seconds": 245,
        "type": "underground_river",
        "confidence": 0.85,
        "frequency_range": "50-1200 Hz",
        "flow_direction_estimate": "north-northeast",
        "intensity": "moderate",
        "classification": "natural_water_flow"
      },
      {
        "detected_at_seconds": 290,
        "type": "mechanical_pump",
        "confidence": 0.92,
        "frequency_range": "60 Hz + harmonics",
        "classification": "pump_or_machinery"
      }
    ],
    "turbulence_level": 0.42,
    "recommended_action": "Monitor for underwater tapping/knocking"
  }
}
```

### Simulation Logic
- Hydrophones detect underwater sound propagation
- Water acoustic signatures: rivers, springs, leaks, pumps, tapping, impacts
- Turbulence and cavitation reduce detection confidence
- Flow direction estimated from spatial audio (with multiple hydrophones)
- Underwater tapping/knocking indicates possible survivor
- Mechanical sounds (pumps, generators) identified by steady frequency
- Human review required for survivor-related detections

### Media Generated
- `hydrophone_spectrogram_underground_river_08m30s.png`
- `underwater_knock_detection_waveform_12m15s.png`
- `pump_noise_signature_05m45s.png`

### UI Display
```
┌─ Water / Hydrophone Acoustic Monitoring ────────┐
│ Deployed Hydrophones: 1 active                  │
│                                                  │
│ ● Hydrophone 1 - Flooded Corridor B (-6.5m)     │
│   Status: Listening                             │
│   Water Depth: 6.5m                             │
│   Turbulence: ████░░░░░░ 42%                    │
│                                                  │
│   Detections:                                   │
│   ✓ Underground River (85% confidence)          │
│     Flow Direction: North-Northeast             │
│     [View Spectrogram]                          │
│                                                  │
│   ✓ Mechanical Pump (92% confidence)            │
│     60 Hz + harmonics                           │
│     [View Signature]                            │
│                                                  │
│ Recommendation: Continue monitoring for         │
│ underwater tapping or knocking                  │
│                                                  │
│ [Deploy Hydrophone] [Request Analysis]          │
└──────────────────────────────────────────────────┘
```

---

## 5. Improved Generated Media System

### Purpose
Replace generic blurry placeholders with context-aware imagery that reflects mission conditions, sensor modes, lighting state, and environmental factors.

### Media Metadata Structure
```json
{
  "media_id": "thermal_chamber2_survivor_candidate_15m20s",
  "media_type": "thermal_image",
  "agent_id": "drone-a",
  "sensor_type": "thermal_camera",
  "location": "Chamber 2",
  "position": {"x_m": 18.5, "y_m": 12.3, "z_m": -22.0},
  "mission_time_seconds": 920,
  "timestamp": "15:20",
  "lighting_mode": "thermal_only",
  "light_active": false,
  "signal_quality": 0.78,
  "confidence": 0.82,
  "confidence_penalty_factors": {
    "dust": 0.15,
    "distance": 0.10
  },
  "human_review_flag": true,
  "classification": "thermal_anomaly_survivor_candidate",
  "description": "Thermal signature consistent with human heat pattern",
  "generated_not_real": true,
  "generation_context": {
    "use_case": "cave_rescue",
    "sector_type": "chamber",
    "environmental_conditions": ["low_light", "dust", "cool_ambient"],
    "detection_context": "survivor_search"
  }
}
```

### Media Types by Context

#### Cave Rescue
- `cave_low_light_entrance.jpg`: Ambient light, high confidence
- `cave_ir_assisted_passage.jpg`: IR illumination, moderate dust
- `cave_thermal_chamber_anomaly.jpg`: Thermal detection, survivor candidate
- `cave_last_good_frame_squeeze.jpg`: Signal loss during narrow passage

#### Collapsed Building
- `collapsed_thermal_void_hotspot.jpg`: Thermal anomaly in void space
- `collapsed_dust_obscured_visible.jpg`: Heavy dust penalty, low confidence
- `collapsed_ir_structural_detail.jpg`: IR mode, metallic/concrete detail

#### Flooded Structure
- `flooded_murky_spotlight_on.jpg`: Visible light, water turbidity
- `flooded_underwater_sonar_image.jpg`: Acoustic imaging
- `flooded_last_frame_before_submersion.jpg`: Transition to underwater

#### Industrial Inspection
- `industrial_thermal_hotspot_equipment.jpg`: Thermal anomaly, machinery
- `industrial_gas_leak_ir_signature.jpg`: IR detection of gas plume
- `industrial_visible_close_inspection.jpg`: High-detail visible inspection

#### Seismic / Acoustic
- `seismic_waveform_tapping_3_knocks.png`: Waveform with clear pattern
- `acoustic_spectrogram_voice_frequency.png`: Audio frequency analysis
- `hydrophone_underground_river_signature.png`: Water flow spectrum

### Generation Rules
1. **Use Case Context**: Media appearance varies by mission type
2. **Sector Type**: Chamber vs passage vs squeeze vs void space
3. **Lighting Mode**: Low-light, IR, thermal, visible spotlight, last-good-frame
4. **Environmental Factors**: Dust, smoke, moisture, water turbidity
5. **Signal Quality**: High quality vs degraded vs last-good-frame
6. **Detection Context**: Survivor search, hazard inspection, mapping, equipment fault
7. **Human Review Flag**: Marks media requiring operator attention
8. **Generated Indicator**: Always labeled "Generated for simulation"

### Media File Naming Convention
```
{sensor_mode}_{use_case}_{context}_{location}_{timestamp}.{ext}

Examples:
- thermal_cave_survivor_chamber2_15m20s.jpg
- ir_industrial_hotspot_equipment_04m50s.jpg
- visible_collapsed_void_dust_12m35s.jpg
- hydrophone_flooded_river_corridor_08m30s.png
- seismic_waveform_tapping_chamber1_05m40s.png
- last_good_frame_squeeze1_signal_loss_11m35s.jpg
```

---

## 6. Mission Profile Capability Assignments

### Collapsed Building Search
**Priority**: Life safety, survivor location
**Capability Packs**:
- ✓ Low-Light / Night-Vision / Illumination (thermal priority)
- ✓ Talkback / Survivor Communication
- ✓ Seismic / Acoustic Ground Sensors (primary detection method)
- ○ Hydrophone (only if water present)
**Sensors**: Thermal, IR, visible spotlight, seismic nodes, speaker/mic, CO₂/O₂, dust monitor

### Cave Rescue
**Priority**: Mapping, survivor location, GPS-denied navigation
**Capability Packs**:
- ✓ Low-Light / Night-Vision / Illumination (IR + visible priority)
- ✓ Talkback / Survivor Communication
- ✓ Seismic / Acoustic Ground Sensors
- ✓ Hydrophone (underground rivers/springs)
**Sensors**: LiDAR, IR camera, thermal, seismic nodes, hydrophone, speaker/mic, relay chain

### Flooded Structure
**Priority**: Underwater navigation, amphibious operation, obstruction mapping
**Capability Packs**:
- ✓ Low-Light / Night-Vision / Illumination (underwater spotlight priority)
- ✓ Talkback (above waterline only)
- ○ Seismic (limited use)
- ✓ Hydrophone (primary underwater detection)
**Sensors**: Sonar, underwater camera, hydrophone, turbidity sensor, pressure sensor, IR (above waterline)

### Industrial Inspection
**Priority**: Hazard detection, equipment fault inspection, confined space safety
**Capability Packs**:
- ✓ Low-Light / Night-Vision / Illumination (thermal + IR priority)
- ✓ Talkback (confined space communication)
- ✓ Seismic (vibration/structural monitoring)
- ○ Hydrophone (leak detection if applicable)
**Sensors**: Thermal, gas sensors, vibration monitor, IR camera, visible spotlight

### Archaeological Exploration
**Priority**: Non-destructive mapping, artifact preservation, humidity control
**Capability Packs**:
- ✓ Low-Light / Night-Vision / Illumination (low-power IR priority, no turbulence)
- ○ Talkback (not applicable)
- ○ Seismic (avoid vibration)
- ○ Hydrophone (only if underground water)
**Sensors**: LiDAR, low-light RGB, IR (non-heating), humidity/CO₂/O₂, low-turbulence flight mode

---

## 7. Integration with Existing Systems

### Backend Integration
Capability packs extend existing models:
- `ScenarioEvent.event_data`: Add lighting state, sensor readings, talkback messages
- `SensorPackageTemplate`: Add new sensor types (seismic, hydrophone, speaker/mic)
- Scenario engine: Extract capability pack data from events

### Frontend Integration
New React island components:
- `LightingControlPanel.tsx`: Display mode and controls
- `TalkbackPanel.tsx`: Message sending and response monitoring
- `SeismicMonitoringPanel.tsx`: Ground sensor dashboard
- `HydrophonePanel.tsx`: Water acoustic monitoring
- `MediaFeedsPanel.tsx` (enhanced): Context-aware media with metadata

### Scenario JSON Format
New event types:
```json
{
  "event_type": "lighting_mode_change",
  "trigger_at_seconds": 120,
  "agent_id": "drone-a",
  "event_data": {
    "previous_mode": "low_light_rgb",
    "new_mode": "ir_assisted",
    "reason": "dust_reducing_visible_confidence",
    "battery_impact": 0.04
  }
}
```

```json
{
  "event_type": "seismic_detection",
  "trigger_at_seconds": 220,
  "sector_id": "chamber-1",
  "event_data": {
    "sensor_id": "seismic-node-1",
    "type": "tapping",
    "pattern": "3 distinct impacts, 1.2s intervals",
    "confidence": 0.72,
    "human_cue_probability": 0.78,
    "requires_human_review": true
  }
}
```

```json
{
  "event_type": "talkback_message_sent",
  "trigger_at_seconds": 185,
  "agent_id": "drone-a",
  "event_data": {
    "message": "If you can hear me, tap three times.",
    "audio_link_quality": 0.72,
    "delivery_status": "delivered",
    "response_expected": true,
    "response_window_seconds": 30
  }
}
```

```json
{
  "event_type": "talkback_response_detected",
  "trigger_at_seconds": 198,
  "sector_id": "chamber-2",
  "event_data": {
    "original_message_at": 185,
    "response_type": "tapping",
    "tap_count": 3,
    "confidence": 0.68,
    "requires_human_review": true,
    "transcript": "[Tapping detected: 3 distinct impacts]"
  }
}
```

```json
{
  "event_type": "hydrophone_detection",
  "trigger_at_seconds": 245,
  "sector_id": "flooded_corridor_b",
  "event_data": {
    "sensor_id": "hydrophone-1",
    "detection_type": "underground_river",
    "confidence": 0.85,
    "frequency_range": "50-1200 Hz",
    "flow_direction": "north-northeast",
    "intensity": "moderate"
  }
}
```

---

## 8. Safety and Simulation-First Principles

All capability packs must:
- ✓ Label all features as "Simulation only"
- ✓ Never claim real drone control
- ✓ Never claim real survivor contact
- ✓ Require human review for life-safety decisions
- ✓ Use "authorized rescue communications" language for talkback
- ✓ Mark all media as "Generated for simulation"
- ✓ Avoid autonomous command execution

Talkback wording requirements:
- "Via deployed agent speaker/microphone"
- "Simulated for demonstration"
- "Human review required"
- "Not real telephony or device control"

---

## 9. Acceptance Criteria

### Backend
- ✓ Scenario engine supports lighting states
- ✓ Scenario engine supports seismic sensor events
- ✓ Scenario engine supports hydrophone events
- ✓ Scenario engine supports talkback events
- ✓ Media metadata includes full context (mode, lighting, confidence, penalties)
- ✓ New event types extract correctly from JSON scenarios

### Frontend
- ✓ LightingControlPanel shows mode, battery cost, confidence
- ✓ TalkbackPanel includes message presets and simulation warning
- ✓ SeismicMonitoringPanel shows deployed sensors and detections
- ✓ HydrophonePanel shows water acoustic signatures
- ✓ MediaFeedsPanel displays context-aware imagery with metadata
- ✓ Mission layout reorganized for operator workflow

### Scenarios
- ✓ Collapsed building includes seismic sensors and talkback
- ✓ Cave rescue includes lighting modes, seismic, hydrophone, talkback
- ✓ Flooded structure includes underwater lighting and hydrophone
- ✓ Industrial inspection includes lighting and vibration monitoring
- ✓ Archaeological exploration includes non-invasive lighting modes

### Documentation
- ✓ docs/capability-packs.md created
- ✓ README updated with capability packs overview
- ✓ docs/architecture.md updated with capability pack integration
- ✓ docs/use-cases.md updated with capability assignments

---

## Next Implementation Steps

1. Extend backend scenario engine to extract capability pack events
2. Create React island components for each capability panel
3. Update scenario JSON files with lighting, sensor, talkback events
4. Reorganize mission page UI layout
5. Generate context-aware media metadata
6. Test all scenarios with new capability features
7. Update documentation

---

**Document Version**: 1.0
**Last Updated**: June 1, 2026
**Status**: Design Complete, Ready for Implementation
