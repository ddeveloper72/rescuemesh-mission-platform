# ADR-0005: MeshStatic Before MeshCore

**Status:** Accepted

**Date:** 2026-05-30

**Decision Makers:** Core Development Team

---

## Context

The RescueMesh Mission Platform models mesh relay communications for GPS-denied environments where agents must cooperate to maintain connectivity. We must decide between:

1. Implementing real mesh networking protocols (MeshCore) from the start
2. Building static mesh visualization (MeshStatic) for MVP with future real mesh integration

Real mesh networking requires physical hardware, radio protocols, dynamic routing, and significant complexity. The platform follows a "simulation-first" philosophy.

---

## Decision

**We will implement MeshStatic (static mesh visualization) for the MVP, with MeshCore (real mesh networking) planned for future robotics integration phases.**

### MeshStatic (Current Implementation)

**Definition:** Static mesh visualization for demonstration and training

**Characteristics:**
- Predefined relay chains calculated in simulation
- Deterministic network health based on elapsed time
- No runtime topology changes (chains predetermined)
- Visualization only - no actual network protocols
- HTTP polling for state updates (not real mesh packets)

**Purpose:**
- Algorithm demonstration
- Operator training
- Failure scenario exploration
- AI model development
- Decision support simulation

**Implementation:**
- Backend simulates network state in `simulation.py`
- Frontend displays relay chains from JSON responses
- No actual radio protocols or dynamic routing
- Mesh health calculated from distance, obstacles, battery levels
- Relay chain breaks simulated based on failure scenarios

### MeshCore (Future Real-Time Extension)

**Definition:** Real mesh networking for physical hardware integration

**Characteristics:**
- Dynamic topology with runtime route discovery
- Actual mesh protocols (Batman-adv, 802.11s, LoRa mesh, etc.)
- Real packet routing through agent radios
- Link quality monitoring from physical signal strength
- Automatic rerouting on agent failure
- WebSocket streaming of live telemetry

**Future Integration:**
- ROS 2 bridge for real robotics
- MAVLink or similar protocols
- Physical radio hardware
- Safety-approved control systems

**Timeline:** Planned for 2028+ pending robotics integration and safety validation

---

## Consequences

### Positive Consequences of MeshStatic First

**Rapid Development:**
- No hardware required for core features
- Faster iteration without physical testing
- Simpler debugging and testing
- Reproducible scenarios

**Operator Training:**
- Training operators without expensive hardware
- Safe exploration of failure scenarios
- Repeatable training exercises
- No risk of real agent damage

**Algorithm Development:**
- Test mesh routing algorithms before hardware
- Explore relay placement strategies
- Model failure recovery tactics
- AI decision support development

**Cost Efficiency:**
- No radio hardware required for MVP
- Zero spectrum licensing concerns
- No physical test environments needed
- Cloud or local deployment equally viable

**Flexibility:**
- Easy scenario modification
- Instant replay and rewind
- Parameter tuning without re-flights
- Multi-scenario comparison

### Negative Consequences of MeshStatic First

**Not Real Networking:**
- Visualization only, no actual mesh protocols
- Cannot test real radio propagation
- No actual packet routing or collision handling
- Latency and bandwidth are simulated estimates

**Limited Realism:**
- Real mesh networks have unpredictable behavior
- Environmental factors not fully modeled
- Multi-path, fading, interference simplified
- Dynamic topology changes not represented

**Migration Complexity:**
- Future MeshCore integration requires significant backend changes
- WebSocket infrastructure needed for real-time
- ROS 2 bridge adds architectural complexity
- Safety validation required for physical hardware

**Operator Expectations:**
- Operators trained on MeshStatic may need retraining for MeshCore
- Real mesh networks behave differently from simulation
- Failure modes in real hardware may surprise operators

---

## Alternatives Considered

### Alternative 1: MeshCore from Day One

**Pros:**
- Production-ready networking from start
- Real-world testing possible immediately
- No migration effort later

**Cons:**
- Requires physical drone hardware
- Radio licensing and spectrum management
- Complex debugging (software + hardware + RF)
- Slower development velocity
- High cost for initial development
- Safety validation before any testing

**Rejection Reason:** Violates simulation-first principle; requires hardware MVP doesn't need.

