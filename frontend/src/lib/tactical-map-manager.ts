/**
 * Tactical Map Manager
 * 
 * Renders and updates SVG tactical maps based on mission state.
 * Use-case specific layouts for different simulation types.
 * 
 * Now includes animated agent movement, progressive sector reveal,
 * and time-based detection markers.
 */

import type { MissionSimulationState, Agent } from '../types/simulation';

interface MapConfig {
  sectors: TacticalSector[];
  hazardZones?: HazardZone[];
  width: number;
  height: number;
  routes?: TacticalAgentRoute[];
  detectionMarkers?: DetectionMarker[];
}

interface Sector {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  type?: 'accessible' | 'blocked' | 'void' | 'water' | 'hazard';
}

interface TacticalSector extends Sector {
  revealAt: number; // simulated elapsed seconds
  confidenceAtReveal?: number;
}

interface HazardZone {
  id: string;
  x: number;
  y: number;
  radius: number;
  type: 'thermal' | 'gas' | 'electrical' | 'pressure';
}

export interface TacticalWaypoint {
  time: number; // simulated elapsed seconds
  x: number;
  y: number;
  sectorId: string;
  label?: string;
}

export interface TacticalAgentRoute {
  agentId: string;
  startsAt: number;
  route: TacticalWaypoint[];
  leavesAssetBehind?: {
    time: number;
    assetId: string;
    label: string;
    x: number;
    y: number;
    state: 'relay' | 'static_sensor' | 'failed' | 'nfc_readable' | 'sacrificed';
  };
}

export interface DetectionMarker {
  id: string;
  type: 'thermal' | 'audio' | 'gas' | 'electrical' | 'pressure';
  x: number;
  y: number;
  appearsAt: number; // simulated elapsed seconds
  label: string;
  icon: string;
}

/**
 * Industrial Inspection Map Configuration
 */
export function getIndustrialInspectionMapConfig(): MapConfig {
  const sectors: TacticalSector[] = [
    { id: 'entry', label: 'Entry Point', x: 50, y: 50, width: 120, height: 80, type: 'accessible', revealAt: 0 },
    { id: 'plant-room', label: 'Plant Room', x: 50, y: 150, width: 180, height: 120, type: 'accessible', revealAt: 30 },
    { id: 'pipe-gallery', label: 'Pipe Gallery', x: 250, y: 150, width: 200, height: 120, type: 'accessible', revealAt: 90 },
    { id: 'duct-section', label: 'Duct Section', x: 470, y: 150, width: 150, height: 120, type: 'accessible', revealAt: 150 },
    { id: 'control-cabinet', label: 'Control Cabinet', x: 640, y: 150, width: 110, height: 120, type: 'accessible', revealAt: 210 },
    { id: 'tank-interior', label: 'Tank Interior', x: 250, y: 290, width: 200, height: 110, type: 'hazard', revealAt: 120 },
  ];

  const routes: TacticalAgentRoute[] = [
    {
      agentId: 'inspector',  // Matches "Industrial Inspector" and "inspection-drone-a"
      startsAt: 30,
      route: [
        { time: 30, x: 110, y: 90, sectorId: 'entry', label: 'Start' },
        { time: 60, x: 140, y: 210, sectorId: 'plant-room', label: 'Plant Room inspection' },
        { time: 120, x: 350, y: 210, sectorId: 'pipe-gallery', label: 'Pipe Gallery scan' },
        { time: 180, x: 545, y: 210, sectorId: 'duct-section', label: 'Duct Section' },
        { time: 240, x: 695, y: 210, sectorId: 'control-cabinet', label: 'Control Cabinet' },
      ]
    },
    {
      agentId: 'monitor',  // Matches "Plant Room Monitor"
      startsAt: 120,
      route: [
        { time: 120, x: 110, y: 90, sectorId: 'entry', label: 'Deploy' },
        { time: 130, x: 140, y: 210, sectorId: 'plant-room', label: 'Station' },
      ],
      leavesAssetBehind: {
        time: 130,
        assetId: 'plant-room-monitor',
        label: 'Monitoring Node',
        x: 140,
        y: 210,
        state: 'static_sensor'
      }
    },
    {
      agentId: 'thermal',  // Matches "Thermal Specialist"
      startsAt: 240,
      route: [
        { time: 240, x: 110, y: 90, sectorId: 'entry', label: 'Thermal deploy' },
        { time: 270, x: 350, y: 210, sectorId: 'pipe-gallery', label: 'Thermal scan' },
        { time: 330, x: 545, y: 210, sectorId: 'duct-section', label: 'Hotspot investigation' },
        { time: 390, x: 695, y: 210, sectorId: 'control-cabinet', label: 'Critical thermal' },
      ]
    },
  ];

  const detectionMarkers: DetectionMarker[] = [
    { id: 'thermal-pipe-joint', type: 'thermal', x: 380, y: 240, appearsAt: 150, label: 'Pipe Joint A3', icon: 'T' },
    { id: 'gas-methane', type: 'gas', x: 320, y: 180, appearsAt: 180, label: 'Methane', icon: 'G' },
    { id: 'pressure-leak', type: 'pressure', x: 520, y: 200, appearsAt: 390, label: 'Pressure leak', icon: 'P' },
    { id: 'thermal-critical', type: 'thermal', x: 680, y: 190, appearsAt: 450, label: 'Control Cabinet C2', icon: 'T' },
  ];

  return {
    width: 800,
    height: 450,
    sectors,
    routes,
    detectionMarkers,
  };
}

