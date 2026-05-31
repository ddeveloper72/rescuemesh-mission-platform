# Interactive Mission Simulator Architecture

**Date**: May 31, 2026  
**Status**: Design Phase  
**Impact**: Transforms pre-scripted scenario playback → interactive mission control

---

## 🎯 Mission Modes

### **Mode 1: Automated AI-Optimized**
- User selects mission objective and initial constraints
- AI selects hardware from inventory based on terrain/objective
- AI automatically deploys relays when signal degrades
- AI replaces failed agents to maintain coverage
- AI optimizes for: survivor detection, terrain coverage, equipment preservation
- User observes in real-time with explanation tooltips
- **Outcome**: Demonstrates "optimal" AI-driven rescue strategy

### **Mode 2: Manual Control**
- User manually selects each drone/relay from inventory
- User chooses deployment timing and destination
- App shows AI recommendations but user decides
- User balances risk vs. reward (send expensive thermal drone vs. cheap relay?)
- **Outcome**: Training simulation, "what-if" scenarios, operator skill building

### **Mode 3: Hybrid**
- AI handles routine tasks (relay placement)
- User makes critical decisions (send rescue team vs. more drones?)
- AI provides confidence levels on recommendations
- **Outcome**: Realistic operational model

---

## 🗄️ Database Architecture

### **New Models Needed**

```python
# backend/apps/missions/models.py

class HardwareInventory(models.Model):
    """Available hardware that can be deployed"""
    inventory_id = models.CharField(max_length=50, unique=True)
    hardware_type = models.CharField(max_length=50)  # drone, relay, sensor_package, ground_robot
    model_name = models.CharField(max_length=100)  # "Lightweight Scout", "Heavy Mapper", "Static Relay"
    
    # Capabilities
    max_battery_minutes = models.IntegerField()
    sensors = models.JSONField()  # ["lidar", "thermal", "audio"]
    movement_capability = models.CharField(max_length=50)  # aerial, ground, amphibious, static
    signal_range_m = models.FloatField()
    
    # Costs/Constraints
    deployment_cost = models.IntegerField()  # Arbitrary "mission points" for balancing
    recovery_difficulty = models.CharField(max_length=50)  # easy, moderate, difficult, sacrificial
    
    # Availability
    quantity_available = models.IntegerField()
    quantity_deployed = models.IntegerField(default=0)
    quantity_lost = models.IntegerField(default=0)
    
    # Failure profile
    base_failure_profile = models.ForeignKey('FailureProfile', null=True, blank=True)


class FailureProfile(models.Model):
    """Customizable failure/degradation scenarios"""
    profile_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Trigger conditions
    trigger_type = models.CharField(max_length=50)  # time_based, sector_based, depth_based, random
    trigger_params = models.JSONField()  # {"after_minutes": 10} or {"sector_id": "tight-squeeze"}
    
    # Effects
    affected_systems = models.JSONField()  # ["battery", "lidar", "radio"]
    severity = models.CharField(max_length=20)  # minor, moderate, severe, critical
    progression_curve = models.CharField(max_length=20)  # linear, exponential, sudden
    
    # Outcomes
    effect_modifiers = models.JSONField()  # {"battery_drain_multiplier": 2.5, "lidar_noise": 0.4}
    mission_impact = models.TextField()  # Human-readable explanation


class UserDeployment(models.Model):
    """Records user/AI decisions to deploy hardware mid-mission"""
    mission = models.ForeignKey('Mission')
    deployment_timestamp = models.DateTimeField(auto_now_add=True)
    mission_time_seconds = models.IntegerField()  # When in mission this was deployed
    
    # What was deployed
    hardware = models.ForeignKey('HardwareInventory')
    agent_id = models.CharField(max_length=50)  # Generated ID for this specific deployment
    agent_name = models.CharField(max_length=100)
    
    # Where/How
    deployment_sector = models.ForeignKey('TerrainSector')
    deployment_reason = models.TextField()  # "Signal chain broken" or user's reason
    deployed_by = models.CharField(max_length=20)  # 'ai' or 'user'
    
    # Assignment
    assigned_route = models.ForeignKey('AgentRoute', null=True)  # Pre-planned path
    mission_objective = models.CharField(max_length=100)  # "relay", "map_sector", "detect_survivor"


class AIRecommendation(models.Model):
    """AI-generated suggestions for user review"""
    mission = models.ForeignKey('Mission')
    recommendation_timestamp = models.DateTimeField(auto_now_add=True)
    mission_time_seconds = models.IntegerField()
    
    # Recommendation details
    recommendation_type = models.CharField(max_length=50)  # deploy_relay, replace_failed_agent, abort_mission
    priority = models.CharField(max_length=20)  # low, medium, high, critical
    confidence = models.FloatField()  # 0-1
    
    # Content
    title = models.CharField(max_length=200)  # "Deploy relay at Junction Alpha"
    reasoning = models.TextField()  # "Signal strength to Cave Scout dropped to 15%..."
    suggested_action = models.JSONField()  # {"hardware_id": "relay-static-01", "sector": "junction-alpha"}
    
    # User response
    user_decision = models.CharField(max_length=20, null=True)  # accepted, rejected, deferred
    user_decision_time = models.DateTimeField(null=True)
    actual_outcome = models.TextField(null=True)  # What happened after decision


class MissionOutcome(models.Model):
    """Final mission results for comparison/learning"""
    mission = models.ForeignKey('Mission')
    completion_timestamp = models.DateTimeField(auto_now_add=True)
    
    # Objectives
    primary_objective_achieved = models.BooleanField()  # Survivor found?
    secondary_objectives = models.JSONField()  # {"terrain_mapped": true, "safe_route_found": true}
    
    # Costs
    total_agents_deployed = models.IntegerField()
    agents_sacrificed = models.IntegerField()
    agents_recovered = models.IntegerField()
    total_deployment_cost = models.IntegerField()
    
    # Performance
    mission_duration_minutes = models.IntegerField()
    terrain_coverage_percent = models.FloatField()
    detection_confidence = models.FloatField(null=True)
    
    # Classification
    outcome_classification = models.CharField(max_length=50)  # success_efficient, success_costly, partial_success, failure
    lessons_learned = models.TextField()
    ai_analysis = models.TextField()  # What could have been done better
```

