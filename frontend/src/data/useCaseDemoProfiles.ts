/**
 * Use case demo profiles for RescueMesh mission simulations
 * 
 * TODO: Replace this with Django API calls to /api/v1/missions/templates/
 * Future shape: GET /api/v1/missions/templates/{slug}/demo-profile
 */

import type { UseCaseDemoProfile } from '../types/demo';

export const useCaseDemoProfiles: UseCaseDemoProfile[] = [
  {
    slug: 'collapsed-building-search',
    title: 'Collapsed Building Search',
    priority: 'Life Safety',
    missionId: 'mission-demo-collapsed-001',
    status: 'Simulated',
    missionObjective: 'Rapidly map unstable voids and detect signs of human presence in partially collapsed structures where traditional search methods are too dangerous or time-consuming.',
    terrain: {
      type: 'Collapsed building with unstable voids, rubble, and confined spaces',
      gps: 'Denied or unreliable inside structure',
      communications: 'Radio attenuation through concrete and steel',
      lighting: 'Dark with dust obscuration',
      hazards: ['Unstable structure', 'Sharp debris', 'Dust', 'Potential secondary collapse']
    },
    agents: [
      {
        id: 'drone-a',
        name: 'Survey Drone A',
        role: 'Primary Mapper',
        description: 'LiDAR and thermal imaging survey drone',
        state: 'healthy',
        batteryPercent: 78,
        locationLabel: 'Sector 2 - Main void',
        capabilities: ['LiDAR 3D mapping', 'Thermal imaging', 'RGB camera', 'Obstacle avoidance'],
        sensors: ['LiDAR', 'Thermal camera', 'RGB camera', 'IMU', 'Altimeter']
      },
      {
        id: 'drone-b',
        name: 'Detection Drone B',
        role: 'Life Sign Detection',
        description: 'Audio and environmental sensor specialist',
        state: 'landed_relay',
        batteryPercent: 23,
        locationLabel: 'Sector 3 - Relay position',
        capabilities: ['Audio detection', 'CO2 sensing', 'Device scanning', 'Mesh relay'],
        sensors: ['Microphone array', 'CO2 sensor', 'WiFi/Bluetooth scanner', 'Temperature'],
        nfcRecoveryAvailable: true
      },
      {
        id: 'drone-c',
        name: 'Penetration Drone C',
        role: 'Deep Exploration',
        description: 'Compact drone for confined spaces',
        state: 'failed',
        batteryPercent: 3,
        locationLabel: 'Sector 4 - Deep void (last known)',
        capabilities: ['Compact design', 'Thermal imaging', 'Audio detection', 'Priority streaming'],
        sensors: ['Thermal camera', 'Audio sensor', 'IMU'],
        nfcRecoveryAvailable: true
      },
      {
        id: 'relay-01',
        name: 'Relay Node 01',
        role: 'Communications Bridge',
        description: 'Static relay extending range into structure',
        state: 'healthy',
        batteryPercent: 94,
        locationLabel: 'Entry point - Sector 1',
        capabilities: ['High-power radio', 'Mesh networking', 'Environmental monitoring'],
        sensors: ['Temperature', 'Humidity', 'Pressure']
      }
    ],
    expectedFailures: [
      {
        name: 'Dust Occlusion',
        affectedComponent: 'LiDAR - Drone A',
        severity: 'medium',
        description: 'LiDAR quality degraded by airborne particulate matter',
        dashboardEffect: 'Map confidence reduced to 68%, slower mapping speed'
      },
      {
        name: 'Radio Packet Loss',
        affectedComponent: 'Communications - Drone B',
        severity: 'high',
        description: 'Intermittent signal through reinforced concrete',
        dashboardEffect: 'Drone B switched to relay mode to preserve communication chain'
      },
      {
        name: 'Battery Collapse',
        affectedComponent: 'Power - Drone C',
        severity: 'critical',
        description: 'Unexpected battery failure after thermal payload surge',
        dashboardEffect: 'Drone C failed in deep void, NFC black-box recovery available'
      }
    ],
    expectedOutputs: [
      {
        name: '3D Void Map',
        outputType: '3d-map',
        description: 'Point cloud showing accessible spaces and obstructions',
        confidenceRequired: true
      },
      {
        name: 'Thermal Anomalies',
        outputType: 'thermal',
        description: 'Heat signatures ranked by survivor probability',
        confidenceRequired: true
      },
      {
        name: 'Audio Events',
        outputType: 'audio',
        description: 'Voice-like sounds with confidence ratings',
        confidenceRequired: true
      },
      {
        name: 'Device Scan',
        outputType: 'device-scan',
        description: 'WiFi/Bluetooth signals from mobile phones',
        confidenceRequired: false
      },
      {
        name: 'Relay Map',
        outputType: 'relay-map',
        description: 'Network topology showing communications coverage',
        confidenceRequired: false
      },
      {
        name: 'AI Analysis',
        outputType: 'ai-analysis',
        description: 'Prioritized detection list requiring human review',
        confidenceRequired: true
      }
    ],
    simulation: {
      mapType: 'void-map',
      environmentTags: ['urban', 'concrete', 'steel', 'dusty', 'unstable'],
      defaultConfidence: 0.72,
      communicationRisk: 'high',
      batteryRisk: 'medium',
      sensorRisk: 'medium',
      missionDurationMinutes: 18
    },
    timeline: [
      {
        time: '00:00',
        title: 'Mission Start',
        description: 'Three drones and one relay node deployed',
        eventType: 'mission-start'
      },
      {
        time: '02:15',
        title: 'Initial Mapping',
        description: 'Drone A completes sector 1 LiDAR scan',
        assetId: 'drone-a',
        eventType: 'mapping',
        confidence: 0.89
      },
      {
        time: '05:30',
        title: 'Dust Degradation',
        description: 'Drone A LiDAR quality drops due to airborne dust',
        assetId: 'drone-a',
        eventType: 'failure',
        confidence: 0.68
      },
      {
        time: '08:45',
        title: 'Thermal Detection',
        description: 'Drone A detects thermal anomaly in sector 2',
        assetId: 'drone-a',
        eventType: 'sensor-detection',
        confidence: 0.58
      },
      {
        time: '11:20',
        title: 'Communications Degraded',
        description: 'Drone B experiences intermittent packet loss',
        assetId: 'drone-b',
        eventType: 'failure'
      },
      {
        time: '12:10',
        title: 'Tactical Relay Decision',
        description: 'Drone B lands to serve as relay node (battery 23%)',
        assetId: 'drone-b',
        eventType: 'relay'
      },
      {
        time: '14:35',
        title: 'Voice-Like Audio',
        description: 'Drone C detects possible voice signature in sector 4',
        assetId: 'drone-c',
        eventType: 'sensor-detection',
        confidence: 0.61
      },
      {
        time: '15:42',
        title: 'Battery Failure',
        description: 'Drone C suffers unexpected power collapse',
        assetId: 'drone-c',
        eventType: 'failure'
      },
      {
        time: '16:30',
        title: 'AI Analysis Complete',
        description: 'AI analyst identifies priority review zones',
        eventType: 'ai-analysis',
        confidence: 0.74
      },
      {
        time: '17:45',
        title: 'Operator Review',
        description: 'Human review of thermal and audio detections',
        eventType: 'operator-review'
      },
      {
        time: '18:00',
        title: 'Mission Complete',
        description: 'Mapping coverage 76%, two priority zones identified',
        eventType: 'mission-end'
      }
    ],
    aiAnalyst: {
      role: 'Survivor Detection Analyst',
      promptSummary: 'Analyze thermal, audio, and WiFi/Bluetooth data to identify possible survivor locations',
      expectedFindings: [
        'Thermal anomaly in sector 2 (confidence: 58%) - possible human presence',
        'Voice-like audio in sector 4 (confidence: 61%) - recommend immediate human review',
        'No WiFi/Bluetooth signals detected',
        'Void map shows accessible rescue route to sector 2'
      ],
      humanReviewRequired: true
    }
  },
  {
    slug: 'cave-rescue',
    title: 'Cave Rescue',
    priority: 'Life Safety / Navigation Safety',
    missionId: 'mission-demo-cave-002',
    status: 'Simulated',
    missionObjective: 'Map complex underground cave passages, identify safe routes, detect signs of trapped persons, and maintain communication links in GPS-denied, dark, humid, and irregular terrain.',
    terrain: {
      type: 'Natural cave system with tunnels, chambers, narrow passages',
      gps: 'Fully denied underground',
      communications: 'Severe attenuation through rock',
      lighting: 'Complete darkness',
      hazards: ['Tight passages', 'Falling rock', 'Moisture', 'Water', 'Unstable footing', 'Low oxygen pockets']
    },
    agents: [
      {
        id: 'scout-a',
        name: 'Scout Drone A',
        role: 'Primary Explorer',
        description: 'Route mapping and passage assessment',
        state: 'healthy',
        batteryPercent: 65,
        locationLabel: 'Chamber 3 - Main passage',
        capabilities: ['3D passage mapping', 'Thermal imaging', 'Obstacle avoidance'],
        sensors: ['LiDAR', 'Thermal camera', 'Low-light camera', 'IMU']
      },
      {
        id: 'relay-b',
        name: 'Relay Drone B',
        role: 'Communications Chain',
        description: 'Mesh relay maintaining signal path',
        state: 'landed_relay',
        batteryPercent: 41,
        locationLabel: 'Junction 2 - Relay position',
        capabilities: ['Mesh networking', 'Signal monitoring', 'Low-power mode'],
        sensors: ['Signal strength monitor', 'Temperature', 'Humidity'],
        nfcRecoveryAvailable: true
      },
      {
        id: 'micro-c',
        name: 'Micro Mapper C',
        role: 'Narrow Passage Specialist',
        description: 'Small form factor for tight squeezes',
        state: 'degraded',
        batteryPercent: 28,
        locationLabel: 'Side passage 4B',
        capabilities: ['Compact design', 'Short-range mapping', 'Audio detection'],
        sensors: ['Depth sensor', 'Audio sensor', 'Temperature', 'Humidity']
      },
      {
        id: 'sensor-node-01',
        name: 'Ground Sensor Node 01',
        role: 'Environmental Monitoring',
        description: 'Static node at key junction',
        state: 'healthy',
        batteryPercent: 88,
        locationLabel: 'Junction 1 - Entry zone',
        capabilities: ['Mesh repeater', 'Air quality monitoring', 'Passive audio'],
        sensors: ['Temperature', 'Humidity', 'Air quality', 'Microphone', 'Pressure']
      }
    ],
    expectedFailures: [
      {
        name: 'Rock Attenuation',
        affectedComponent: 'Communications - Relay B',
        severity: 'high',
        description: 'Radio signal severely degraded through dense rock',
        dashboardEffect: 'Relay B landed at junction to preserve communication chain'
      },
      {
        name: 'Moisture Degradation',
        affectedComponent: 'Sensors - Micro C',
        severity: 'medium',
        description: 'High humidity affecting sensor readings',
        dashboardEffect: 'Micro C depth sensor confidence reduced to 54%'
      },
      {
        name: 'Navigation Drift',
        affectedComponent: 'SLAM - Scout A',
        severity: 'medium',
        description: 'SLAM confidence decreasing in repetitive tunnel section',
        dashboardEffect: 'Scout A position uncertainty increased to ±2.1m'
      }
    ],
    expectedOutputs: [
      {
        name: '3D Cave Passage Map',
        outputType: '3d-map',
        description: 'Tunnel mesh showing chambers, shafts, and traversable routes',
        confidenceRequired: true
      },
      {
        name: 'Route Safety Estimate',
        outputType: 'ai-analysis',
        description: 'Confidence-ranked routes for rescue teams',
        confidenceRequired: true
      },
      {
        name: 'Thermal Anomalies',
        outputType: 'thermal',
        description: 'Heat signatures indicating humans or warm airflow',
        confidenceRequired: true
      },
      {
        name: 'Audio Events',
        outputType: 'audio',
        description: 'Voice, movement, water flow, or tapping patterns',
        confidenceRequired: true
      },
      {
        name: 'Environmental Readings',
        outputType: 'environmental',
        description: 'Temperature, humidity, air quality indicators',
        confidenceRequired: false
      },
      {
        name: 'Relay Map',
        outputType: 'relay-map',
        description: 'Communication chain from entrance to deep exploration',
        confidenceRequired: false
      }
    ],
    simulation: {
      mapType: 'cave-map',
      environmentTags: ['underground', 'rock', 'humid', 'dark', 'irregular'],
      defaultConfidence: 0.68,
      communicationRisk: 'severe',
      batteryRisk: 'medium',
      sensorRisk: 'medium',
      missionDurationMinutes: 22
    },
    timeline: [
      {
        time: '00:00',
        title: 'Mission Start',
        description: 'Cave entrance deployment of three agents and sensor node',
        eventType: 'mission-start'
      },
      {
        time: '03:20',
        title: 'Initial Passage Mapped',
        description: 'Scout A completes entry tunnel scan',
        assetId: 'scout-a',
        eventType: 'mapping',
        confidence: 0.84
      },
      {
        time: '06:45',
        title: 'Signal Degradation',
        description: 'Relay B signal strength drops below threshold',
        assetId: 'relay-b',
        eventType: 'failure'
      },
      {
        time: '07:30',
        title: 'Relay Positioned',
        description: 'Relay B lands at junction 2 to maintain comms chain',
        assetId: 'relay-b',
        eventType: 'relay'
      },
      {
        time: '11:15',
        title: 'Chamber Discovery',
        description: 'Scout A discovers large chamber with multiple passages',
        assetId: 'scout-a',
        eventType: 'mapping',
        confidence: 0.79
      },
      {
        time: '14:20',
        title: 'Moisture Impact',
        description: 'Micro C sensors affected by high humidity',
        assetId: 'micro-c',
        eventType: 'failure'
      },
      {
        time: '16:40',
        title: 'Audio Detection',
        description: 'Possible tapping pattern detected in side passage',
        assetId: 'micro-c',
        eventType: 'sensor-detection',
        confidence: 0.52
      },
      {
        time: '19:10',
        title: 'Route Analysis',
        description: 'AI identifies three potential safe routes',
        eventType: 'ai-analysis',
        confidence: 0.71
      },
      {
        time: '21:30',
        title: 'Operator Review',
        description: 'Human review of audio signature and route options',
        eventType: 'operator-review'
      },
      {
        time: '22:00',
        title: 'Mission Complete',
        description: 'Cave passage mapped, relay chain established',
        eventType: 'mission-end'
      }
    ],
    aiAnalyst: {
      role: 'Cave Navigation Analyst',
      promptSummary: 'Analyze cave geometry, audio events, and environmental data to identify safe routes and possible trapped person locations',
      expectedFindings: [
        'Three traversable routes identified to chamber 3',
        'Possible tapping audio in side passage 4B (confidence: 52%)',
        'Route 2 recommended - widest passage, stable footing',
        'Low oxygen risk detected in chamber 2 - respirator required'
      ],
      humanReviewRequired: true
    }
  },
  {
    slug: 'flooded-structure',
    title: 'Flooded Structure',
    priority: 'Life Safety / Environmental Hazard Assessment',
    missionId: 'mission-demo-flood-003',
    status: 'Simulated',
    missionObjective: 'Survey partially flooded buildings, tunnels, or basements where water, debris, poor visibility, and electrical hazards make human access unsafe.',
    terrain: {
      type: 'Flooded or partially submerged built environment',
      gps: 'Denied indoors or underground',
      communications: 'Radio degraded by concrete, metal, and water',
      lighting: 'Dark and visually confusing due to water surfaces',
      hazards: ['Deep water', 'Floating debris', 'Submerged obstacles', 'Contamination', 'Electrical risk', 'Unstable surfaces']
    },
    agents: [
      {
        id: 'surface-a',
        name: 'Surface Scout A',
        role: 'Aerial Survey',
        description: 'Aerial survey of dry and partially flooded areas',
        state: 'healthy',
        batteryPercent: 71,
        locationLabel: 'Upper floor - Zone 2',
        capabilities: ['RGB imaging', 'Thermal imaging', 'LiDAR mapping', 'Water-resistant'],
        sensors: ['RGB camera', 'Thermal camera', 'LiDAR', 'Spotlight']
      },
      {
        id: 'amphibious-b',
        name: 'Amphibious Agent B',
        role: 'Water Surface Inspection',
        description: 'Hybrid unit for shallow flooded areas',
        state: 'abandoned',
        batteryPercent: 8,
        locationLabel: 'Basement level - Zone 4 (flooded)',
        capabilities: ['Water-surface operation', 'Sonar', 'Temperature sensing'],
        sensors: ['Short-range sonar', 'Temperature', 'Depth sensor'],
        nfcRecoveryAvailable: true
      },
      {
        id: 'env-sensor-01',
        name: 'Environmental Sensor Node 01',
        role: 'Water Level Monitoring',
        description: 'Static sensor at water entry point',
        state: 'healthy',
        batteryPercent: 92,
        locationLabel: 'Entry point - Zone 1',
        capabilities: ['Water level monitoring', 'Environmental sensing', 'Mesh relay'],
        sensors: ['Water level', 'Temperature', 'Pressure', 'Air quality']
      },
      {
        id: 'relay-02',
        name: 'Relay Node 02',
        role: 'Communications Bridge',
        description: 'High-position relay maintaining signal',
        state: 'healthy',
        batteryPercent: 86,
        locationLabel: 'Stairwell - Zone 3',
        capabilities: ['High-power mesh', 'Signal monitoring'],
        sensors: ['Signal strength', 'Temperature']
      }
    ],
    expectedFailures: [
      {
        name: 'Water Damage',
        affectedComponent: 'Motors - Amphibious B',
        severity: 'critical',
        description: 'Water ingress caused motor failure',
        dashboardEffect: 'Amphibious B abandoned in basement, NFC recovery possible'
      },
      {
        name: 'Reflection Errors',
        affectedComponent: 'LiDAR - Surface A',
        severity: 'medium',
        description: 'Water surface reflections reducing LiDAR accuracy',
        dashboardEffect: 'Surface A LiDAR confidence reduced near water surfaces'
      },
      {
        name: 'Signal Loss',
        affectedComponent: 'Communications - Amphibious B',
        severity: 'high',
        description: 'Radio signal lost through water and concrete',
        dashboardEffect: 'Last telemetry received before water immersion'
      }
    ],
    expectedOutputs: [
      {
        name: 'Flood Extent Map',
        outputType: '3d-map',
        description: 'Map showing dry, shallow, deep, and inaccessible zones',
        confidenceRequired: true
      },
      {
        name: 'Depth/Pressure Readings',
        outputType: 'environmental',
        description: 'Approximate water depth by location',
        confidenceRequired: false
      },
      {
        name: 'Thermal Anomalies',
        outputType: 'thermal',
        description: 'Possible human presence above waterline',
        confidenceRequired: true
      },
      {
        name: 'Submerged Obstruction Map',
        outputType: '3d-map',
        description: 'Sonar-based estimate of underwater hazards',
        confidenceRequired: true
      },
      {
        name: 'Environmental Alerts',
        outputType: 'environmental',
        description: 'Temperature, contamination, electrical-risk notes',
        confidenceRequired: false
      },
      {
        name: 'Asset Placement Map',
        outputType: 'relay-map',
        description: 'Locations of agents, failed units, and sensors',
        confidenceRequired: false
      }
    ],
    simulation: {
      mapType: 'flood-map',
      environmentTags: ['flooded', 'water', 'concrete', 'electrical-hazard', 'debris'],
      defaultConfidence: 0.64,
      communicationRisk: 'high',
      batteryRisk: 'low',
      sensorRisk: 'high',
      missionDurationMinutes: 15
    },
    timeline: [
      {
        time: '00:00',
        title: 'Mission Start',
        description: 'Deployment of surface drone, amphibious agent, and sensors',
        eventType: 'mission-start'
      },
      {
        time: '02:30',
        title: 'Upper Floor Survey',
        description: 'Surface A completes dry area mapping',
        assetId: 'surface-a',
        eventType: 'mapping',
        confidence: 0.81
      },
      {
        time: '04:45',
        title: 'Water Level Assessment',
        description: 'Environmental sensor confirms basement fully flooded',
        assetId: 'env-sensor-01',
        eventType: 'sensor-detection'
      },
      {
        time: '06:20',
        title: 'Amphibious Deployment',
        description: 'Amphibious B enters shallow water zone',
        assetId: 'amphibious-b',
        eventType: 'mapping'
      },
      {
        time: '08:10',
        title: 'Reflection Interference',
        description: 'Surface A LiDAR accuracy reduced near water',
        assetId: 'surface-a',
        eventType: 'failure'
      },
      {
        time: '10:35',
        title: 'Motor Failure',
        description: 'Amphibious B suffers water damage',
        assetId: 'amphibious-b',
        eventType: 'failure'
      },
      {
        time: '11:00',
        title: 'Asset Abandoned',
        description: 'Amphibious B left in place as water-level beacon',
        assetId: 'amphibious-b',
        eventType: 'relay'
      },
      {
        time: '12:45',
        title: 'Thermal Scan',
        description: 'No thermal signatures detected in accessible zones',
        assetId: 'surface-a',
        eventType: 'sensor-detection',
        confidence: 0.76
      },
      {
        time: '14:20',
        title: 'AI Analysis Complete',
        description: 'Flood map and access routes generated',
        eventType: 'ai-analysis',
        confidence: 0.69
      },
      {
        time: '15:00',
        title: 'Mission Complete',
        description: 'Flood extent mapped, electrical hazard zones identified',
        eventType: 'mission-end'
      }
    ],
    aiAnalyst: {
      role: 'Flood Assessment Analyst',
      promptSummary: 'Analyze flood extent, thermal data, and obstruction map to identify safe access routes and hazard zones',
      expectedFindings: [
        'Basement fully flooded - depth 2.8m estimated',
        'No thermal signatures detected in surveyed areas',
        'Electrical panel in zone 3 - high shock risk',
        'Safe access route via stairwell to upper floors'
      ],
      humanReviewRequired: true
    }
  },
  {
    slug: 'industrial-inspection',
    title: 'Industrial Inspection',
    priority: 'Infrastructure Safety / Hazard Prevention',
    missionId: 'mission-demo-industrial-004',
    status: 'Simulated',
    missionObjective: 'Inspect dangerous, confined, or hard-to-access industrial environments such as tanks, ducts, silos, and plant rooms without exposing personnel to unnecessary risk.',
    terrain: {
      type: 'Industrial interior with confined spaces and equipment',
      gps: 'Denied indoors or inside metal structures',
      communications: 'Interference from metal, machinery, and electromagnetic noise',
      lighting: 'Variable with dark spaces and glare',
      hazards: ['Heat', 'Gas', 'Chemicals', 'Moving machinery', 'Confined-space risks', 'Sharp metal', 'Poor ventilation']
    },
    agents: [
      {
        id: 'inspection-a',
        name: 'Inspection Drone A',
        role: 'Primary Inspection',
        description: 'Visual and geometric inspection specialist',
        state: 'healthy',
        batteryPercent: 69,
        locationLabel: 'Tank 3 - Upper section',
        capabilities: ['RGB imaging', 'LiDAR mapping', 'Thermal imaging', 'Protective cage'],
        sensors: ['RGB camera', 'LiDAR', 'Thermal camera', 'Stable hover']
      },
      {
        id: 'environmental-b',
        name: 'Environmental Drone B',
        role: 'Hazard Detection',
        description: 'Environmental and gas sensing specialist',
        state: 'degraded',
        batteryPercent: 52,
        locationLabel: 'Pipe gallery - Section 4',
        capabilities: ['Temperature sensing', 'Gas detection', 'Audio monitoring'],
        sensors: ['Temperature', 'Gas sensor', 'Humidity', 'Pressure', 'Audio/vibration']
      },
      {
        id: 'detail-c',
        name: 'Detail Drone C',
        role: 'Close-Range Inspection',
        description: 'Macro inspection for defects and corrosion',
        state: 'healthy',
        batteryPercent: 44,
        locationLabel: 'Duct junction - Section 2',
        capabilities: ['Macro camera', 'LED lighting', 'Compact design'],
        sensors: ['Close-range camera', 'LED array', 'IMU']
      },
      {
        id: 'monitor-node-01',
        name: 'Static Monitoring Node 01',
        role: 'Continuous Monitoring',
        description: 'Left in place for vibration and temperature tracking',
        state: 'healthy',
        batteryPercent: 91,
        locationLabel: 'Tank 2 - Lower mount',
        capabilities: ['Vibration monitoring', 'Temperature tracking', 'Long-life battery'],
        sensors: ['Temperature', 'Vibration/acoustic', 'Gas sensor', 'Mesh relay']
      }
    ],
    expectedFailures: [
      {
        name: 'Electromagnetic Interference',
        affectedComponent: 'Compass - Environmental B',
        severity: 'medium',
        description: 'Industrial equipment interfering with navigation',
        dashboardEffect: 'Environmental B navigation confidence reduced'
      },
      {
        name: 'Reflective Surface Confusion',
        affectedComponent: 'LiDAR - Inspection A',
        severity: 'low',
        description: 'Metal tank surfaces causing reflection errors',
        dashboardEffect: 'LiDAR readings filtered, confidence adjusted'
      },
      {
        name: 'Heat Exposure',
        affectedComponent: 'Sensors - Environmental B',
        severity: 'medium',
        description: 'High ambient temperature affecting sensor accuracy',
        dashboardEffect: 'Environmental B sensor readings flagged for review'
      }
    ],
    expectedOutputs: [
      {
        name: '3D Asset Map',
        outputType: '3d-map',
        description: 'Point cloud of tanks, ducts, machinery, and pipework',
        confidenceRequired: true
      },
      {
        name: 'Defect Indicators',
        outputType: 'ai-analysis',
        description: 'Possible corrosion, cracks, obstructions, leaks',
        confidenceRequired: true
      },
      {
        name: 'Thermal Map',
        outputType: 'thermal',
        description: 'Heat signatures around equipment and confined spaces',
        confidenceRequired: false
      },
      {
        name: 'Environmental Readings',
        outputType: 'environmental',
        description: 'Temperature, humidity, pressure, gas-risk data',
        confidenceRequired: false
      },
      {
        name: 'Audio/Vibration Events',
        outputType: 'audio',
        description: 'Unusual mechanical sounds or vibration patterns',
        confidenceRequired: true
      },
      {
        name: 'Inspection Confidence Score',
        outputType: 'ai-analysis',
        description: 'Confidence level for each inspected zone',
        confidenceRequired: true
      }
    ],
    simulation: {
      mapType: 'industrial-map',
      environmentTags: ['industrial', 'metal', 'confined', 'heat', 'machinery'],
      defaultConfidence: 0.77,
      communicationRisk: 'medium',
      batteryRisk: 'low',
      sensorRisk: 'medium',
      missionDurationMinutes: 20
    },
    timeline: [
      {
        time: '00:00',
        title: 'Mission Start',
        description: 'Industrial inspection deployment - three drones and monitoring node',
        eventType: 'mission-start'
      },
      {
        time: '03:10',
        title: 'Tank 1 Inspection',
        description: 'Inspection A completes external visual and LiDAR scan',
        assetId: 'inspection-a',
        eventType: 'mapping',
        confidence: 0.86
      },
      {
        time: '05:45',
        title: 'Corrosion Detected',
        description: 'Detail C identifies possible corrosion on pipe joint',
        assetId: 'detail-c',
        eventType: 'sensor-detection',
        confidence: 0.71
      },
      {
        time: '08:20',
        title: 'EM Interference',
        description: 'Environmental B compass affected by machinery',
        assetId: 'environmental-b',
        eventType: 'failure'
      },
      {
        time: '11:30',
        title: 'Heat Exposure',
        description: 'Environmental B enters high-temperature zone',
        assetId: 'environmental-b',
        eventType: 'failure'
      },
      {
        time: '13:50',
        title: 'Vibration Anomaly',
        description: 'Monitoring node detects unusual vibration pattern',
        assetId: 'monitor-node-01',
        eventType: 'sensor-detection',
        confidence: 0.68
      },
      {
        time: '16:00',
        title: 'Duct Inspection',
        description: 'Detail C completes narrow duct section scan',
        assetId: 'detail-c',
        eventType: 'mapping',
        confidence: 0.79
      },
      {
        time: '18:10',
        title: 'AI Analysis Complete',
        description: 'Defect list and inspection confidence scores generated',
        eventType: 'ai-analysis',
        confidence: 0.74
      },
      {
        time: '19:30',
        title: 'Operator Review',
        description: 'Human review of corrosion and vibration findings',
        eventType: 'operator-review'
      },
      {
        time: '20:00',
        title: 'Mission Complete',
        description: 'Inspection coverage 84%, three defects flagged for maintenance',
        eventType: 'mission-end'
      }
    ],
    aiAnalyst: {
      role: 'Industrial Defect Analyst',
      promptSummary: 'Analyze visual, thermal, and vibration data to identify equipment defects and maintenance priorities',
      expectedFindings: [
        'Pipe joint corrosion in section 2 (confidence: 71%) - recommend closer inspection',
        'Tank 2 vibration pattern anomaly - possible bearing wear',
        'Thermal signature normal across all inspected equipment',
        'Duct obstruction in section 4 - reduced airflow risk'
      ],
      humanReviewRequired: true
    }
  }
];

/**
 * Get demo profile by slug
 * TODO: Replace with API call: GET /api/v1/missions/templates/{slug}/demo-profile
 */
export function getDemoProfileBySlug(slug: string): UseCaseDemoProfile | undefined {
  return useCaseDemoProfiles.find(profile => profile.slug === slug);
}

/**
 * Get all demo profile slugs
 */
export function getAllDemoSlugs(): string[] {
  return useCaseDemoProfiles.map(profile => profile.slug);
}