/** * Archaeological Exploration Map Configuration
 * Progressive chamber discovery with fragile zone warnings
 */
export function getArchaeologicalExplorationMapConfig(): MapConfig {
  const sectors: TacticalSector[] = [
    { id: 'entry-chamber', label: 'Entry Chamber', x: 50, y: 180, width: 120, height: 100, type: 'accessible', revealAt: 60 },
    { id: 'first-chamber', label: 'First Chamber', x: 190, y: 170, width: 160, height: 120, type: 'accessible', revealAt: 180 },
    { id: 'transition-passage', label: 'Transition Passage', x: 370, y: 210, width: 140, height: 50, type: 'hazard', revealAt: 300 },
    { id: 'narrow-passage', label: 'Narrow Passage', x: 530, y: 220, width: 80, height: 30, type: 'hazard', revealAt: 360 },
    { id: 'second-chamber', label: 'Second Chamber', x: 630, y: 160, width: 140, height: 130, type: 'accessible', revealAt: 480 },
  ];

  const routes: TacticalAgentRoute[] = [
    {
      agentId: 'micro-scout',  // Micro Scout Drone
      startsAt: 60,
      route: [
        { time: 60, x: 110, y: 230, sectorId: 'entry-chamber', label: 'Initial entry' },
        { time: 120, x: 270, y: 230, sectorId: 'first-chamber', label: 'First chamber rough scan' },
        { time: 240, x: 440, y: 235, sectorId: 'transition-passage', label: 'Transition passage' },
        { time: 360, x: 570, y: 235, sectorId: 'narrow-passage', label: 'Narrow passage navigation' },
        { time: 450, x: 570, y: 235, sectorId: 'narrow-passage', label: 'Stranded - NFC available' },
      ]
    },
    {
      agentId: 'lidar-mapper',  // LiDAR Mapping Drone
      startsAt: 180,
      route: [
        { time: 180, x: 110, y: 230, sectorId: 'entry-chamber', label: 'Deploy for detailed scan' },
        { time: 240, x: 270, y: 230, sectorId: 'first-chamber', label: 'High-fidelity first chamber' },
        { time: 360, x: 440, y: 235, sectorId: 'transition-passage', label: 'Passage mapping' },
        { time: 480, x: 700, y: 225, sectorId: 'second-chamber', label: 'Second chamber discovery' },
        { time: 600, x: 700, y: 225, sectorId: 'second-chamber', label: 'Detailed reconstruction' },
      ]
    },
    {
      agentId: 'imaging-drone',  // Low-Light Imaging Drone
      startsAt: 300,
      route: [
        { time: 300, x: 110, y: 230, sectorId: 'entry-chamber', label: 'Deploy for documentation' },
        { time: 360, x: 270, y: 230, sectorId: 'first-chamber', label: 'Visual documentation' },
        { time: 480, x: 700, y: 225, sectorId: 'second-chamber', label: 'Second chamber photography' },
      ]
    },
  ];

  const detectionMarkers: DetectionMarker[] = [
    { id: 'artefact-wall', type: 'artefact', x: 300, y: 180, appearsAt: 240, label: 'Possible wall marking', icon: 'A' },
    { id: 'artefact-floor', type: 'artefact', x: 450, y: 250, appearsAt: 420, label: 'Possible ceramic fragment', icon: 'A' },
  ];

  return {
    width: 800,
    height: 450,
    sectors,
    routes,
    detectionMarkers,
  };
}

