For your RescueMesh app, I’d split the use case content into two layers:

Astro content = mostly static explanatory/public pages
Django database = operational mission templates and simulation data

So not every bit of the use case needs to live in Django.

Keep this in Astro / Markdown / JSON content

These are mostly descriptive website content:

Use case title
Marketing description
Long mission objective text
Narrative explanation
Public-facing examples
Architecture notes
Screenshots / diagrams
Reference links
Static documentation

Example:

Cave Rescue
Priority: Life Safety / Navigation Safety

Mission Objective:
Map complex underground cave passages...

This can happily live in Astro as .md, .mdx, or local JSON/TypeScript files.

Put this in the Django database

Django should store the parts that become operational, selectable, configurable, or used by the simulator.

1. Use Case Template

This is the high-level mission template.

class UseCaseTemplate(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    priority = models.CharField(max_length=100)
    summary = models.TextField()
    is_active = models.BooleanField(default=True)

Examples:

collapsed-building-search
cave-rescue
flooded-structure
industrial-inspection
2. Terrain Profile

This belongs in Django because terrain affects simulation behaviour.

class TerrainProfile(models.Model):
    use_case = models.ForeignKey(UseCaseTemplate, on_delete=models.CASCADE)
    terrain_type = models.CharField(max_length=200)
    gps_status = models.CharField(max_length=100)
    communication_conditions = models.TextField()
    lighting_conditions = models.TextField()
    hazards = models.JSONField(default=list)

For example:

{
  "hazards": [
    "rock fall",
    "water pools",
    "low oxygen pockets",
    "narrow passages"
  ]
}
3. Recommended Agent Roles

These should be in Django because the demo will use them to create simulated drones, relays, and sensor nodes.

class AgentRoleTemplate(models.Model):
    use_case = models.ForeignKey(UseCaseTemplate, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    description = models.TextField()
    default_quantity = models.PositiveIntegerField(default=1)
    capabilities = models.JSONField(default=list)

Example:

Scout Drone
Relay Drone
Micro Mapper
Amphibious Micro Agent
Static Monitoring Node
4. Sensor Package Templates

These definitely belong in Django if the dashboard will simulate or display sensor feeds.

class SensorPackageTemplate(models.Model):
    agent_role = models.ForeignKey(AgentRoleTemplate, on_delete=models.CASCADE)
    sensor_type = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    data_format = models.CharField(max_length=100)
    expected_output = models.TextField(blank=True)

Examples:

LiDAR
Thermal camera
RGB camera
Microphone array
CO2 sensor
WiFi/Bluetooth scanner
Pressure sensor
Humidity sensor
Gas sensor placeholder
NFC black-box module
5. Failure Profiles

These absolutely belong in Django because they drive the demo behaviour.

class FailureProfile(models.Model):
    use_case = models.ForeignKey(UseCaseTemplate, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    affected_component = models.CharField(max_length=100)
    severity = models.CharField(max_length=50)
    trigger_type = models.CharField(max_length=100)
    description = models.TextField()
    effects = models.JSONField(default=dict)

Example:

{
  "name": "Dust Occlusion",
  "affected_component": "LiDAR",
  "severity": "medium",
  "trigger_type": "enter_sector",
  "effects": {
    "map_confidence_drop": 0.35,
    "sensor_noise_multiplier": 2.4,
    "operator_alert": true
  }
}
6. Expected Outputs

These should be in Django if they become dashboard tabs, generated artifacts, AI outputs, or report sections.

class ExpectedOutputTemplate(models.Model):
    use_case = models.ForeignKey(UseCaseTemplate, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    output_type = models.CharField(max_length=100)
    description = models.TextField()
    confidence_required = models.BooleanField(default=True)

Examples:

3D Void Map
Thermal Anomalies
Audio Events
Device Scan
Relay Map
Access Routes
AI Analysis
Flood Extent Map
Static Sensor Placement Map
7. AI Prompt Templates

These should live in Django because they are part of the operational behaviour.

class AIPromptTemplate(models.Model):
    use_case = models.ForeignKey(UseCaseTemplate, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    prompt_text = models.TextField()
    output_schema = models.JSONField(default=dict)

Example roles:

mission_planner
sensor_analyst
operator_assistant
incident_report_writer
8. Mission Instances

This is where the database becomes essential. A use case template is static; a mission instance is an actual run of that template.

class Mission(models.Model):
    use_case = models.ForeignKey(UseCaseTemplate, on_delete=models.PROTECT)
    mission_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

Example:

mission-demo-001
Collapsed Building Search - Demo
Status: Simulated
9. Mission Assets

These are the actual drones, relays, nodes, sensors, and abandoned hardware shown on the dashboard map.

class MissionAsset(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    asset_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    battery_percent = models.FloatField(null=True, blank=True)
    last_known_position = models.JSONField(default=dict)
    nfc_recovery_available = models.BooleanField(default=False)

Example states:

healthy
degraded
intermittent
failed
landed_relay
abandoned
sacrificed
nfc_readable
black_box_recovered
10. Mission Events / Timeline

The mission timeline should be database-backed.

class MissionEvent(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    event_type = models.CharField(max_length=100)
    asset = models.ForeignKey(MissionAsset, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200)
    description = models.TextField()
    confidence = models.FloatField(null=True, blank=True)
    payload = models.JSONField(default=dict)

Examples:

Drone A entered Sector 1
Relay Node deployed
Thermal anomaly detected
LiDAR confidence degraded
Drone B landed as relay
NFC black-box readable
Practical recommendation

For the MVP, I’d start with this minimum Django set:

UseCaseTemplate
TerrainProfile
AgentRoleTemplate
SensorPackageTemplate
FailureProfile
ExpectedOutputTemplate
Mission
MissionAsset
MissionEvent

Then add AI prompt templates once the simulation is working.

Simple rule of thumb

Ask this question:

“Will the dashboard, simulator, API, report, or AI prompt engine need to query or change this?”

If yes, put it in Django.

“Is this just explanatory text for the website?”

If yes, keep it in Astro.

Best split for your current use cases
Use case section	Astro	Django DB
Title	Yes	Yes
Priority	Yes	Yes
Mission Objective	Yes	Optional summary
Terrain Characteristics	Display	Yes
Recommended Agents	Display	Yes
Sensor capabilities	Display	Yes
Expected Failures	Display	Yes
Expected Outputs	Display	Yes
Long narrative explanation	Yes	No
AI prompt logic	No	Yes
Mission runs	No	Yes
Telemetry	No	Yes
Hardware state	No	Yes
Left-behind asset locations	No	Yes
NFC black-box state	No	Yes

So the use case page can still be beautifully rendered by Astro, but the source of truth for mission simulation should come from Django.