---

## 🤖 AI Recommendation Engine

### **Decision Points Where AI Can Help**

```python
# backend/apps/missions/services/ai_advisor.py

class MissionAdvisor:
    """AI recommendation engine for automated/hybrid missions"""
    
    def analyze_mission_state(self, mission_state) -> List[Recommendation]:
        """Generate recommendations based on current state"""
        recommendations = []
        
        # Check signal chain integrity
        if self._signal_chain_weak(mission_state):
            recommendations.append(
                Recommendation(
                    type="deploy_relay",
                    priority="high",
                    confidence=0.85,
                    title="Signal chain compromised",
                    reasoning="Cave Scout signal dropped to 15%. Deploy relay at Junction Alpha to maintain connection.",
                    suggested_action={
                        "hardware": "relay-static-01",
                        "sector": "junction-alpha",
                        "estimated_improvement": "Signal strength 15% → 85%"
                    }
                )
            )
        
        # Check battery levels
        if self._battery_critical(mission_state):
            recommendations.append(
                Recommendation(
                    type="replace_agent",
                    priority="medium",
                    confidence=0.72,
                    title="Replace degraded mapper",
                    reasoning="Cave Mapper battery at 18%. Mission coverage only 45%. Deploy fresh mapper to complete terrain survey.",
                    suggested_action={
                        "hardware": "drone-mapper-02",
                        "sector": "junction-alpha",  # Meet degraded agent here
                        "mission": "Continue mapping northern passages"
                    }
                )
            )
        
        # Check detection quality
        if self._detection_needs_verification(mission_state):
            recommendations.append(
                Recommendation(
                    type="deploy_specialist",
                    priority="critical",
                    confidence=0.91,
                    title="Verify audio detection",
                    reasoning="Voice-like audio detected at Tight Squeeze (confidence: 62%). Deploy thermal-audio specialist for confirmation.",
                    suggested_action={
                        "hardware": "drone-thermal-audio-01",
                        "sector": "tight-squeeze",
                        "mission": "Confirm survivor presence"
                    }
                )
            )
        
        return recommendations
    
    def select_optimal_hardware(self, mission_objective, terrain_profile, available_inventory):
        """AI selects best hardware for automated mode"""
        # Score each hardware option based on:
        # - Sensor match to objective (thermal for survivor search)
        # - Movement capability match to terrain (amphibious for flooded)
        # - Battery/range adequate for mission
        # - Cost vs. benefit ratio
        pass
    
    def generate_deployment_plan(self, mission_scenario, inventory):
        """Full automated mission plan"""
        # Returns: {
        #   "initial_deployment": [drone-a, drone-b, relay-1],
        #   "contingency_deployments": [
        #     {"trigger": "signal < 20%", "action": "deploy relay-2 at junction-alpha"},
        #     {"trigger": "battery < 15%", "action": "replace with drone-c"}
        #   ],
        #   "expected_outcome": "85% chance of survivor detection, 3-4 agents sacrificed"
        # }
        pass
```