/** * Collapsed Building Map Configuration
 */
export function getCollapsedBuildingMapConfig(): MapConfig {
  const sectors: TacticalSector[] = [
    { id: 'entry', label: 'Entry', x: 50, y: 200, width: 100, height: 80, type: 'accessible', revealAt: 0 },
    { id: 'corridor-a', label: 'Corridor A', x: 170, y: 200, width: 150, height: 80, type: 'accessible', revealAt: 30 },
    { id: 'void-1', label: 'Void Space 1', x: 340, y: 140, width: 180, height: 120, type: 'void', revealAt: 120 },
    { id: 'corridor-b', label: 'Corridor B', x: 340, y: 280, width: 180, height: 100, type: 'accessible', revealAt: 90 },
    { id: 'collapsed', label: 'Collapsed Section', x: 540, y: 180, width: 200, height: 140, type: 'blocked', revealAt: 180 },
  ];

  const routes: TacticalAgentRoute[] = [
    {
      agentId: 'scout',  // Matches "Scout Drone A"
      startsAt: 30,
      route: [
        { time: 30, x: 100, y: 240, sectorId: 'entry', label: 'Start' },
        { time: 60, x: 245, y: 240, sectorId: 'corridor-a', label: 'Mapping' },
        { time: 120, x: 430, y: 200, sectorId: 'void-1', label: 'Void exploration' },
        { time: 240, x: 430, y: 200, sectorId: 'void-1', label: 'Deep scan' },
      ]
    },
    {
      agentId: 'thermal',  // Matches "Thermal/Audio Drone"
      startsAt: 60,
      route: [
        { time: 60, x: 100, y: 240, sectorId: 'entry', label: 'Deploy' },
        { time: 120, x: 245, y: 240, sectorId: 'corridor-a', label: 'Scan' },
        { time: 210, x: 430, y: 330, sectorId: 'corridor-b', label: 'Detection' },
        { time: 360, x: 430, y: 330, sectorId: 'corridor-b', label: 'Relay position' },
      ],
      leavesAssetBehind: {
        time: 360,
        assetId: 'thermal-audio-drone',
        label: 'Relay (Battery critical)',
        x: 430,
        y: 330,
        state: 'relay'
      }
    },
    {
      agentId: 'relay',  // Matches "Relay Drone"
      startsAt: 90,
      route: [
        { time: 90, x: 100, y: 240, sectorId: 'entry', label: 'Deploy relay' },
        { time: 150, x: 200, y: 240, sectorId: 'corridor-a', label: 'Relay position' },
      ],
      leavesAssetBehind: {
        time: 150,
        assetId: 'relay-drone',
        label: 'Sacrificed Relay',
        x: 200,
        y: 240,
        state: 'sacrificed'
      }
    },
  ];

  const detectionMarkers: DetectionMarker[] = [
    { id: 'thermal-void', type: 'thermal', x: 450, y: 200, appearsAt: 180, label: 'Heat signature', icon: 'T' },
    { id: 'audio-voice', type: 'audio', x: 470, y: 220, appearsAt: 240, label: 'Voice-like audio', icon: 'A' },
  ];

  return {
    width: 800,
    height: 450,
    sectors,
    routes,
    detectionMarkers,
  };
}

/**
 * Cave Rescue Map Configuration
 * 
 * Per claude_prompt09.md: All agents must start from entrance-chamber.
 * No agent should spawn directly in Narrow Passage or Deep Squeeze.
 * Routes show progression: Entrance → Main Tunnel → Narrow Passage → Junction → Deep Squeeze
 */
