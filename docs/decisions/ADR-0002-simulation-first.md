# ADR-0002: Simulation-First Architecture

## Status
Accepted

## Context
The RescueMesh Mission Platform could be built in several ways:
1. Real-time drone control system
2. Hybrid (support both real and simulated)
3. Simulation-first with future hardware integration

We need to decide the MVP scope and architecture direction.

## Decision
Build a **simulation-first** mission dashboard that does NOT require real drone hardware for core features.

### Rationale

**Why Simulation-First?**

1. **Safety**: Developing with real drones is dangerous and expensive
2. **Reproducibility**: Simulated scenarios are deterministic and repeatable
3. **Failure Testing**: Can safely model dangerous failure scenarios
4. **Development Speed**: No hardware dependencies or field testing delays
5. **Demonstration**: Can show complex scenarios without physical setup
6. **Training**: Safe environment for operator training
7. **AI Development**: Generate consistent data for AI algorithm testing

**MVP Scope**
- Mission planning and setup
- Simulated agent behavior
- Event generation and timeline
- Detection simulation
- Failure modeling
- AI prompt generation
- Report generation

**NOT in MVP**
- Real-time drone command and control
- Physical autopilot integration
- Live video streaming from hardware
- Safety-critical flight control

### Simulation Capabilities

The platform will simulate:
- Agent movement and positioning
- Battery drain (realistic curves)
- Signal strength and dropouts
- Sensor readings (LiDAR, thermal, audio)
- Detection events (with confidence)
- Hardware degradation
- Intermittent failures
- Complete failures
- Tactical decisions (land as relay)
- AI analysis results

### Data Model Implications

All simulated data uses:
- Timestamps (ISO 8601)
- Source agent IDs
- Confidence values (0-1)
- Structured JSON payloads
- Optional simulation seeds for reproducibility

Example:
```json
{
  "event_type": "detection",
  "mission_id": "mission-demo-001",
  "agent_id": "drone-c",
  "timestamp": "2026-05-29T12:14:30Z",
  "detection_type": "voice_like_audio",
  "confidence": 0.58,
  "requires_human_review": true
}
```

### Future Hardware Integration

The architecture allows future real hardware integration:
- Agent models can represent real or simulated
- Telemetry format matches ROS 2 / MCAP patterns
- Mission events work for both modes
- Clear separation between simulation engine and data models

Integration points:
- ROS 2 bridge for real robotics data
- MCAP log replay for recorded missions
- WebSocket telemetry for live feeds
- Gazebo simulation for physics-accurate testing

## Trade-offs

### Advantages
- Safe development
- Rapid iteration
- Reproducible scenarios
- Lower cost
- Easier demonstration
- Better testing

### Disadvantages
- Simulation may not match reality
- No real-world validation in MVP
- Must model failure modes carefully
- Risk of overconfidence in simulation

### Mitigation
- Base simulations on real drone capabilities
- Consult with rescue professionals
- Include uncertainty in all outputs
- Clearly label as "simulation"
- Plan validation phase with real hardware
- Use conservative assumptions

## Consequences

### Positive
- Can demonstrate complex scenarios safely
- Reproducible testing and demos
- Faster development
- Lower barrier to entry
- Good foundation for AI training

### Negative
- Must eventually validate with real hardware
- Simulation accuracy depends on modeling quality
- May build features that don't work in reality

### Required Work
- Implement deterministic simulation engine
- Create realistic failure scenarios
- Model battery behavior
- Model signal propagation
- Generate sensor artifacts (noise, dropouts)
- Document simulation assumptions

## Implementation

**Simulation Engine** (Django backend)
- Mission event generator
- Agent behavior models
- Sensor simulation
- Failure injection
- Timeline generation

**Visualization** (Astro frontend)
- Mission playback
- Timeline replay
- Agent state display
- Detection rendering

**Data Fixtures**
- Sample missions
- Agent profiles
- Failure scenarios
- Use case templates

## Future Path

When ready for hardware integration:
1. Define hardware abstraction layer
2. Implement ROS 2 bridge
3. Add real/simulated mode flag
4. Validate simulations against real data
5. Implement safety checks
6. Comply with aviation regulations

## References
- [Gazebo Simulation](https://gazebosim.org/)
- [ROS 2 Documentation](https://docs.ros.org/)
- [MCAP](https://mcap.dev/)
- [PX4 SITL](https://docs.px4.io/main/en/simulation/)

---
**Date**: 2026-05-29  
**Author**: RescueMesh Team  
**Supersedes**: N/A