### **Automatable Decisions**

| Decision | Can AI Handle? | Requires User? | Reasoning |
|----------|----------------|----------------|-----------|
| Deploy relay when signal < 20% | ✅ Yes | Optional override | Clear threshold |
| Replace failed mapper drone | ✅ Yes | User approval for cost | Resource management |
| Send thermal drone to audio detection | ⚠️ Suggest | User decides | High-stakes verification |
| Continue vs. abort mission | ❌ No | Always user | Life-safety decision |
| Sacrifice drone for data | ⚠️ Suggest | User decides | Equipment vs. mission priority |
| Deploy human rescue team | ❌ No | Always user | Human life at risk |

---

## 🎨 UI Components Needed

### **1. AI Recommendations Panel**
```
┌─ AI Advisor ────────────────────────────────┐
│ 🔴 CRITICAL (08:42)                        │
│ Verify audio detection                     │
│ Voice-like audio detected at Tight Squeeze │
│ Confidence: 62% - Deploy thermal specialist?│
│ [Deploy drone-thermal-01] [Defer] [Ignore] │
├────────────────────────────────────────────┤
│ 🟡 HIGH (07:15)                            │
│ Signal chain compromised                   │
│ Cave Scout signal: 15% - Deploy relay?     │
│ [Deploy relay-02] [Defer] [Ignore]         │
└────────────────────────────────────────────┘
```

### **2. Hardware Inventory Panel**
```
┌─ Available Hardware ────────────────────────┐
│ Filter: [All] [Aerial] [Ground] [Relay]    │
├────────────────────────────────────────────┤
│ 🚁 Lightweight Scout (×2)                  │
│    Battery: 15min | Sensors: LiDAR, Camera│
│    [Deploy to: ▼] [Select on map]         │
├────────────────────────────────────────────┤
│ 📡 Static Relay Node (×4)                 │
│    Signal: 50m | No movement              │
│    [Deploy to: ▼] [Select on map]         │
├────────────────────────────────────────────┤
│ 🔥 Thermal-Audio Specialist (×1)          │
│    Battery: 20min | Sensors: Thermal, Mic │
│    Cost: High | [Deploy to: ▼]            │
└────────────────────────────────────────────┘
```

### **3. Mission Control Mode Selector**
```
┌─ Mission Mode ──────────────────────────────┐
│ ○ Fully Automated AI                       │
│   AI deploys all hardware, user observes   │
│                                            │
│ ● Manual Control                           │
│   User selects each deployment            │
│                                            │
│ ○ AI-Assisted (Hybrid)                     │
│   AI suggests, user approves              │
│                                            │
│ [Start Mission]                            │
└────────────────────────────────────────────┘
```

### **4. Deployment History Timeline**
```
┌─ Mission Timeline ──────────────────────────┐
│ ├─ 00:00 ✓ Initial deployment (3 agents)  │
│ ├─ 05:12 ✓ Audio detection (Cave Scout)   │
│ ├─ 07:42 ⚠️ AI: Deploy relay (Deferred)   │
│ ├─ 08:15 ❌ Cave Scout failed (0% battery) │
│ ├─ 08:30 ✓ USER: Deployed thermal drone   │
│ ├─ 12:45 ✓ Survivor confirmed (92% conf)  │
│ └─ 16:49 ✅ Mission complete               │
└────────────────────────────────────────────┘
```

### **5. Outcome Analysis Modal**
```
┌─ Mission Complete ──────────────────────────┐
│ ✅ SUCCESS (COSTLY)                        │
│                                            │
│ Primary Objective: ✓ Survivor Located     │
│ Confidence: 92%                            │
│ Location: Tight Squeeze, -18m depth       │
│                                            │
│ Mission Statistics:                        │
│ • Duration: 16:49                          │
│ • Terrain Mapped: 71.4%                    │
│ • Agents Deployed: 4                       │
│ • Agents Sacrificed: 3                     │
│ • Deployment Cost: 850 points              │
│                                            │
│ AI Analysis:                               │
│ "Relay deployment at 07:42 would have     │
│ preserved Cave Scout. Thermal confirmation │
│ at 08:30 was optimal timing."              │
│                                            │
│ [View Full Report] [Replay Mission]       │
└────────────────────────────────────────────┘
```