export function getCaveRescueMapConfig(): MapConfig {
  const sectors: TacticalSector[] = [
    { id: 'entrance-chamber', label: 'Entrance Chamber', x: 50, y: 180, width: 140, height: 120, type: 'accessible', revealAt: 0 },
    { id: 'main-tunnel', label: 'Main Tunnel', x: 210, y: 200, width: 180, height: 80, type: 'accessible', revealAt: 60 },
    { id: 'narrow-passage', label: 'Narrow Passage', x: 410, y: 220, width: 100, height: 40, type: 'hazard', revealAt: 120 },
    { id: 'junction-chamber', label: 'Junction Chamber', x: 530, y: 160, width: 140, height: 140, type: 'accessible', revealAt: 180 },
    { id: 'deep-squeeze', label: 'Deep Squeeze', x: 690, y: 200, width: 60, height: 80, type: 'blocked', revealAt: 300 },
  ];

  const routes: TacticalAgentRoute[] = [
    {
      agentId: 'scout',  // Matches "Cave Scout Drone" (drone-a)
      startsAt: 30,
      route: [
        { time: 30, x: 120, y: 240, sectorId: 'entrance-chamber', label: 'Start from entrance' },
        { time: 60, x: 300, y: 240, sectorId: 'main-tunnel', label: 'Map main tunnel' },
        { time: 120, x: 460, y: 240, sectorId: 'narrow-passage', label: 'Detect narrow passage' },
        { time: 180, x: 600, y: 230, sectorId: 'junction-chamber', label: 'Discover junction' },
        { time: 300, x: 720, y: 240, sectorId: 'deep-squeeze', label: 'Enter deep squeeze' },
        { time: 420, x: 720, y: 240, sectorId: 'deep-squeeze', label: 'Audio detection scan' },
      ]
    },
    {
      agentId: 'micro',  // Matches "Micro Mapper" (drone-b)
      startsAt: 90,
      route: [
        { time: 90, x: 120, y: 240, sectorId: 'entrance-chamber', label: 'Deploy from entrance' },
        { time: 120, x: 300, y: 240, sectorId: 'main-tunnel', label: 'Follow mapped route' },
        { time: 180, x: 460, y: 240, sectorId: 'narrow-passage', label: 'Narrow passage exploration' },
        { time: 240, x: 460, y: 240, sectorId: 'narrow-passage', label: 'Lost - NFC available' },
      ]
    },
    {
      agentId: 'relay',  // Matches "Junction Relay Drone" (relay-1)
      startsAt: 180,
      route: [
        { time: 180, x: 120, y: 240, sectorId: 'entrance-chamber', label: 'Deploy relay' },
        { time: 210, x: 300, y: 240, sectorId: 'main-tunnel', label: 'Travel to junction' },
        { time: 240, x: 600, y: 230, sectorId: 'junction-chamber', label: 'Position at junction' },
        { time: 300, x: 600, y: 230, sectorId: 'junction-chamber', label: 'Landed relay mode' },
      ],
      leavesAssetBehind: {
        time: 300,
        assetId: 'junction-relay',
        label: 'Junction Relay (static)',
        x: 600,
        y: 230,
        state: 'relay'
      }
    },
  ];

  const detectionMarkers: DetectionMarker[] = [
    { id: 'audio-tap', type: 'audio', x: 720, y: 250, appearsAt: 420, label: 'Tapping sounds', icon: 'A' },
    { id: 'audio-voice', type: 'audio', x: 720, y: 220, appearsAt: 480, label: 'Voice-like audio', icon: 'A' },
  ];

  return {
    width: 800,
    height: 450,
    sectors,
    routes,
    detectionMarkers,
  };
}

/**
 * Flooded Structure Map Configuration
 */
