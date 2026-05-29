/**
 * RescueMesh Use Case Profiles
 */
import type { UseCaseProfile } from '../types/usecases';

export const useCaseProfiles: UseCaseProfile[] = [
  {
    slug: 'collapsed-building',
    title: 'Collapsed Building Search',
    priority: 'Life Safety',
    missionObjective: 'Rapidly map unstable voids and detect signs of human presence in partially collapsed structures where traditional search methods are too dangerous or time-consuming.',
    terrainCharacteristics: {
      type: 'Collapsed building with unstable voids, rubble, and confined spaces',
      gps: 'Denied or unreliable inside structure',
      communications: 'Radio attenuation through concrete and steel',
      lighting: 'Dark with dust obscuration',
      hazards: ['Unstable structure', 'Sharp debris', 'Dust', 'Potential secondary collapse']
    },
    recommendedAgents: [
      {
        name: 'Survey Drone (Drone A)',
        role: 'Primary mapper with LiDAR and thermal imaging',
        description: 'Primary exploration and mapping agent for initial void assessment',
        capabilities: ['LiDAR for 3D mapping', 'Thermal camera', 'RGB camera', 'High endurance battery']
      },
      {
        name: 'Detection Drone (Drone B)',
        role: 'Specialized audio and life-sign detection',
        description: 'Audio and environmental sensor specialist for survivor detection',
        capabilities: ['Microphone array', 'CO2 sensor', 'WiFi/Bluetooth scanner', 'Relay capability']
      },
      {
        name: 'Deep Penetration (Drone C)',
        role: 'Small form factor for narrow passages',
        description: 'Compact drone for confined void penetration and priority streaming',
        capabilities: ['Compact design', 'Thermal camera', 'Audio sensor', 'NFC black-box module']
      },
      {
        name: 'Relay Node',
        role: 'Extended range communications bridge',
        description: 'Static communications and coordination hub',
        capabilities: ['High-power radio', 'Mesh networking', 'Battery or wired power', 'Environmental sensor']
      }
    ],
    expectedFailures: [
      {
        name: 'Dust Occlusion',
        description: 'LiDAR and camera quality degrades in dusty environments'
      },
      {
        name: 'Radio Packet Loss',
        description: 'Communications become intermittent through reinforced concrete'
      },
      {
        name: 'Battery Drain',
        description: 'Higher power consumption due to hovering in confined spaces'
      },
      {
        name: 'Tactical Relay Decision',
        description: 'Drone may land to serve as relay when battery is low and signal chain is weak'
      }
    ],
    expectedOutputs: [
      {
        name: '3D Void Map',
        description: 'Point cloud showing accessible spaces and obstructions'
      },
      {
        name: 'Thermal Anomalies',
        description: 'Heat signatures ranked by survivor probability'
      },
      {
        name: 'Audio Events',
        description: 'Voice-like sounds with confidence ratings'
      },
      {
        name: 'Device Scan',
        description: 'WiFi/Bluetooth signals from mobile phones'
      },
      {
        name: 'Relay Map',
        description: 'Network topology showing communications coverage'
      },
      {
        name: 'Access Routes',
        description: 'Recommended paths for human rescuers'
      },
      {
        name: 'AI Analysis',
        description: 'Prioritized detection list requiring human review'
      }
    ]
  },
  {
    slug: 'cave-rescue',
    title: 'Cave Rescue',
    priority: 'Life Safety / Navigation Safety',
    missionObjective: 'Map complex underground cave passages, identify safe routes, detect signs of trapped persons, and maintain communication links in GPS-denied, dark, humid, and irregular terrain.',
    terrainCharacteristics: {
      type: 'Natural cave system with tunnels, chambers, vertical shafts, narrow squeezes, uneven floors, water pools, and loose rock',
      gps: 'Fully denied underground',
      communications: 'Severe attenuation through rock; line-of-sight radio often unreliable',
      lighting: 'Complete darkness except drone-mounted illumination',
      hazards: ['Tight passages', 'Falling rock', 'Moisture', 'Water', 'Mud', 'Unstable footing', 'Low oxygen pockets', 'Disorientation risk']
    },
    recommendedAgents: [
      {
        name: 'Scout Drone (Drone A)',
        role: 'Primary exploration and route-mapping agent',
        description: 'Primary exploration and route-mapping agent for initial entry into unknown cave passages',
        capabilities: ['LiDAR or depth sensor for 3D passage mapping', 'Low-light RGB camera', 'Thermal camera', 'Obstacle avoidance', 'High-efficiency battery profile']
      },
      {
        name: 'Relay Drone (Drone B)',
        role: 'Communication chain maintainer',
        description: 'Maintains the communication chain between the cave entrance and deeper agents',
        capabilities: ['Mesh radio', 'Signal-strength monitoring', 'Autonomous landing mode', 'Low-power relay mode', 'NFC black-box module']
      },
      {
        name: 'Micro Mapper (Drone C)',
        role: 'Narrow passage specialist',
        description: 'Small form-factor drone for narrow passages, side chambers, and tight squeezes',
        capabilities: ['Compact protected frame', 'Short-range LiDAR/depth sensor', 'Audio sensor', 'Temperature and humidity sensor', 'Disposable / one-way mission mode']
      },
      {
        name: 'Ground Sensor Node',
        role: 'Static environmental and communications support',
        description: 'Static environmental and communications support node placed at key junctions',
        capabilities: ['Mesh repeater', 'Temperature and humidity sensor', 'Air quality sensor', 'Passive audio monitoring', 'Long-life battery']
      }
    ],
    expectedFailures: [
      {
        name: 'Rock Attenuation',
        description: 'Radio signals become weak or unavailable after bends, chambers, or deep rock sections'
      },
      {
        name: 'Moisture Degradation',
        description: 'Humidity, dripping water, or condensation may reduce sensor quality and increase electrical risk'
      },
      {
        name: 'Navigation Drift',
        description: 'SLAM confidence may decrease in repetitive or feature-poor tunnel sections'
      },
      {
        name: 'Confined-Space Collision',
        description: 'Narrow passages increase the likelihood of propeller strikes or protective cage contact'
      },
      {
        name: 'Tactical Relay Decision',
        description: 'A drone may land at a cave junction and become a static relay to preserve the communication path'
      }
    ],
    expectedOutputs: [
      {
        name: '3D Cave Passage Map',
        description: 'Point cloud or tunnel mesh showing chambers, shafts, obstructions, and traversable routes'
      },
      {
        name: 'Route Safety Estimate',
        description: 'Confidence-ranked routes for rescue teams'
      },
      {
        name: 'Thermal Anomalies',
        description: 'Heat signatures that may indicate humans, animals, or warm airflow'
      },
      {
        name: 'Audio Events',
        description: 'Voice-like sounds, movement, water flow, falling rock, or tapping patterns'
      },
      {
        name: 'Environmental Readings',
        description: 'Temperature, humidity, air quality, and possible low-oxygen risk indicators'
      },
      {
        name: 'Relay Map',
        description: 'Communication chain from cave entrance to deep exploration agents'
      },
      {
        name: 'Lost Asset Markers',
        description: 'Last known locations of landed, failed, or abandoned drones/nodes'
      },
      {
        name: 'AI Analysis',
        description: 'Suggested route priorities and human-review alerts'
      }
    ]
  },
  {
    slug: 'flooded-structure',
    title: 'Flooded Structure',
    priority: 'Life Safety / Environmental Hazard Assessment',
    missionObjective: 'Survey partially flooded buildings, tunnels, basements, underground car parks, culverts, or industrial spaces where water, debris, poor visibility, and electrical hazards make human access unsafe.',
    terrainCharacteristics: {
      type: 'Flooded or partially submerged built environment',
      gps: 'Denied indoors or underground',
      communications: 'Radio degraded by concrete, metal, and water; underwater communications extremely limited',
      lighting: 'Dark, reflective, and visually confusing due to water surfaces',
      hazards: ['Deep water', 'Floating debris', 'Submerged obstacles', 'Contamination', 'Electrical risk', 'Unstable surfaces', 'Trapped persons']
    },
    recommendedAgents: [
      {
        name: 'Surface Scout Drone (Drone A)',
        role: 'Aerial survey agent',
        description: 'Aerial survey agent for dry or partially flooded upper spaces',
        capabilities: ['RGB camera', 'Thermal camera', 'LiDAR/depth sensor', 'Spotlight', 'Water-resistant frame']
      },
      {
        name: 'Amphibious Micro Agent (Drone B)',
        role: 'Hybrid water-surface inspection',
        description: 'Hybrid or amphibious unit for shallow flooded areas, water-surface inspection, and low-clearance spaces',
        capabilities: ['Water-resistant or waterproof housing', 'Buoyancy support', 'Short-range sonar or depth sensor', 'Temperature sensor', 'NFC black-box module']
      },
      {
        name: 'Environmental Sensor Node',
        role: 'Static hazard monitoring',
        description: 'Static sensor node deployed near water entry points or hazard zones',
        capabilities: ['Water level sensor', 'Temperature sensor', 'Pressure sensor', 'Air quality sensor', 'Contamination indicator placeholder']
      },
      {
        name: 'Relay Node',
        role: 'Exterior-interior communications bridge',
        description: 'Maintains communication between exterior command and interior agents',
        capabilities: ['Mesh radio', 'High-position deployment mode', 'Battery or tethered power', 'Low-power survival mode']
      }
    ],
    expectedFailures: [
      {
        name: 'Water Damage',
        description: 'Sensors, motors, or electronics may degrade or fail due to splashing, immersion, or condensation'
      },
      {
        name: 'Reflection and Refraction Errors',
        description: 'LiDAR, camera, or depth readings may become unreliable near reflective water surfaces'
      },
      {
        name: 'Signal Loss',
        description: 'Radio communications may degrade rapidly through concrete, metal, and water-filled spaces'
      },
      {
        name: 'Buoyancy or Mobility Failure',
        description: 'Amphibious agents may become trapped by debris, tangled material, or narrow submerged gaps'
      },
      {
        name: 'Tactical Abandonment Decision',
        description: 'An amphibious unit may be left in place as a water-level monitor, beacon, or passive sensor if recovery is unsafe'
      }
    ],
    expectedOutputs: [
      {
        name: 'Flood Extent Map',
        description: 'Map layer showing dry, shallow, deep, and inaccessible zones'
      },
      {
        name: 'Depth / Pressure Readings',
        description: 'Approximate water depth and pressure changes by location'
      },
      {
        name: 'Thermal Anomalies',
        description: 'Possible human presence above waterline or behind obstructions'
      },
      {
        name: 'Submerged Obstruction Map',
        description: 'Sonar/depth-based estimate of underwater hazards'
      },
      {
        name: 'Environmental Alerts',
        description: 'Temperature, air quality, possible contamination, and electrical-risk notes'
      },
      {
        name: 'Asset Placement Map',
        description: 'Locations of relay nodes, amphibious agents, failed units, and static sensors'
      },
      {
        name: 'Access Route Suggestions',
        description: 'Safe or unsafe route estimates for rescuers'
      },
      {
        name: 'AI Analysis',
        description: 'Prioritised areas for human review, rescue entry, or further robotic inspection'
      }
    ]
  },
  {
    slug: 'industrial-inspection',
    title: 'Industrial Inspection',
    priority: 'Infrastructure Safety / Hazard Prevention',
    missionObjective: 'Inspect dangerous, confined, or hard-to-access industrial environments such as tanks, ducts, silos, utility tunnels, plant rooms, chimneys, warehouses, and processing facilities without exposing personnel to unnecessary risk.',
    terrainCharacteristics: {
      type: 'Industrial interior, confined space, plant room, tank, pipe gallery, ducting, or service tunnel',
      gps: 'Denied indoors or inside metal structures',
      communications: 'Interference from metal, machinery, concrete, and electromagnetic noise',
      lighting: 'Variable; may include dark spaces, glare, reflective surfaces, or steam/dust',
      hazards: ['Heat', 'Gas', 'Chemicals', 'Moving machinery', 'Confined-space entry risks', 'Sharp metal', 'Poor ventilation', 'Electrical equipment']
    },
    recommendedAgents: [
      {
        name: 'Inspection Drone (Drone A)',
        role: 'Primary visual and geometric inspection',
        description: 'Primary visual and geometric inspection agent',
        capabilities: ['RGB camera', 'LiDAR or depth sensor', 'Thermal camera', 'Protective cage', 'Stable hover mode']
      },
      {
        name: 'Environmental Drone (Drone B)',
        role: 'Environmental and hazard detection',
        description: 'Specialised agent for environmental and hazard detection',
        capabilities: ['Temperature sensor', 'Gas sensor placeholder', 'Humidity sensor', 'Pressure sensor', 'Audio/vibration sensor']
      },
      {
        name: 'Close-Range Detail Drone (Drone C)',
        role: 'Detailed surface inspection',
        description: 'Small drone for detailed inspection of pipes, ducts, cracks, corrosion points, and equipment surfaces',
        capabilities: ['Macro/close-range camera', 'Compact frame', 'LED lighting', 'NFC black-box module', 'Short-duration precision flight mode']
      },
      {
        name: 'Static Monitoring Node',
        role: 'Continuous hazard monitoring',
        description: 'Deployable node left behind for temporary monitoring of hazardous or unstable conditions',
        capabilities: ['Temperature sensor', 'Gas/air quality sensor placeholder', 'Vibration/acoustic sensor', 'Mesh relay', 'Long-life battery']
      }
    ],
    expectedFailures: [
      {
        name: 'Electromagnetic Interference',
        description: 'Industrial equipment may interfere with compass, radio, or sensor readings'
      },
      {
        name: 'Reflective Surface Confusion',
        description: 'Metal surfaces, tanks, glass, or water may reduce LiDAR/camera confidence'
      },
      {
        name: 'Heat or Gas Exposure',
        description: 'High temperatures, fumes, or poor air quality may degrade hardware or trigger early retreat'
      },
      {
        name: 'Confined-Space Collision',
        description: 'Narrow spaces, cables, beams, and pipework increase collision risk'
      },
      {
        name: 'Static Monitoring Decision',
        description: 'An agent or sensor node may be left in place to monitor vibration, temperature, or gas levels after the main inspection pass'
      }
    ],
    expectedOutputs: [
      {
        name: '3D Asset Map',
        description: 'Point cloud or model of tanks, ducts, machinery, pipework, and access spaces'
      },
      {
        name: 'Defect Indicators',
        description: 'Possible corrosion, cracks, obstructions, leaks, deformation, or abnormal heat'
      },
      {
        name: 'Thermal Map',
        description: 'Heat signatures around motors, panels, pipes, machinery, or confined spaces'
      },
      {
        name: 'Environmental Readings',
        description: 'Temperature, humidity, pressure, air quality, and gas-risk placeholders'
      },
      {
        name: 'Audio / Vibration Events',
        description: 'Unusual mechanical sounds, vibration patterns, or impact events'
      },
      {
        name: 'Inspection Confidence Score',
        description: 'Confidence level for each inspected zone or asset'
      },
      {
        name: 'Static Sensor Placement Map',
        description: 'Nodes left behind for continued monitoring'
      },
      {
        name: 'AI Analysis',
        description: 'Prioritised defect list, recommended human review points, and follow-up inspection actions'
      }
    ]
  }
];

/**
 * Get a use case profile by slug
 */
export function getUseCaseBySlug(slug: string): UseCaseProfile | undefined {
  return useCaseProfiles.find(profile => profile.slug === slug);
}

/**
 * Get all use case slugs
 */
export function getAllUseCaseSlugs(): string[] {
  return useCaseProfiles.map(profile => profile.slug);
}