---

## 🔧 Implementation Phases

### **Phase 1: Foundation** (Current Sprint)
- ✅ Fix signal strength for sacrificed agents
- ⏺️ Fix audio detection marker positioning
- ⏺️ Implement full network relay chain visualization
- ⏺️ Create basic AI Recommendations Panel (static demo)
- ⏺️ Create Mission Outcome Modal
- ⏺️ Create Hardware Inventory database models

### **Phase 2: Interactive Deployment** (Next Sprint)
- Create UserDeployment model
- Build hardware inventory UI
- Implement "Deploy Hardware" API endpoints
- Allow mid-mission deployments in manual mode
- Update simulation engine to handle dynamic deployments
- Add deployment events to timeline

### **Phase 3: AI Advisor** (Sprint 3)
- Implement AIRecommendation model
- Build MissionAdvisor service
- Create AI recommendation generation logic
- Add recommendation acceptance/rejection UI
- Implement hybrid mode (AI suggests, user decides)

### **Phase 4: Customizable Failures** (Sprint 4)
- Create FailureProfile model
- Build failure profile editor UI
- Implement failure profile application in simulation
- Add failure event visualization
- Create failure library (dust, water, heat, impact, etc.)

### **Phase 5: Automated Mode** (Sprint 5)
- Implement full automated AI mission planner
- Build hardware selection algorithm
- Create contingency deployment logic
- Add real-time automated deployment
- Implement outcome prediction

### **Phase 6: Replay & Analysis** (Sprint 6)
- Build mission replay controls
- Implement timeline scrubbing
- Create comparative analysis (manual vs AI modes)
- Add "lessons learned" generation
- Build training scenario library

---

## 📊 Sample Data

### **Hardware Inventory Examples**

```json
{
  "inventory_id": "drone-scout-light-01",
  "hardware_type": "drone",
  "model_name": "Lightweight Scout Quadcopter",
  "max_battery_minutes": 15,
  "sensors": ["lidar", "camera_rgb"],
  "movement_capability": "aerial",
  "signal_range_m": 30,
  "deployment_cost": 100,
  "recovery_difficulty": "moderate",
  "quantity_available": 3,
  "base_failure_profile": "dust_vulnerable"
}
```

```json
{
  "inventory_id": "drone-thermal-specialist",
  "hardware_type": "drone",
  "model_name": "Thermal-Audio Specialist",
  "max_battery_minutes": 20,
  "sensors": ["lidar", "thermal", "audio_array", "camera_rgb"],
  "movement_capability": "aerial",
  "signal_range_m": 40,
  "deployment_cost": 500,
  "recovery_difficulty": "difficult",
  "quantity_available": 1,
  "base_failure_profile": "high_reliability"
}
```

```json
{
  "inventory_id": "relay-static-basic",
  "hardware_type": "relay",
  "model_name": "Static Relay Node",
  "max_battery_minutes": 180,
  "sensors": [],
  "movement_capability": "static",
  "signal_range_m": 50,
  "deployment_cost": 50,
  "recovery_difficulty": "easy",
  "quantity_available": 6,
  "base_failure_profile": null
}
```

### **Failure Profile Examples**

```json
{
  "profile_id": "dust_degradation_lidar",
  "name": "Dust-Induced LiDAR Degradation",
  "description": "Particulate interference in collapsed structures",
  "trigger_type": "sector_based",
  "trigger_params": {"sector_tags": ["collapsed", "dusty"]},
  "affected_systems": ["lidar"],
  "severity": "moderate",
  "progression_curve": "linear",
  "effect_modifiers": {
    "lidar_noise_multiplier": 2.4,
    "map_confidence_reduction": 0.35,
    "range_reduction": 0.5
  },
  "mission_impact": "Mapping accuracy reduced, slower progress required"
}
```

```json
{
  "profile_id": "battery_thermal_load",
  "name": "Thermal Sensor Battery Drain",
  "description": "Thermal imaging increases power consumption",
  "trigger_type": "sensor_activation",
  "trigger_params": {"sensor": "thermal", "continuous": true},
  "affected_systems": ["battery"],
  "severity": "moderate",
  "progression_curve": "exponential",
  "effect_modifiers": {
    "battery_drain_multiplier": 1.8
  },
  "mission_impact": "Reduced mission duration when thermal active"
}
```