export function getFloodedStructureMapConfig(): MapConfig {
  const sectors: TacticalSector[] = [
    { id: 'entry-pool', label: 'Entry Pool (surface)', x: 50, y: 50, width: 150, height: 80, type: 'water', revealAt: 0 },
    { id: 'flooded-corridor', label: 'Flooded Corridor', x: 220, y: 50, width: 200, height: 150, type: 'water', revealAt: 60 },
    { id: 'plant-room', label: 'Plant Room (shallow)', x: 440, y: 50, width: 150, height: 150, type: 'water', revealAt: 120 },
    { id: 'submerged-zone', label: 'Submerged Zone', x: 220, y: 220, width: 370, height: 180, type: 'hazard', revealAt: 180 },
  ];

  const routes: TacticalAgentRoute[] = [
    {
      agentId: 'amphibious',  // Matches "Amphibious Explorer"
      startsAt: 30,
      route: [
        { time: 30, x: 125, y: 90, sectorId: 'entry-pool', label: 'Surface start' },
        { time: 90, x: 320, y: 125, sectorId: 'flooded-corridor', label: 'Shallow scan' },
        { time: 180, x: 515, y: 125, sectorId: 'plant-room', label: 'Plant room' },
        { time: 270, x: 405, y: 310, sectorId: 'submerged-zone', label: 'Deep dive' },
      ]
    },
  ];

  const detectionMarkers: DetectionMarker[] = [
    { id: 'electrical-hazard', type: 'electrical', x: 280, y: 150, appearsAt: 120, label: 'Electrical hazard', icon: 'E' },
    { id: 'thermal-above-water', type: 'thermal', x: 480, y: 80, appearsAt: 210, label: 'Thermal anomaly', icon: 'T' },
  ];

  return {
    width: 800,
    height: 450,
    sectors,
    routes,
    detectionMarkers,
  };
}

/**
 * Get map configuration by use case
 */
export function getMapConfig(useCase: string): MapConfig {
  switch (useCase) {
    case 'industrial-inspection':
      return getIndustrialInspectionMapConfig();
    case 'collapsed-building-search':
      return getCollapsedBuildingMapConfig();
    case 'cave-rescue':
      return getCaveRescueMapConfig();
    case 'flooded-structure':
      return getFloodedStructureMapConfig();
    case 'archaeological-exploration':
      return getArchaeologicalExplorationMapConfig();
    default:
      return { width: 800, height: 450, sectors: [] };
  }
}

/**
 * Interpolate position between two waypoints based on current time
 */
function interpolatePosition(
  current: TacticalWaypoint,
  next: TacticalWaypoint,
  currentTime: number
): { x: number; y: number } {
  const timeDelta = next.time - current.time;
  if (timeDelta <= 0) return { x: current.x, y: current.y };
  
  const progress = Math.min(1, (currentTime - current.time) / timeDelta);
  
  return {
    x: current.x + (next.x - current.x) * progress,
    y: current.y + (next.y - current.y) * progress,
  };
}

/**
 * Get agent position at specific time from route
 */
function getAgentPositionAtTime(route: TacticalAgentRoute, time: number): { x: number; y: number; stopped: boolean } | null {
  if (time < route.startsAt) {
    return null; // Agent hasn't started yet
  }

  // Check if agent leaves asset behind and should stop
  if (route.leavesAssetBehind && time >= route.leavesAssetBehind.time) {
    return {
      x: route.leavesAssetBehind.x,
      y: route.leavesAssetBehind.y,
      stopped: true,
    };
  }

  // Find current position on route
  const waypoints = route.route;
  
  // If before first waypoint, stay at start
  if (time < waypoints[0].time) {
    return { x: waypoints[0].x, y: waypoints[0].y, stopped: false };
  }

  // If after last waypoint, stay at end
  if (time >= waypoints[waypoints.length - 1].time) {
    const last = waypoints[waypoints.length - 1];
    return { x: last.x, y: last.y, stopped: false };
  }

  // Find the two waypoints to interpolate between
  for (let i = 0; i < waypoints.length - 1; i++) {
    const current = waypoints[i];
    const next = waypoints[i + 1];
    
    if (time >= current.time && time < next.time) {
      return { ...interpolatePosition(current, next, time), stopped: false };
    }
  }

  // Fallback to last position
  const last = waypoints[waypoints.length - 1];
  return { x: last.x, y: last.y, stopped: false };
}

