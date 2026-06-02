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
    priority: 'heritage-preservation',
    missionId: 'DEMO-ARCH-001',
    status: 'Simulated',
    missionObjective: 'Non-destructive mapping and documentation of sensitive heritage sites using autonomous agents',
    terrain: {
      type: 'Underground chamber complex',
      gps: 'Denied (underground)',
      communications: 'Relay chain required',
      lighting: 'Dark (artificial lighting required)',
      hazards: ['Low oxygen zones', 'Unstable passages', 'Cultural heritage preservation requirements']
    },
    agents: [
      {
        id: 'arch-drone-1',
        name: 'LiDAR Mapping Drone A',
        role: 'Primary Mapper',
        description: 'High-resolution LiDAR mapping',
        state: 'healthy',
        batteryPercent: 85,
        locationLabel: 'Chamber 2',
        capabilities: ['3D mapping', 'Low-light navigation'],
        sensors: ['LiDAR', 'Low-light camera', 'IMU']
      }
    ],
    expectedFailures: [
      {
        name: 'Battery Drain',
        affectedComponent: 'Power System',
        severity: 'medium',
        description: 'Battery depletes faster than expected',
        dashboardEffect: 'Reduced mission duration'
      }
    ],
    expectedOutputs: [
      {
        name: '3D Chamber Geometry',
        outputType: '3d-map',
        description: 'Detailed 3D point cloud of chambers',
        confidenceRequired: true
      }
    ],
    simulation: {
      mapType: 'cave-map',
      environmentTags: ['underground', 'heritage', 'low-light'],
      defaultConfidence: 0.85,
      communicationRisk: 'medium',
      batteryRisk: 'medium',
      sensorRisk: 'low',
      missionDurationMinutes: 10
    },
    timeline: [
      {
        time: '0:00',
        title: 'Mission Start',
        description: 'Agents deployed at entrance'
      }
    ],
    aiAnalyst: {
      role: 'Heritage Documentation Assistant',
      promptSummary: 'Analyze chamber geometry and identify artifacts',
      expectedFindings: ['Chamber dimensions', 'Artifact locations'],
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
  'flooded-structure-inspection': {
    slug: 'flooded-structure-inspection',
    title: 'Flooded Structure Inspection',
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