---

## 🎯 User Stories

### **Story 1: Automated AI Mission**
> As a mission commander, I want the AI to automatically select and deploy hardware so I can see an optimized rescue strategy without manual intervention.

**Acceptance Criteria**:
- User selects "Fully Automated AI" mode
- User clicks "Start Mission"
- AI deploys initial hardware based on terrain analysis
- AI automatically deploys relays when signal degrades
- AI replaces failed agents to maintain coverage
- User sees real-time explanations of AI decisions
- Mission completes with outcome analysis

### **Story 2: Manual Hardware Deployment**
> As a rescue operator, I want to manually select and deploy hardware so I can practice mission decision-making skills.

**Acceptance Criteria**:
- User selects "Manual Control" mode
- User sees available hardware inventory
- User can deploy hardware to specific sectors at any time
- System shows consequences of deployment decisions
- User can choose to continue mission or abort
- User receives outcome analysis comparing to AI-optimized path

### **Story 3: AI-Assisted Decision Making**
> As a rescue coordinator, I want AI recommendations with final approval so I maintain control while getting expert guidance.

**Acceptance Criteria**:
- User selects "AI-Assisted (Hybrid)" mode
- AI generates recommendations at key decision points
- User can accept, defer, or reject each recommendation
- System explains reasoning for each recommendation
- System tracks user decisions vs AI suggestions
- Outcome analysis shows impact of user's choices

### **Story 4: Custom Failure Scenarios**
> As a training officer, I want to customize equipment failure scenarios so I can train operators for specific conditions.

**Acceptance Criteria**:
- User can create/edit failure profiles
- User can assign failure profiles to hardware types
- User can configure trigger conditions (time, depth, sector)
- System applies failures during mission
- Failures explained with operator-visible messages
- Library of pre-built failure scenarios available

---

## 🚀 Technical Challenges

### **Challenge 1: Dynamic Simulation State**
**Problem**: Current scenario_engine.py assumes pre-scripted routes. Need to handle mid-mission deployments.

**Solution**:
```python
def generate_simulation_state_from_scenario(scenario, elapsed_seconds, user_deployments=None):
    """
    Enhanced to support dynamic user deployments
    
    user_deployments: [
        {"agent_id": "user-drone-1", "deployment_time": 420, "route_id": 5, "current_waypoint": 2},
        {"agent_id": "user-relay-1", "deployment_time": 450, "route_id": None, "static_sector": "junction-alpha"}
    ]
    """
    # Process pre-scripted routes
    # PLUS process user deployments
    # Calculate positions for both
    # Merge into unified state
```

### **Challenge 2: Real-Time AI Recommendations**
**Problem**: Need to analyze mission state and generate recommendations in < 500ms

**Solution**:
- Pre-compute common recommendation templates
- Use rule-based system (not ML) for speed
- Cache terrain analysis
- Update recommendations only on state changes

### **Challenge 3: Inventory Management**
**Problem**: Track available/deployed/lost hardware across multiple missions

**Solution**:
- HardwareInventory.quantity_available decrements on deployment
- Increments on successful recovery
- Locks hardware during active missions
- Admin UI to reset inventory between training sessions

### **Challenge 4: Branching Mission Outcomes**
**Problem**: Manual mode creates infinite possible outcomes

**Solution**:
- Define clear success criteria (survivor found/not found)
- Measure efficiency (cost, time, equipment loss)
- Compare to baseline AI-optimized outcome
- Focus on "learning moments" not perfect optimization

---

## 📚 References

- **Project Instructions**: `.github/copilot-instructions.md`
- **Current Scenario System**: `backend/apps/missions/models.py`
- **Scenario Engine**: `backend/apps/missions/services/scenario_engine.py`
- **Mission Dashboard**: `frontend/src/pages/demo/live/cave-rescue.astro`
- **Tactical Map**: `frontend/src/lib/tactical-map-manager.ts`

---

## ✅ Next Actions

1. **Create database models** for HardwareInventory, FailureProfile, UserDeployment, AIRecommendation
2. **Seed sample inventory** with 10-15 hardware options
3. **Build basic AI Recommendations Panel** (static recommendations for demo)
4. **Implement full network relay chain visualization** (fix missing connections)
5. **Create Mission Outcome Modal** (show results at mission end)
6. **Fix audio detection positioning bug**

**Priority**: Focus on Phase 1 Foundation items before building interactive deployment system.