/**
 * Render sectors on the map with progressive reveal
 */
export function renderSectors(
  config: MapConfig,
  currentTime: number,
  terrainReconstruction?: { sectors: any[] }
) {
  const sectorsGroup = document.getElementById('map-sectors');
  if (!sectorsGroup) return;

  sectorsGroup.innerHTML = config.sectors.map(sector => {
    // Try to find terrain reconstruction state for this sector
    let sectorState = null;
    if (terrainReconstruction) {
      sectorState = terrainReconstruction.sectors.find(
        (s: any) => s.sector_id === sector.id
      );
    }

    // Use terrain reconstruction if available, otherwise fallback to revealAt timing
    let fillColor = 'rgba(71, 85, 105, 0.3)'; // slate-600 default
    let strokeColor = 'rgba(148, 163, 184, 0.5)'; // slate-400
    let opacity = 0.15;
    let labelOpacity = 0.3;
    let label = '???';
    let strokeWidth = 2;
    
    if (sectorState) {
      // Use terrain reconstruction state
      const status = sectorState.status;
      const confidence = sectorState.confidence || 0;
      
      if (status === 'unknown') {
        opacity = 0.05;
        labelOpacity = 0.15;
        label = '???';
      } else if (status === 'detected') {
        opacity = 0.3;
        labelOpacity = 0.5;
        label = `${sector.label} (${confidence}%)`;
        strokeColor = 'rgba(148, 163, 184, 0.7)';
        strokeWidth = 1;
      } else if (status === 'partially_mapped') {
        opacity = 0.5;
        labelOpacity = 0.7;
        label = `${sector.label} (${confidence}%)`;
        strokeWidth = 2;
      } else if (status === 'mapped') {
        opacity = 0.8;
        labelOpacity = 1.0;
        label = sector.label;
        strokeWidth = 2;
      } else if (status === 'high_confidence') {
        opacity = 1.0;
        labelOpacity = 1.0;
        label = sector.label;
        strokeWidth = 3;
        strokeColor = 'rgba(148, 163, 184, 0.9)';
      } else if (status === 'hazardous') {
        opacity = 1.0;
        labelOpacity = 1.0;
        label = `[!] ${sector.label}`;
        fillColor = 'rgba(133, 77, 14, 0.4)';
        strokeColor = 'rgba(252, 211, 77, 0.8)';
        strokeWidth = 3;
      } else if (status === 'blocked') {
        opacity = 1.0;
        labelOpacity = 1.0;
        label = `[X] ${sector.label}`;
        fillColor = 'rgba(153, 27, 27, 0.4)';
        strokeColor = 'rgba(252, 165, 165, 0.8)';
        strokeWidth = 3;
      }
    } else {
      // Fallback to revealAt timing
      opacity = currentTime >= sector.revealAt ? 1.0 : 0.15;
      labelOpacity = currentTime >= sector.revealAt ? 1.0 : 0.3;
      label = currentTime >= sector.revealAt ? sector.label : '???';
      
      if (sector.type === 'blocked') {
        fillColor = 'rgba(153, 27, 27, 0.3)';
        strokeColor = 'rgba(252, 165, 165, 0.5)';
      } else if (sector.type === 'void') {
        fillColor = 'rgba(88, 28, 135, 0.3)';
        strokeColor = 'rgba(216, 180, 254, 0.5)';
      } else if (sector.type === 'water') {
        fillColor = 'rgba(12, 74, 110, 0.3)';
        strokeColor = 'rgba(103, 232, 249, 0.5)';
      } else if (sector.type === 'hazard') {
        fillColor = 'rgba(133, 77, 14, 0.3)';
        strokeColor = 'rgba(252, 211, 77, 0.5)';
      }
    }

    return `
      <rect 
        id="sector-${sector.id}"
        class="sector-area"
        x="${sector.x}" 
        y="${sector.y}" 
        width="${sector.width}" 
        height="${sector.height}"
        fill="${fillColor}"
        stroke="${strokeColor}"
        stroke-width="${strokeWidth}"
        rx="4"
        opacity="${opacity}"
      />
      <text 
        x="${sector.x + sector.width / 2}" 
        y="${sector.y + sector.height / 2}"
        text-anchor="middle"
        dominant-baseline="middle"
        class="text-xs"
        fill="#e2e8f0"
        opacity="${labelOpacity}"
      >${label}</text>
    `;
  }).join('');
}