### Alternative 2: Hybrid Approach (Both Modes)

**Pros:**
- Support both simulated and real operations
- Side-by-side comparison possible
- Gradual transition path

**Cons:**
- Dual implementation maintenance burden
- Code complexity from two networking stacks
- Testing matrix explosion
- Risk of divergence between modes

**Rejection Reason:** Premature complexity; MeshCore not needed until robotics integration phase.

### Alternative 3: Third-Party Mesh Simulation

**Pros:**
- Existing mesh simulators available (NS-3, OMNeT++)
- More realistic RF modeling
- Academic validation

**Cons:**
- Integration complexity
- Learning curve for team
- External dependency
- May not match mission scenarios
- Still not real hardware

**Rejection Reason:** Overkill for MVP needs; adds dependency without hardware integration benefits.

---

## Implementation Details

### MeshStatic Architecture

**Backend (Django):**
```python
# simulation.py calculates network state
network_state = {
    "base_signal_strength": 85,
    "mesh_health": 78,
    "relay_chain": ["base-station", "drone-a", "drone-b"],
    "packet_loss_percent": 5
}
```

**Frontend (TypeScript):**
```typescript
// Render relay chain visualization
renderRelayChain(relayChain: string[]) {
    // Draw lines connecting agents in relay chain
    // Show signal strength at each hop
    // Indicate weak links with color coding
}
```

### Future MeshCore Architecture

**Requirements:**
- WebSocket for real-time telemetry streaming
- ROS 2 bridge for robotics integration
- MAVLink protocol support (if using PX4/ArduPilot)
- Radio driver integration (physical hardware)
- Link quality monitoring from radios
- Dynamic route discovery implementation
- Safety-approved command interfaces

**Migration Path:**
1. Implement Django Channels for WebSockets
2. Add ROS 2 bridge architecture
3. Integrate radio drivers (when hardware available)
4. Implement real mesh protocol (Batman-adv, 802.11s, custom)
5. Add safety validation layer
6. Maintain MeshStatic mode for demos and testing

---

## Terminology Clarity

To avoid confusion between simulation and real networking:

**MeshStatic:**
- Static mesh visualization
- Predetermined relay chains
- Calculated network health
- Demo/training mode
- No actual networking protocols

**MeshCore:**
- Real mesh networking
- Dynamic topology
- Actual radio protocols
- Physical hardware integration
- Production-ready operations

**Current Status (May 2026):** MeshStatic implemented and active  
**MeshCore Status:** Planned for 2028+ (robotics integration phase)

---

## Documentation Requirements

All documentation must clearly distinguish:
- MeshStatic: Current implementation (simulation/visualization)
- MeshCore: Future real networking (physical hardware)

Frontend UI should indicate simulation mode to operators.

Safety documentation must emphasize:
- MeshStatic is demonstration/training only
- Not a real-time control system
- Human review required for real operations
- MeshCore will require safety validation before use

---

## Review and Transition Criteria

**MeshStatic to MeshCore transition triggers:**
- Physical hardware available and safety-approved
- ROS 2 integration requirements defined
- Safety validation process established
- WebSocket infrastructure implemented
- Team trained on robotics platforms

**MeshStatic maintenance during MeshCore development:**
- Keep MeshStatic mode available for demos
- Use MeshStatic for algorithm development
- Maintain MeshStatic for operator training
- Parallel testing against MeshCore when available

---

## Related Decisions

- [ADR-0002: Simulation-First Approach](ADR-0002-simulation-first.md)
- [ADR-0003: Agent-Based Domain Model](ADR-0003-agent-based-model.md)
- [ADR-0004: Generated Media Demo Mode](ADR-0004-generated-media-demo-mode.md)

---

## References

- Batman-adv: https://www.open-mesh.org/projects/batman-adv/wiki
- IEEE 802.11s: https://en.wikipedia.org/wiki/IEEE_802.11s
- LoRa Mesh: https://www.semtech.com/lora
- ROS 2 Documentation: https://docs.ros.org/
- MAVLink Protocol: https://mavlink.io/
- Django Channels: https://channels.readthedocs.io/

---

**Status:** Active  
**Review Date:** Q4 2027 (when robotics integration planning begins)
