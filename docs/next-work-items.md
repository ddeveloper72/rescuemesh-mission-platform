# Next Work Items

This document tracks current outstanding work items for the RescueMesh Mission Platform.

**Last updated:** May 30, 2026

---

## High Priority

### Route Realism and No Teleporting Agents

**Status:** Planned

**Description:**
Agents currently follow predefined routes but position interpolation needs refinement to prevent visual "teleporting" between waypoints.

**Tasks:**
- Smooth position interpolation between route segments
- Add acceleration/deceleration curves for realistic movement
- Implement pause/hover states at waypoints
- Add rotation/heading changes during path following
- Visual trail rendering showing complete path history

**Benefits:**
- More believable simulation visualization
- Better understanding of agent navigation behavior
- Improved operator training realism

---

### Mission Distance, Bearing, Depth/Elevation Refinements

**Status:** In Progress

**Description:**
Navigation intelligence is implemented but needs polish for production readiness.

**Tasks:**
- Add return path calculation (reverse route estimation)
- Implement nearest relay calculation with bearing
- Add contact path length through relay mesh
- Enhanced vertical profile visualization
- Slope and traversal risk calculations for path segments
- Communications risk assessment based on distance and obstructions

**Benefits:**
- Complete GPS-denied navigation intelligence
- Better operator situational awareness
- Tactical decision support for relay deployment

---

### Generated Media Polish

**Status:** Planned

**Description:**
Generated media system works but image/audio quality and variety need enhancement.

**Tasks:**
- Improve thermal image realism (gradient quality, noise patterns)
- Add more audio event variations (different knock patterns, voice characteristics)
- Better spectrogram generation with frequency detail
- Media metadata enhancement (timestamp, location, confidence)
- Add "last good frame" degradation effects
- Implement media quality indicators

**Benefits:**
- More convincing demo presentations
- Better AI analysis training data
- Improved operator interface realism

---

### Mission Escalation and Relay Reinforcement Polish

**Status:** Partially Implemented

**Description:**
Escalation logic exists but needs refinement and UI improvements.

**Tasks:**
- Refine escalation triggers (battery, network, detection thresholds)
- Add escalation history timeline
- Visual escalation level indicators in UI
- Recommended actions display for each escalation level
- Relay reinforcement animation/visualization
- De-escalation logic when conditions improve

**Benefits:**
- Better tactical situation awareness
- Clear operator guidance during mission changes
- Training for escalation decision-making

---

## Medium Priority

### Mission Report Export

**Status:** Planned

**Description:**
Generate comprehensive mission reports for after-action review and analysis.

**Tasks:**
- PDF report generation with mission summary
- JSON export for external analysis tools
- CSV export for spreadsheet analysis
- Include mission timeline, agent paths, detections, failures
- Embed key media artifacts (thermal images, audio events)
- Statistics summary (coverage %, detection count, battery consumption)
- AI analysis summary with confidence scores

**Benefits:**
- Post-mission analysis capability
- Training material generation
- Algorithm performance comparison
- Regulatory compliance documentation

---

### 3D Visualization Foundation

**Status:** Research Phase

**Description:**
Plan and prototype 3D visualization capabilities for future implementation.

**Tasks:**
- Technology evaluation (Three.js vs CesiumJS vs Babylon.js)
- Point cloud rendering prototype
- 3D agent positioning and movement
- Camera controls (orbit, pan, zoom)
- Terrain mesh generation from sector data
- Performance benchmarking with large datasets

**Benefits:**
- Enhanced spatial understanding
- Better LiDAR data visualization
- Improved operator training immersion
- Foundation for future AR/VR interfaces

---

## Future Enhancements

### Advanced Simulation Controls

- Mission scenario editor UI
- Configurable failure injection
- Custom agent configurations
- Dynamic terrain generation
- Multi-mission coordination

### Real-Time Infrastructure

- WebSocket streaming migration from HTTP polling
- Django Channels integration
- Live telemetry push notifications
- Collaborative operator features
- Real-time map updates

### Physical Hardware Integration

- ROS 2 bridge architecture
- MCAP log import/replay
- Gazebo simulation bridge
- PX4/ArduPilot integration
- Safety-approved control interfaces

---

## Completed Recent Work

For reference, recently completed major features:

- ✅ Live simulation state calculation
- ✅ Tactical maps with SVG rendering
- ✅ Agent detail modals with 3D positioning
- ✅ Navigation model with compass bearing
- ✅ Terrain reconstruction with progressive reveal
- ✅ Generated media system (images, audio, spectrograms)
- ✅ Audio detections panel
- ✅ Mission escalation modeling
- ✅ ISO 8601 time formatting
- ✅ Clickable agents and detections

---

## Contributing

If you'd like to work on any of these items:

1. Open a GitHub issue referencing the work item
2. Discuss approach and implementation details
3. Create a feature branch
4. Submit a pull request with tests and documentation

---

**Note:** Priorities may shift based on user feedback, demonstration requirements, and strategic goals. Check this document regularly for updates.