/**
 * Update agent markers on the map using route-based positioning
 */
export function updateAgents(agents: Agent[], config: MapConfig, currentTime: number) {
  const agentsGroup = document.getElementById('map-agents');
  if (!agentsGroup) return;

  const elements: string[] = [];

  // Render path trails for each route
  if (config.routes) {
    config.routes.forEach(route => {
      const pos = getAgentPositionAtTime(route, currentTime);
      if (!pos) return;

      // Draw path trail from start to current position
      const pathPoints: string[] = [];
      for (const waypoint of route.route) {
        if (waypoint.time <= currentTime) {
          pathPoints.push(`${waypoint.x},${waypoint.y}`);
        }
      }

      if (pathPoints.length > 1) {
        elements.push(`
          <polyline
            points="${pathPoints.join(' ')}"
            fill="none"
            stroke="rgba(148, 163, 184, 0.3)"
            stroke-width="2"
            stroke-dasharray="5,5"
          />
        `);
      }
    });
  }

  // Render left-behind assets
  if (config.routes) {
    config.routes.forEach(route => {
      if (route.leavesAssetBehind && currentTime >= route.leavesAssetBehind.time) {
        const asset = route.leavesAssetBehind;
        let color = '#a855f7'; // purple-500 for relay/sacrificed
        if (asset.state === 'failed') color = '#ef4444'; // red-500
        if (asset.state === 'static_sensor') color = '#3b82f6'; // blue-500

        elements.push(`
          <g class="asset-marker">
            <rect
              x="${asset.x - 6}"
              y="${asset.y - 6}"
              width="12"
              height="12"
              fill="${color}"
              stroke="#1e293b"
              stroke-width="2"
              rx="2"
            />
            <title>${asset.label}</title>
          </g>
        `);
      }
    });
  }

  // Render active agents
  agents.forEach(agent => {
    let pos: { x: number; y: number; stopped: boolean } | null = null;

    // Try to find position from route with flexible matching
    if (config.routes) {
      const agentIdLower = agent.agent_id.toLowerCase();
      const agentNameLower = agent.name.toLowerCase();
      
      const route = config.routes.find(r => {
        const routeIdLower = r.agentId.toLowerCase();
        return (
          agentIdLower.includes(routeIdLower) || 
          routeIdLower.includes(agentIdLower) ||
          agentNameLower.includes(routeIdLower) ||
          routeIdLower.includes(agentNameLower) ||
          // Try word matching
          agentNameLower.split(/\s+/).some(word => routeIdLower.includes(word)) ||
          routeIdLower.split(/[-_\s]+/).some(word => agentNameLower.includes(word))
        );
      });
      
      if (route) {
        pos = getAgentPositionAtTime(route, currentTime);
      }
    }

    // If no route found, use fallback position
    if (!pos) {
      const location = agent.location_label.toLowerCase();
      let sector = config.sectors.find(s => 
        location.includes(s.id) || location.includes(s.label.toLowerCase())
      );
      
      if (!sector) {
        sector = config.sectors[0];
      }

      pos = {
        x: sector.x + sector.width / 2,
        y: sector.y + sector.height / 2,
        stopped: false,
      };
    }

    // Don't render if agent hasn't started yet
    if (!pos) return;

    // Color based on agent state
    let color = '#10b981'; // green-500 for active/healthy
    if (agent.state === 'degraded' || agent.state === 'intermittent') {
      color = '#eab308'; // yellow-500
    } else if (agent.state === 'failed' || agent.state === 'lost') {
      color = '#ef4444'; // red-500
    } else if (agent.state === 'landed_relay' || agent.state === 'sacrificed') {
      color = '#a855f7'; // purple-500
    }

    // Add scan pulse for active agents
    const showPulse = !pos.stopped && 
      (agent.state === 'healthy' || agent.state === 'active' || agent.state === 'degraded');

    elements.push(`
      <g id="agent-${agent.agent_id}" class="agent-marker">
        ${showPulse ? `
          <circle 
            cx="${pos.x}" 
            cy="${pos.y}" 
            r="12"
            fill="none"
            stroke="${color}"
            stroke-width="1.5"
            opacity="0.4"
          >
            <animate
              attributeName="r"
              from="8"
              to="16"
              dur="2s"
              repeatCount="indefinite"
            />
            <animate
              attributeName="opacity"
              from="0.6"
              to="0"
              dur="2s"
              repeatCount="indefinite"
            />
          </circle>
        ` : ''}
        <circle 
          cx="${pos.x}" 
          cy="${pos.y}" 
          r="8"
          fill="${color}"
          stroke="#1e293b"
          stroke-width="2"
        />
        <title>${agent.name} - ${agent.state} (Battery: ${agent.battery_percent}%)</title>
      </g>
    `);
  });

  agentsGroup.innerHTML = elements.join('');
}

