# ADR-0003: Agent-Based Domain Model

## Status
Accepted

## Context
The system could be modeled in several ways:
1. **Drone-centric**: Focus on drones with other hardware as accessories
2. **Robot-centric**: Focus on ground robots with drones as special cases
3. **Agent-based**: Treat all participants as cooperating agents
4. **Service-oriented**: Focus on capabilities rather than hardware

We need a flexible model that supports diverse hardware and future expansion.

## Decision
Use an **agent-based domain model** where all mission participants are modeled as `Agent` entities.

### Definition of Agent

An `Agent` is any autonomous or semi-autonomous entity that participates in a mission:

- Drones (survey, detection, penetration)
- Ground robots
- Amphibious robots
- Static relay nodes
- Passive sensors
- Base stations
- AI analyst services
- (future) Human operators with wearable tech

### Definition of Asset

An `Asset` is a physical or logical component:

- Complete agents
- Attached sensors
- Dropped relay modules
- NFC recovery modules
- Black-box recorders
- Battery packs
- Sensor packages

### Rationale

**Why Agent-Based?**

1. **Flexibility**: Easy to add new hardware types
2. **Consistency**: Uniform API for all participants
3. **Cooperation**: Natural model for multi-agent coordination
4. **Extensibility**: AI services treated the same as hardware
5. **Future-Proof**: Supports swarm robotics, human-robot teaming

**Why NOT Drone-Only?**

- Limits thinking to aerial platforms
- Hard to add ground robots later
- Doesn't model relay nodes well
- Poor fit for sensor networks
- Excludes AI services

**Why NOT Service-Oriented?**

- Loses physical hardware context
- Harder to model state and location
- Less intuitive for operators
- Complicates failure modeling

### Agent Properties

All agents have:
- Unique ID
- Type (drone, robot, sensor, etc.)
- Current state
- Capabilities (sensors, actuators)
- Current location (if applicable)
- Battery level (if applicable)
- Current mission assignment

### Agent Types

```python
AGENT_TYPES = [
    'drone',
    'ground_robot',
    'amphibious_robot',
    'relay_node',
    'sensor',
    'base_station',
    'ai_analyst',
]
```

### Agent States

```python
STATE_CHOICES = [
    'planned',
    'available',
    'deployed',
    'active',
    'healthy',
    'degraded',
    'intermittent',
    'failed',
    'landed_relay',
    'abandoned',
    'recoverable',
    'recovered',
]
```

### State Transitions

All state changes are recorded as `AgentStateChange` events:

```python
class AgentStateChange:
    agent: Agent
    mission: Mission
    timestamp: datetime
    previous_state: str
    new_state: str
    reason: str
    confidence: float
    location: dict
```

## Consequences

### Positive
- Clean abstraction for diverse hardware
- Easy to add new agent types
- Natural fit for multi-agent missions
- AI services are first-class participants
- Good foundation for swarm coordination

### Negative
- More abstract than drone-specific model
- May feel overengineered for simple cases
- Need to document agent patterns

### Required Work
- Define agent interface clearly
- Document state machine
- Create agent behavior models
- Build visualization for agent types
- Implement agent coordination logic

## Implementation

**Core Models**
```python
class Agent(models.Model):
    agent_id: str
    name: str
    agent_type: str
    state: str
    current_mission: Mission
    specifications: dict
    battery_level: int
    location: dict

class AgentStateChange(models.Model):
    agent: Agent
    mission: Mission
    timestamp: datetime
    previous_state: str
    new_state: str
    reason: str
    confidence: float
    location: dict
```

**API Endpoints**
- `GET /api/v1/agents/` - List all agents
- `GET /api/v1/agents/{id}/` - Agent details
- `GET /api/v1/agents/{id}/state-changes/` - State history
- `POST /api/v1/agents/{id}/deploy/` - Deploy to mission
- `POST /api/v1/agents/{id}/state/` - Update state

**Frontend Visualization**
- Agent list with type icons
- State badges with colors
- Location on map
- Battery/health indicators
- State change timeline

## Future Extensions

**Swarm Coordination**
- Agent groups
- Coordinated actions
- Formation flying
- Load balancing

**Human-Robot Teaming**
- Human operators as agents
- Mixed autonomy levels
- Task allocation
- Shared situational awareness

**AI Services**
- Sensor fusion agent
- Path planning agent
- Detection analysis agent
- Report generation agent

## Examples

**Survey Drone**
```json
{
  "agent_id": "drone-a",
  "name": "Survey Drone Alpha",
  "agent_type": "drone",
  "state": "active",
  "specifications": {
    "sensors": ["lidar", "thermal", "rgb"],
    "max_speed": 15,
    "endurance_minutes": 45
  }
}
```

**Relay Node**
```json
{
  "agent_id": "relay-01",
  "name": "Static Relay Node 1",
  "agent_type": "relay_node",
  "state": "deployed",
  "specifications": {
    "radio_power": "high",
    "mesh_capable": true,
    "power_source": "wired"
  }
}
```

**AI Analyst**
```json
{
  "agent_id": "ai-thermal-analyst",
  "name": "Thermal Analysis Service",
  "agent_type": "ai_analyst",
  "state": "active",
  "specifications": {
    "model": "thermal-detection-v2",
    "inputs": ["thermal_frames"],
    "outputs": ["detections", "confidence"]
  }
}
```

## References
- Multi-agent systems literature
- ROS 2 agent patterns
- Swarm robotics architectures
- Human-robot interaction research

---
**Date**: 2026-05-29  
**Author**: RescueMesh Team  
**Supersedes**: N/A
