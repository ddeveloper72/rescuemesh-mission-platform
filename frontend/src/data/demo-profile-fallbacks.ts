/**
 * Fallback data for static demo pages when Django API is unavailable during build
 * 
 * This data is used during `npm run build` when the backend service isn't accessible.
 * At runtime (client-side), the real API will be used if available.
 */

import type { UseCaseDemoProfile } from '../types/demo';

export const demoProfileFallbacks: Record<string, UseCaseDemoProfile> = {
  'archaeological-exploration': {
    slug: 'archaeological-exploration',
    title: 'Archaeological Exploration',
    priority: 'Heritage Preservation / Site Safety',
    missionId: 'DEMO-ARCH-001',
    status: 'Simulated',
    missionObjective: 'Non-destructive mapping and documentation of fragile underground heritage spaces while keeping people, artefacts, and site fabric out of unnecessary risk.',
    terrain: {
      type: 'Underground chamber complex',
      gps: 'Denied (underground)',
      communications: 'Relay chain required',
      lighting: 'Dark (artificial lighting required)',
      hazards: ['Low oxygen zones', 'Unstable passages', 'Dust-sensitive surfaces', 'Cultural heritage preservation requirements']
    },
    agents: [
      {
        id: 'heritage-scout-a',
        name: 'Heritage Scout A',
        role: 'Primary Mapper',
        description: 'High-resolution LiDAR and low-light mapping agent',
        state: 'healthy',
        batteryPercent: 82,
        locationLabel: 'Chamber 2 - decorated wall zone',
        capabilities: ['3D mapping', 'Low-light navigation', 'No-contact survey'],
        sensors: ['LiDAR', 'Low-light camera', 'IMU', 'Humidity']
      },
      {
        id: 'micro-inspector-b',
        name: 'Micro Inspector B',
        role: 'Narrow Passage Survey',
        description: 'Compact agent for side passages and restricted voids',
        state: 'degraded',
        batteryPercent: 38,
        locationLabel: 'Side passage - north alcove',
        capabilities: ['Compact navigation', 'Close-range imaging', 'Artefact candidate marking'],
        sensors: ['Macro camera', 'Depth sensor', 'Temperature', 'Air quality']
      },
      {
        id: 'relay-node-arch-01',
        name: 'Relay Node ARCH-01',
        role: 'Communications Relay',
        description: 'Static relay positioned at the entry chamber threshold',
        state: 'landed_relay',
        batteryPercent: 91,
        locationLabel: 'Entry chamber',
        capabilities: ['Mesh relay', 'Environmental monitoring', 'Long-duration beacon'],
        sensors: ['Signal strength', 'Temperature', 'Humidity', 'CO2'],
        nfcRecoveryAvailable: true
      }
    ],
    expectedFailures: [
      {
        name: 'Dust-Sensitive Zone',
        affectedComponent: 'Navigation - Heritage Scout A',
        severity: 'medium',
        description: 'Agent speed reduced to avoid rotor wash near fragile deposits',
        dashboardEffect: 'Mapping rate reduced; conservation-safe mode enabled'
      },
      {
        name: 'Narrow Passage Signal Loss',
        affectedComponent: 'Communications - Micro Inspector B',
        severity: 'high',
        description: 'Packet loss increases through a curved side passage',
        dashboardEffect: 'Relay node holds entry threshold and Micro Inspector B pauses for operator review'
      }
    ],
    expectedOutputs: [
      {
        name: '3D Chamber Geometry',
        outputType: '3d-map',
        description: 'Detailed 3D point cloud of chambers',
        confidenceRequired: true
      },
      {
        name: 'Artefact Candidate Log',
        outputType: 'ai-analysis',
        description: 'Review-only list of possible artefacts, inscriptions, or decorated surfaces',
        confidenceRequired: true
      },
      {
        name: 'Environmental Readings',
        outputType: 'environmental',
        description: 'Temperature, humidity, oxygen, and CO2 trends around sensitive areas',
        confidenceRequired: false
      },
      {
        name: 'Conservation Route Notes',
        outputType: 'report',
        description: 'Suggested low-disturbance inspection route for human experts',
        confidenceRequired: true
      }
    ],
    simulation: {
      mapType: 'cave-map',
      environmentTags: ['underground', 'heritage', 'low-light'],
      defaultConfidence: 0.85,
      communicationRisk: 'high',
      batteryRisk: 'medium',
      sensorRisk: 'low',
      missionDurationMinutes: 16
    },
    timeline: [
      {
        time: '00:00',
        title: 'Mission Start',
        description: 'Heritage survey agents deployed at protected entrance line',
        eventType: 'mission-start'
      },
      {
        time: '03:10',
        title: 'Entry Chamber Mapped',
        description: 'Heritage Scout A completes first chamber geometry pass',
        assetId: 'heritage-scout-a',
        eventType: 'mapping',
        confidence: 0.88
      },
      {
        time: '05:40',
        title: 'Conservation-Safe Mode',
        description: 'Dust-sensitive zone detected near decorated surface',
        assetId: 'heritage-scout-a',
        eventType: 'failure'
      },
      {
        time: '08:20',
        title: 'Artefact Candidate',
        description: 'Micro Inspector B flags possible worked-stone edge for expert review',
        assetId: 'micro-inspector-b',
        eventType: 'sensor-detection',
        confidence: 0.63
      },
      {
        time: '11:30',
        title: 'Relay Hold',
        description: 'Relay node maintains entry chamber mesh link as side passage signal drops',
        assetId: 'relay-node-arch-01',
        eventType: 'relay'
      },
      {
        time: '14:20',
        title: 'AI Review Summary',
        description: 'AI analyst prepares conservation-first route and candidate list',
        eventType: 'ai-analysis',
        confidence: 0.76
      },
      {
        time: '16:00',
        title: 'Mission Profile Complete',
        description: 'Survey package ready for archaeologist and conservation review',
        eventType: 'mission-end'
      }
    ],
    aiAnalyst: {
      role: 'Heritage Documentation Assistant',
      promptSummary: 'Analyze chamber geometry, environmental data, and visual candidates while preserving human expert review for all archaeological interpretation',
      expectedFindings: [
        'Primary chamber geometry captured with high confidence',
        'Possible worked-stone edge flagged for expert review',
        'Dust-sensitive area requires low-disturbance access planning',
        'Relay position supports safe return path and data continuity'
      ],
      humanReviewRequired: true
    }
  },
  'collapsed-building-search': {
    slug: 'collapsed-building-search',
    title: 'Collapsed Building Search',
    priority: 'life-safety',
    missionId: 'DEMO-CBS-001',
    status: 'Simulated',
    missionObjective: 'Life safety search and rescue in structurally compromised urban collapse zones',
    terrain: {
      type: 'Collapsed building structure',
      gps: 'Available (degraded)',
      communications: 'Relay chain required',
      lighting: 'Variable',
      hazards: ['Structural instability', 'Dust clouds', 'Gas leaks', 'Sharp debris']
    },
    agents: [],
    expectedFailures: [],
    expectedOutputs: [],
    simulation: {
      mapType: 'void-map',
      environmentTags: ['urban', 'collapse', 'rescue'],
      defaultConfidence: 0.75,
      communicationRisk: 'high',
      batteryRisk: 'high',
      sensorRisk: 'high',
      missionDurationMinutes: 10
    },
    timeline: [],
    aiAnalyst: {
      role: 'Search and Rescue Assistant',
      promptSummary: 'Identify potential survivor locations',
      expectedFindings: ['Thermal anomalies', 'Audio signatures'],
      humanReviewRequired: true
    }
  },
  'cave-rescue': {
    slug: 'cave-rescue',
    title: 'Cave Rescue',
    priority: 'life-safety',
    missionId: 'DEMO-CAVE-001',
    status: 'Simulated',
    missionObjective: 'Search and path mapping in complex cave systems for lost or injured persons',
    terrain: {
      type: 'Natural cave system',
      gps: 'Denied (underground)',
      communications: 'Relay chain mandatory',
      lighting: 'Dark',
      hazards: ['Narrow passages', 'Water hazards', 'Vertical drops']
    },
    agents: [],
    expectedFailures: [],
    expectedOutputs: [],
    simulation: {
      mapType: 'cave-map',
      environmentTags: ['cave', 'underground', 'rescue'],
      defaultConfidence: 0.70,
      communicationRisk: 'severe',
      batteryRisk: 'high',
      sensorRisk: 'medium',
      missionDurationMinutes: 10
    },
    timeline: [],
    aiAnalyst: {
      role: 'Cave Navigation Assistant',
      promptSummary: 'Map safe passages and identify hazards',
      expectedFindings: ['Navigable routes', 'Hazard locations'],
      humanReviewRequired: true
    }
  },
  'flooded-structure': {
    slug: 'flooded-structure',
    title: 'Flooded Structure',
    priority: 'infrastructure',
    missionId: 'DEMO-FLOOD-001',
    status: 'Simulated',
    missionObjective: 'Underwater and amphibious inspection of flooded buildings and infrastructure',
    terrain: {
      type: 'Partially flooded structure',
      gps: 'Available (surface)',
      communications: 'RF attenuated underwater',
      lighting: 'Dark underwater',
      hazards: ['Water ingress risk', 'Low visibility', 'Submerged obstacles']
    },
    agents: [],
    expectedFailures: [],
    expectedOutputs: [],
    simulation: {
      mapType: 'flood-map',
      environmentTags: ['flooded', 'underwater', 'inspection'],
      defaultConfidence: 0.65,
      communicationRisk: 'severe',
      batteryRisk: 'medium',
      sensorRisk: 'high',
      missionDurationMinutes: 10
    },
    timeline: [],
    aiAnalyst: {
      role: 'Underwater Inspection Assistant',
      promptSummary: 'Assess structural damage and obstructions',
      expectedFindings: ['Damage locations', 'Water depth profile'],
      humanReviewRequired: true
    }
  },
  'industrial-inspection': {
    slug: 'industrial-inspection',
    title: 'Industrial Inspection',
    priority: 'safety',
    missionId: 'DEMO-IND-001',
    status: 'Simulated',
    missionObjective: 'Hazardous industrial site inspection without human entry',
    terrain: {
      type: 'Industrial facility',
      gps: 'Available',
      communications: 'Variable (metal structures)',
      lighting: 'Variable',
      hazards: ['Toxic gases', 'High temperature zones', 'Radiation', 'Chemical hazards']
    },
    agents: [],
    expectedFailures: [],
    expectedOutputs: [],
    simulation: {
      mapType: 'industrial-map',
      environmentTags: ['industrial', 'hazmat', 'inspection'],
      defaultConfidence: 0.80,
      communicationRisk: 'medium',
      batteryRisk: 'low',
      sensorRisk: 'high',
      missionDurationMinutes: 10
    },
    timeline: [],
    aiAnalyst: {
      role: 'Industrial Safety Assistant',
      promptSummary: 'Identify safety hazards and structural issues',
      expectedFindings: ['Gas concentrations', 'Temperature zones', 'Damage locations'],
      humanReviewRequired: true
    }
  }
};

export function getDemoProfileFallback(slug: string): UseCaseDemoProfile | null {
  return demoProfileFallbacks[slug] || null;
}