/**
 * Render detection markers (thermal, gas, etc.) - only after their appear time
 */
export function renderDetectionMarkers(config: MapConfig, currentTime: number) {
  const markersGroup = document.getElementById('map-hazards');
  if (!markersGroup) return;

  const markers: string[] = [];

  if (config.detectionMarkers) {
    config.detectionMarkers.forEach(marker => {
      if (currentTime >= marker.appearsAt) {
        let color = '#ef4444'; // red for thermal
        if (marker.type === 'gas') color = '#eab308'; // yellow
        if (marker.type === 'electrical') color = '#3b82f6'; // blue
        if (marker.type === 'audio') color = '#8b5cf6'; // purple
        if (marker.type === 'pressure') color = '#06b6d4'; // cyan

        markers.push(`
          <g class="detection-marker cursor-pointer hover:opacity-80 transition-opacity" data-detection-id="${marker.id}" data-detection-type="${marker.type}">
            <circle 
              cx="${marker.x}" 
              cy="${marker.y}" 
              r="14"
              fill="rgba(239, 68, 68, 0.2)"
              stroke="${color}"
              stroke-width="2"
            />
            <text 
              x="${marker.x}" 
              y="${marker.y + 22}" 
              text-anchor="middle" 
              class="text-xs pointer-events-none"
              fill="#e2e8f0"
              style="font-size: 16px;"
            >${marker.icon}</text>
            <title>${marker.label} - Click for details</title>
          </g>
        `);
      }
    });
  }

  markersGroup.innerHTML = markers.join('');
  
  // Add click handlers to detection markers
  attachDetectionMarkerClickHandlers();
}

/**
 * Attach click handlers to detection markers
 */
function attachDetectionMarkerClickHandlers() {
  const markers = document.querySelectorAll('.detection-marker');
  
  markers.forEach(marker => {
    marker.addEventListener('click', (event) => {
      const target = event.currentTarget as SVGElement;
      const detectionId = target.getAttribute('data-detection-id');
      const detectionType = target.getAttribute('data-detection-type');
      
      if (detectionId) {
        // Dispatch event to open detection detail modal
        window.dispatchEvent(new CustomEvent('detection-marker-clicked', {
          detail: {
            detectionId,
            detectionType,
          }
        }));
      }
    });
  });
}

// Store the last config for use in updates
let lastConfig: MapConfig | null = null;

/**
 * Initialize tactical map
 */
export function initializeTacticalMap(useCase: string) {
  const config = getMapConfig(useCase);
  lastConfig = config;
  renderSectors(config, 0);
  
  return config;
}

/**
 * Update tactical map with new mission state
 */
export function updateTacticalMap(state: MissionSimulationState, config: MapConfig) {
  // Get current elapsed time from mission state
  const currentTime = state.simulation_clock?.elapsed_seconds || 0;
  
  // Update sectors with progressive reveal and terrain reconstruction
  renderSectors(config, currentTime, state.terrain_reconstruction);
  
  // Update agents with route-based positioning
  updateAgents(state.agents, config, currentTime);
  
  // Update detection markers
  renderDetectionMarkers(config, currentTime);
}
