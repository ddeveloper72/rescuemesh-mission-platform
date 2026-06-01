/**
 * Tactical Map Manager
 * 
 * Renders and updates SVG tactical maps based on mission state.
 * Use-case specific layouts for different simulation types.
 * 
 * Now includes animated agent movement, progressive sector reveal,
 * time-based detection markers, and Django Digital Twin integration.
 */

import type { MissionSimulationState, Agent } from '../types/simulation';
import { loadDigitalTwinMap, type DigitalTwinLoadResult } from './tactical-map/digitalTwinMapLoader';
import type { TacticalMapViewModel } from './tactical-map/digitalTwinMapAdapter';

interface MapConfig {
  sectors: TacticalSector[];
  hazardZones?: HazardZone[];
  width: number;
  height: number;
  routes?: TacticalAgentRoute[];
  detectionMarkers?: DetectionMarker[];
  terrainSource?: 'django-digital-twin' | 'local-fallback';
  terrainMeta?: {
    siteName?: string;
    terrainMapName?: string;
    siteSlug?: string;
    terrainMapSlug?: string;
  };
  coordinateScaling?: {
    minX: number;
    maxX: number;
    minY: number;
    maxY: number;
    scaleX: number;
    scaleY: number;
    offsetX: number;
    offsetY: number;
  };
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
    { id: 'artefact-wall', type: 'thermal', x: 300, y: 180, appearsAt: 240, label: 'Possible wall marking', icon: 'A' },
    { id: 'artefact-floor', type: 'thermal', x: 450, y: 250, appearsAt: 420, label: 'Possible ceramic fragment', icon: 'A' },
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
      return { ...getIndustrialInspectionMapConfig(), terrainSource: 'local-fallback' };
    case 'collapsed-building-search':
      return { ...getCollapsedBuildingMapConfig(), terrainSource: 'local-fallback' };
    case 'cave-rescue':
      return { ...getCaveRescueMapConfig(), terrainSource: 'local-fallback' };
    case 'flooded-structure':
      return { ...getFloodedStructureMapConfig(), terrainSource: 'local-fallback' };
    case 'archaeological-exploration':
      return { ...getArchaeologicalExplorationMapConfig(), terrainSource: 'local-fallback' };
    default:
      return { width: 800, height: 450, sectors: [], terrainSource: 'local-fallback' };
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
 * Detect label collision and suggest offset
 */
/**
 * Cached label bounds for collision detection across the entire tactical map.
 * This cache is rebuilt on each render cycle to track all label positions
 * and prevent overlapping labels in dense areas.
 */
interface LabelBounds {
  sectorId: string;    // Unique sector identifier
  x: number;           // Label bounding box X coordinate
  y: number;           // Label bounding box Y coordinate
  width: number;       // Label bounding box width in pixels
  height: number;      // Label bounding box height in pixels
  label: string;       // Label text content
}

let labelBoundsCache: LabelBounds[] = [];

/**
 * Calculate optimal label offset position to avoid collisions with other labels and sectors.
 * 
 * This function implements an intelligent label placement algorithm that:
 * 1. Evaluates 8 candidate positions around the sector (N, NE, E, SE, S, SW, W, NW, Center)
 * 2. Assigns collision scores based on:
 *    - Position priority (center preferred, then cardinal, then diagonal)
 *    - Overlap area with existing labels (heavy penalty)
 *    - Proximity to other labels (moderate penalty)
 *    - Overlap with other sector boundaries (moderate penalty)
 * 3. Selects the position with the lowest collision score
 * 4. Caches the chosen position to inform subsequent label placements
 * 
 * @param sector - The tactical sector to place a label for
 * @param allSectors - Array of all sectors on the map (for boundary collision detection)
 * @param labelOpacity - Opacity value (0-1); returns zero offset if label is invisible
 * @param label - The text content of the label (used for dimension estimation)
 * @returns Object containing offsetX and offsetY in map coordinates
 * 
 * @remarks
 * Label dimensions are estimated at ~7px per character width and 16px height.
 * The algorithm uses a scoring system where lower scores indicate better positions:
 * - Base score = position priority (1-9)
 * - Overlap penalty = overlap_area * 10
 * - Proximity penalty = (40 - distance) / 4 for distances < 40px
 * - Sector overlap penalty = overlap_area * 5
 */
function calculateLabelOffset(
  sector: TacticalSector,
  allSectors: TacticalSector[],
  labelOpacity: number,
  label: string
): { offsetX: number; offsetY: number } {
  // Skip calculation entirely if label is invisible
  if (labelOpacity === 0) return { offsetX: 0, offsetY: 0 };
  
  const centerX = sector.x + sector.width / 2;
  const centerY = sector.y + sector.height / 2;
  
  // Estimate label dimensions (roughly 7px per character width, 16px height)
  const labelWidth = label.length * 7;
  const labelHeight = 16;
  
  // Define 8 candidate positions around the sector center
  // Format: [offsetX, offsetY, priority] - priority lower is better
  const candidatePositions = [
    [0, 0, 1],                              // Center (default, highest priority)
    [0, -sector.height / 2 - 20, 2],       // North
    [0, sector.height / 2 + 20, 3],        // South
    [sector.width / 2 + 20, 0, 4],         // East
    [-sector.width / 2 - 20, 0, 5],        // West
    [sector.width / 2 + 15, -sector.height / 2 - 15, 6],   // NE
    [sector.width / 2 + 15, sector.height / 2 + 15, 7],    // SE
    [-sector.width / 2 - 15, sector.height / 2 + 15, 8],   // SW
    [-sector.width / 2 - 15, -sector.height / 2 - 15, 9],  // NW
  ];
  
  let bestPosition = { offsetX: 0, offsetY: 0, collisionScore: Infinity };
  
  // Evaluate each candidate position to find the one with minimum collisions
  for (const [offsetX, offsetY, priority] of candidatePositions) {
    const labelX = centerX + offsetX;
    const labelY = centerY + offsetY;
    
    // Calculate bounding box for this label position (centered on labelX, labelY)
    const labelBounds = {
      x: labelX - labelWidth / 2,
      y: labelY - labelHeight / 2,
      width: labelWidth,
      height: labelHeight,
    };
    
    // Initialize collision score with position priority (1=center is best, 9=NW is worst)
    let collisionScore = priority as number;
    
    // Phase 1: Check for collisions with existing labels already placed on the map
    for (const existingLabel of labelBoundsCache) {
      if (existingLabel.sectorId === sector.id) continue; // Skip self-collision
      
      // Heavy penalty for any overlap with existing labels
      const overlap = calculateRectangleOverlap(labelBounds, existingLabel);
      if (overlap > 0) {
        collisionScore += overlap * 10; // 10 points per square pixel of overlap
      }
      
      // Proximity penalty: discourage placing labels too close together even without overlap
      // This maintains visual spacing and improves readability
      const distance = Math.sqrt(
        Math.pow(labelBounds.x + labelBounds.width / 2 - (existingLabel.x + existingLabel.width / 2), 2) +
        Math.pow(labelBounds.y + labelBounds.height / 2 - (existingLabel.y + existingLabel.height / 2), 2)
      );
      if (distance < 40) {
        collisionScore += (40 - distance) / 4; // Penalty scales with closeness
      }
    }
    
    // Phase 2: Check for collisions with other sector boundaries
    for (const otherSector of allSectors) {
      if (otherSector.id === sector.id) continue; // Skip self
      
      const otherCenterX = otherSector.x + otherSector.width / 2;
      const otherCenterY = otherSector.y + otherSector.height / 2;
      
      // Avoid placing labels directly on top of other sectors
      const sectorBounds = {
        x: otherSector.x,
        y: otherSector.y,
        width: otherSector.width,
        height: otherSector.height,
      };
      
      const overlap = calculateRectangleOverlap(labelBounds, sectorBounds);
      if (overlap > 0) {
        collisionScore += overlap * 5; // Moderate penalty (5 points per square pixel)
      }
    }
    
    // Update best position if this candidate has a lower collision score
    if (collisionScore < bestPosition.collisionScore) {
      bestPosition = {
        offsetX: offsetX as number,
        offsetY: offsetY as number,
        collisionScore,
      };
    }
    
    // Performance optimization: if center position has no collisions, use it immediately
    // (collision score of 1 means only the base priority, no penalties)
    if (collisionScore === 1 && offsetX === 0 && offsetY === 0) {
      break;
    }
  }
  
  // Cache this label's final position for subsequent collision checks
  // Labels are rendered in sector order, so earlier labels inform later placements
  const finalLabelX = centerX + bestPosition.offsetX;
  const finalLabelY = centerY + bestPosition.offsetY;
  labelBoundsCache.push({
    sectorId: sector.id,
    x: finalLabelX - labelWidth / 2,
    y: finalLabelY - labelHeight / 2,
    width: labelWidth,
    height: labelHeight,
    label,
  });
  
  return { offsetX: bestPosition.offsetX, offsetY: bestPosition.offsetY };
}

/**
 * Calculate the overlapping area between two rectangles using intersection logic.
 * 
 * This helper function is used by the label placement algorithm to detect and quantify
 * collisions between label bounding boxes and other UI elements (labels, sectors).
 * 
 * @param rect1 - First rectangle with {x, y, width, height} properties
 * @param rect2 - Second rectangle with {x, y, width, height} properties
 * @returns The area of overlap in square pixels, or 0 if rectangles don't intersect
 * 
 * @remarks
 * Uses the standard rectangle intersection algorithm:
 * 1. Find the maximum of left edges (x1)
 * 2. Find the maximum of top edges (y1)
 * 3. Find the minimum of right edges (x2)
 * 4. Find the minimum of bottom edges (y2)
 * 5. If x2 <= x1 or y2 <= y1, rectangles don't overlap (return 0)
 * 6. Otherwise, overlap area = (x2 - x1) * (y2 - y1)
 * 
 * @example
 * const overlap = calculateRectangleOverlap(
 *   { x: 0, y: 0, width: 100, height: 50 },
 *   { x: 50, y: 25, width: 100, height: 50 }
 * ); // Returns 1250 (50px × 25px overlap area)
 */
function calculateRectangleOverlap(
  rect1: { x: number; y: number; width: number; height: number },
  rect2: { x: number; y: number; width: number; height: number }
): number {
  // Find the intersection boundaries
  const x1 = Math.max(rect1.x, rect2.x);
  const y1 = Math.max(rect1.y, rect2.y);
  const x2 = Math.min(rect1.x + rect1.width, rect2.x + rect2.width);
  const y2 = Math.min(rect1.y + rect1.height, rect2.y + rect2.height);
  
  // No overlap if intersection has zero or negative dimensions
  if (x2 <= x1 || y2 <= y1) return 0;
  
  // Calculate and return overlap area
  return (x2 - x1) * (y2 - y1);
}

/**
 * Render sectors on the map with progressive reveal
 */
export function renderSectors(
  config: MapConfig,
  currentTime: number,
  simulationSectors?: any[]
) {
  const sectorsGroup = document.getElementById('map-sectors');
  if (!sectorsGroup) return;

  // Clear label cache at the start of each render
  labelBoundsCache = [];

  sectorsGroup.innerHTML = config.sectors.map(sector => {
    // Try to find simulation state for this sector
    let sectorState = null;
    if (simulationSectors) {
      sectorState = simulationSectors.find(
        (s: any) => s.sector_id === sector.id
      );
    }

    // Use simulation sector confidence if available, otherwise fallback to revealAt timing
    let fillColor = 'rgba(71, 85, 105, 0.3)'; // slate-600 default
    let strokeColor = 'rgba(148, 163, 184, 0.5)'; // slate-400
    let opacity = 0.15;
    let labelOpacity = 0.3;
    let label = '???';
    let strokeWidth = 2;
    
    if (sectorState) {
      // Use simulation sector state
      const confidence = sectorState.confidence || 0;
      
      // Only show sector if confidence > 0 (explored)
      if (confidence === 0) {
        opacity = 0.0;  // Completely hide unexplored sectors
        labelOpacity = 0.0;
        label = '';
      } else if (confidence < 0.5) {
        opacity = 0.3;
        labelOpacity = 0.5;
        label = `${sector.label} (${Math.round(confidence * 100)}%)`;
        strokeColor = 'rgba(148, 163, 184, 0.7)';
        strokeWidth = 1;
      } else if (confidence < 0.8) {
        opacity = 0.6;
        labelOpacity = 0.7;
        label = `${sector.label} (${Math.round(confidence * 100)}%)`;
        strokeWidth = 2;
      } else {
        opacity = 0.9;
        labelOpacity = 1.0;
        label = sector.label;
        strokeWidth = 2;
      }
      
      // Apply sector type styling
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
    } else {
      // Fallback: hide sectors until simulation state provides confidence
      // This prevents showing the full map before agents have explored
      opacity = currentTime >= sector.revealAt ? 1.0 : 0.0;
      labelOpacity = currentTime >= sector.revealAt ? 1.0 : 0.0;
      label = currentTime >= sector.revealAt ? sector.label : '';
      
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

    // Calculate label offset to prevent collisions
    const labelOffset = calculateLabelOffset(sector, config.sectors, labelOpacity, label);

    // Build depth/elevation label if available
    let depthLabel = '';
    if (sector.depthLabel || sector.elevationLabel) {
      const depthText = sector.elevationLabel || sector.depthLabel || '';
      depthLabel = `
        <text 
          x="${sector.x + sector.width / 2 + labelOffset.offsetX}" 
          y="${sector.y + sector.height / 2 + labelOffset.offsetY + 14}"
          text-anchor="middle"
          dominant-baseline="middle"
          class="text-xs"
          fill="#94a3b8"
          opacity="${labelOpacity * 0.8}"
          font-size="9"
        >${depthText}</text>
      `;
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
        x="${sector.x + sector.width / 2 + labelOffset.offsetX}" 
        y="${sector.y + sector.height / 2 + labelOffset.offsetY}"
        text-anchor="middle"
        dominant-baseline="middle"
        class="text-xs"
        fill="#e2e8f0"
        opacity="${labelOpacity}"
      >${label}</text>
      ${depthLabel}
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

    // For Digital Twin terrain, use agent's real position if available
    if (config.terrainSource === 'django-digital-twin' && config.coordinateScaling && agent.position) {
      const scaling = config.coordinateScaling;
      // Convert from meters to SVG coordinates
      const svgX = (agent.position.x - scaling.minX) * scaling.scaleX + scaling.offsetX;
      const svgY = (agent.position.y - scaling.minY) * scaling.scaleY + scaling.offsetY;
      pos = {
        x: svgX,
        y: svgY,
        stopped: agent.state === 'landed_relay' || agent.state === 'sacrificed' || agent.state === 'failed',
      };
    } else {
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

    // Get depth/elevation label if navigation data available
    const depthElevationLabel = (agent as any).navigation?.depth_elevation_label;
    const hasDepthElevation = depthElevationLabel && depthElevationLabel !== '±0 m';

    elements.push(`
      <g id="agent-${agent.agent_id}" class="agent-marker cursor-pointer hover:opacity-80 transition-opacity" data-agent-id="${agent.agent_id}">
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
        ${hasDepthElevation ? `
          <rect
            x="${pos.x - 18}"
            y="${pos.y + 12}"
            width="36"
            height="14"
            rx="2"
            fill="#1e293b"
            fill-opacity="0.9"
            stroke="${color}"
            stroke-width="1"
          />
          <text
            x="${pos.x}"
            y="${pos.y + 22}"
            text-anchor="middle"
            font-size="9"
            font-weight="bold"
            fill="${color}"
          >${depthElevationLabel}</text>
        ` : ''}
        <title>${agent.name} - ${agent.state} (Battery: ${agent.battery_percent}%)${hasDepthElevation ? '\n' + depthElevationLabel : ''}</title>
      </g>
    `);
  });

  agentsGroup.innerHTML = elements.join('');
  
  // Attach click handlers to agent markers
  attachAgentMarkerClickHandlers(agents);
}

/**
 * Attach click handlers to agent markers for detailed information display.
 * 
 * Enables interactive exploration of agent details by dispatching custom events
 * when agent markers are clicked on the tactical map.
 * 
 * @param agents - Array of all agents in the mission
 */
function attachAgentMarkerClickHandlers(agents: Agent[]) {
  const markers = document.querySelectorAll('.agent-marker');
  
  markers.forEach(marker => {
    marker.addEventListener('click', (event) => {
      const target = event.currentTarget as SVGElement;
      const agentId = target.getAttribute('data-agent-id');
      
      if (agentId) {
        const agent = agents.find(a => a.agent_id === agentId);
        if (agent) {
          // Dispatch event to open agent detail modal
          window.dispatchEvent(new CustomEvent('agent-marker-clicked', {
            detail: { agent }
          }));
        }
      }
    });
  });
}

/**
 * Render network connection lines between agents showing the relay chain topology.
 * 
 * This function visualizes the communications network by drawing lines between agents,
 * establishing the relay chain from the origin (entrance) through intermediate relays
 * to active field agents. 
 * 
 * **Critical Feature: Active-Only Routing**
 * The network rendering implements intelligent routing that:
 * - Only shows connections through ACTIVE/HEALTHY relay nodes
 * - Excludes sacrificed, failed, or degraded relays from the network path
 * - Dynamically recalculates routes when relays fail
 * - Reflects operational reality: dead relays cannot relay signals
 * 
 * **Network Path Selection:**
 * 1. Identifies the origin point (entrance/base station)
 * 2. Separates agents into active relays vs. field agents
 * 3. For each field agent, finds the nearest ACTIVE relay
 * 4. Draws connections through the active relay chain only
 * 5. Applies signal strength-based color coding to connections
 * 
 * @param agents - Array of all agents in the mission with position and state data
 * @param config - Map configuration including coordinate scaling for digital twin mode
 * 
 * @remarks
 * Connection colors indicate signal strength:
 * - Green (85-100%): Strong, reliable connection
 * - Yellow (50-84%): Moderate signal quality
 * - Red (<50%): Weak or degraded connection
 * 
 * Line styles:
 * - Solid lines: Direct agent-to-relay connections
 * - Dashed lines: Relay-to-relay backbone connections
 */
export function renderNetworkConnections(agents: Agent[], config: MapConfig) {
  const networkGroup = document.getElementById('map-network');
  if (!networkGroup) return;

  const elements: string[] = [];

  // Build list of agents with positions
  const agentsWithPositions: Array<{ agent: Agent; x: number; y: number }> = [];
  
  agents.forEach(agent => {
    // Get agent position from config
    if (config.terrainSource === 'django-digital-twin' && config.coordinateScaling && agent.position) {
      const scaling = config.coordinateScaling;
      const svgX = (agent.position.x - scaling.minX) * scaling.scaleX + scaling.offsetX;
      const svgY = (agent.position.y - scaling.minY) * scaling.scaleY + scaling.offsetY;
      agentsWithPositions.push({ agent, x: svgX, y: svgY });
    } else {
      // Try to find position from sector
      const location = agent.location_label.toLowerCase();
      const sector = config.sectors.find(s => 
        location.includes(s.id) || location.includes(s.label.toLowerCase())
      );
      
      if (sector) {
        const x = sector.x + sector.width / 2;
        const y = sector.y + sector.height / 2;
        agentsWithPositions.push({ agent, x, y });
      }
    }
  });

  if (agentsWithPositions.length < 2) {
    // No connections to draw
    networkGroup.innerHTML = '';
    return;
  }

  // Identify origin (entrance) - typically at sector entrance or lowest agent_id
  const entrance = agentsWithPositions.find(a => 
    a.agent.location_label?.toLowerCase().includes('entrance') ||
    a.agent.location_label?.toLowerCase().includes('entry') ||
    a.agent.location_label?.toLowerCase().includes('breach')
  );
  const origin = entrance || agentsWithPositions[0];

  // Separate into ACTIVE relay nodes only (exclude sacrificed relays - they can't relay!)
  const activeRelayNodes = agentsWithPositions.filter(a => 
    a.agent.state !== 'sacrificed' && 
    a.agent.state !== 'failed' &&
    (a.agent.state === 'landed_relay' || 
     a.agent.role === 'relay' ||
     a.agent.location_label?.toLowerCase().includes('entrance') ||
     a.agent.location_label?.toLowerCase().includes('entry'))
  );
  
  // Ensure origin is in active relay nodes if it's not sacrificed
  if (origin.agent.state !== 'sacrificed' && !activeRelayNodes.find(r => r === origin)) {
    activeRelayNodes.unshift(origin);
  }

  // Active agents = non-relay agents that are still operational
  const activeAgents = agentsWithPositions.filter(a => 
    a.agent.state !== 'sacrificed' &&
    a.agent.state !== 'failed' &&
    a.agent.state !== 'landed_relay' && 
    !activeRelayNodes.includes(a)
  );

  // Draw connections from each agent back to origin through relay chain
  const drawnConnections = new Set<string>(); // Track to avoid duplicates

  const drawConnection = (fromX: number, fromY: number, toX: number, toY: number, signal: number, label: string) => {
    const connectionKey = `${fromX},${fromY}-${toX},${toY}`;
    if (drawnConnections.has(connectionKey)) return; // Skip duplicates
    drawnConnections.add(connectionKey);

    // Scale opacity by signal strength, minimum 25% for visibility
    const opacity = Math.max(0.25, (signal / 100) * 0.7);
    const color = signal > 70 ? '#10b981' : signal > 40 ? '#eab308' : signal === 0 ? '#64748b' : '#ef4444';
    
    elements.push(`
      <line
        x1="${fromX}"
        y1="${fromY}"
        x2="${toX}"
        y2="${toY}"
        stroke="${color}"
        stroke-width="2"
        stroke-opacity="${opacity}"
        stroke-dasharray="5,5"
      >
        <title>${label}</title>
      </line>
    `);
  };

  // Connect active agents to nearest ACTIVE relay (bypassing dead relays)
  activeAgents.forEach(({ agent, x, y }) => {
    if (activeRelayNodes.length === 0) return; // No active relays available
    
    // Find nearest ACTIVE relay node
    let nearest = activeRelayNodes[0];
    let minDist = Math.hypot(x - nearest.x, y - nearest.y);
    
    activeRelayNodes.forEach(relay => {
      const dist = Math.hypot(x - relay.x, y - relay.y);
      if (dist < minDist) {
        minDist = dist;
        nearest = relay;
      }
    });

    // Draw connection to nearest active relay
    const signal = agent.signal_strength || 0;
    drawConnection(
      x, y,
      nearest.x, nearest.y,
      signal,
      `${agent.name} → ${nearest.agent.name} (Signal: ${signal}%)`
    );
  });

  // Connect ACTIVE relay chain - each relay to next closest ACTIVE relay toward origin
  activeRelayNodes.forEach(relay => {
    if (relay === origin) return; // Origin doesn't connect to anything (it's the root)

    // Find nearest ACTIVE relay that's closer to origin (creates chain back to entrance)
    const relayDistToOrigin = Math.hypot(relay.x - origin.x, relay.y - origin.y);
    
    let nearest = origin;
    let minDist = relayDistToOrigin;
    
    activeRelayNodes.forEach(candidateRelay => {
      if (candidateRelay === relay) return; // Skip self
      
      const distToCandidate = Math.hypot(relay.x - candidateRelay.x, relay.y - candidateRelay.y);
      const candidateDistToOrigin = Math.hypot(candidateRelay.x - origin.x, candidateRelay.y - origin.y);
      
      // Connect to ACTIVE relay that's closer to origin and reasonably near
      if (candidateDistToOrigin < relayDistToOrigin && distToCandidate < minDist) {
        minDist = distToCandidate;
        nearest = candidateRelay;
      }
    });

    // Draw relay-to-relay connection for ACTIVE relays only
    const signal = relay.agent.signal_strength || 0;
    drawConnection(
      relay.x, relay.y,
      nearest.x, nearest.y,
      signal,
      `Relay: ${relay.agent.name} → ${nearest.agent.name} (Signal: ${signal}%)`
    );
  });

  networkGroup.innerHTML = elements.join('');
}

/**
 * Render sensor detection markers from live mission data
 * Detections persist even after detecting agent fails
 */
export function renderSensorDetections(
  sensors: {
    thermal_anomalies?: Array<{
      id: string;
      agent_id: string;
      agent_name: string;
      detected_at: string;
      location: string;
      position?: { x_m: number; y_m: number; z_m: number };
      temperature_delta: number;
      confidence: number;
      timestamp_seconds?: number;
    }>;
    audio_events?: Array<{
      id: string;
      agent_id: string;
      agent_name: string;
      detected_at: string;
      location: string;
      position?: { x_m: number; y_m: number; z_m: number };
      type: string;
      confidence: number;
      timestamp_seconds?: number;
    }>;
  },
  config: MapConfig,
  currentTime: number
) {
  const markersGroup = document.getElementById('map-detections');
  if (!markersGroup) {
    console.warn('Sensor detections group not found in SVG');
    return;
  }

  const markers: string[] = [];

  // Get coordinate scaling for proper position transformation
  const scaling = config.coordinateScaling;
  if (!scaling) {
    console.warn('No coordinate scaling available for sensor detections');
    return;
  }

  // Render thermal detections
  if (sensors.thermal_anomalies && sensors.thermal_anomalies.length > 0) {
    sensors.thermal_anomalies.forEach(detection => {
      if (!detection.position) return;

      // Convert position to SVG coordinates using proper scaling (handles negative coordinates)
      const svgX = (detection.position.x_m - scaling.minX) * scaling.scaleX + scaling.offsetX;
      const svgY = (detection.position.y_m - scaling.minY) * scaling.scaleY + scaling.offsetY;

      // Check if detection is recent (within last 60 seconds)
      const detectionAge = currentTime - (detection.timestamp_seconds || 0);
      const isRecent = detectionAge < 60;
      
      // Visual styling based on age
      const opacity = isRecent ? 1.0 : 0.6;
      const pulseAnimation = isRecent ? 'animate-pulse' : '';
      
      markers.push(`
        <g class="sensor-detection detection-thermal ${pulseAnimation}" 
           data-detection-id="${detection.id}" 
           data-detection-type="thermal"
           data-agent-name="${detection.agent_name}"
           data-detected-at="${detection.detected_at}"
           opacity="${opacity}">
          <circle 
            cx="${svgX}" 
            cy="${svgY}" 
            r="14"
            fill="rgba(239, 68, 68, 0.2)"
            stroke="#ef4444"
            stroke-width="2"
          />
          <text 
            x="${svgX}" 
            y="${svgY + 22}" 
            text-anchor="middle" 
            class="text-xs pointer-events-none"
            fill="#ef4444"
            style="font-size: 16px; font-weight: bold;"
          >🔥</text>
          <title>Thermal: ${detection.temperature_delta}°C @ ${detection.detected_at} by ${detection.agent_name}</title>
        </g>
      `);
    });
  }

  // Render audio detections
  if (sensors.audio_events && sensors.audio_events.length > 0) {
    sensors.audio_events.forEach(detection => {
      if (!detection.position) return;

      // Convert position to SVG coordinates using proper scaling (handles negative coordinates)
      const svgX = (detection.position.x_m - scaling.minX) * scaling.scaleX + scaling.offsetX;
      const svgY = (detection.position.y_m - scaling.minY) * scaling.scaleY + scaling.offsetY;

      // Check if detection is recent
      const detectionAge = currentTime - (detection.timestamp_seconds || 0);
      const isRecent = detectionAge < 60;
      
      // Visual styling based on age
      const opacity = isRecent ? 1.0 : 0.6;
      const pulseAnimation = isRecent ? 'animate-pulse' : '';
      
      markers.push(`
        <g class="sensor-detection detection-audio ${pulseAnimation}" 
           data-detection-id="${detection.id}" 
           data-detection-type="audio"
           data-agent-name="${detection.agent_name}"
           data-detected-at="${detection.detected_at}"
           opacity="${opacity}">
          <circle 
            cx="${svgX}" 
            cy="${svgY}" 
            r="14"
            fill="rgba(139, 92, 246, 0.2)"
            stroke="#8b5cf6"
            stroke-width="2"
          />
          <text 
            x="${svgX}" 
            y="${svgY + 22}" 
            text-anchor="middle" 
            class="text-xs pointer-events-none"
            fill="#8b5cf6"
            style="font-size: 16px; font-weight: bold;"
          >🔊</text>
          <title>Audio: ${detection.type} @ ${detection.detected_at} by ${detection.agent_name} (Confidence: ${Math.round(detection.confidence * 100)}%)</title>
        </g>
      `);
    });
  }

  markersGroup.innerHTML = markers.join('');
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
/**
 * Render compass rose indicator for mission north reference
 */
export function renderCompassRose(navigationModel?: {
  north_reference: string;
  bearing_reference: string;
  bearing_reliability?: string;
  bearing_confidence?: number;
}) {
  const compassGroup = document.getElementById('map-compass');
  if (!compassGroup) return;

  if (!navigationModel) {
    compassGroup.innerHTML = '';
    return;
  }

  const compassX = 680; // Top right area, left of zoom controls
  const compassY = 40;
  const compassRadius = 25;

  // Reliability color
  const reliability = navigationModel.bearing_reliability || 'good';
  let strokeColor = '#10b981'; // green-500
  let fillColor = 'rgba(16, 185, 129, 0.1)';
  
  if (reliability === 'degraded') {
    strokeColor = '#f59e0b'; // amber-500
    fillColor = 'rgba(245, 158, 11, 0.1)';
  } else if (reliability === 'unreliable') {
    strokeColor = '#ef4444'; // red-500
    fillColor = 'rgba(239, 68, 68, 0.1)';
  }

  // Label based on reference
  const label = navigationModel.bearing_reference === 'magnetic_simulated'
    ? 'Mag N (sim)'
    : 'Mission N';

  compassGroup.innerHTML = `
    <!-- Compass background -->
    <circle cx="${compassX}" cy="${compassY}" r="${compassRadius}" 
      fill="${fillColor}" stroke="${strokeColor}" stroke-width="2" />
    
    <!-- North indicator (triangle pointing up) -->
    <path d="M ${compassX} ${compassY - compassRadius + 8} 
             L ${compassX - 6} ${compassY - compassRadius + 18} 
             L ${compassX + 6} ${compassY - compassRadius + 18} Z"
      fill="${strokeColor}" />
    
    <!-- North label -->
    <text x="${compassX}" y="${compassY + 3}" 
      text-anchor="middle" font-size="14" font-weight="bold" fill="${strokeColor}">N</text>
    
    <!-- Reference label below compass -->
    <text x="${compassX}" y="${compassY + compassRadius + 12}" 
      text-anchor="middle" font-size="9" fill="#94a3b8">${label}</text>
    
    <!-- Confidence indicator (if reliability is not good) -->
    ${reliability !== 'good' ? `
      <circle cx="${compassX + compassRadius - 5}" cy="${compassY - compassRadius + 5}" r="4" 
        fill="#f59e0b" stroke="#1e293b" stroke-width="1" />
      <text x="${compassX + compassRadius - 5}" y="${compassY - compassRadius + 8}" 
        text-anchor="middle" font-size="8" font-weight="bold" fill="#1e293b">!</text>
    ` : ''}
  `;
}

export function initializeTacticalMap(useCase: string) {
  const config = getMapConfig(useCase);
  lastConfig = config;
  renderSectors(config, 0);
  renderCompassRose(); // Will be updated with navigation_model when state arrives
  renderTerrainSourceBadge(config);
  
  return config;
}

/**
 * Initialize tactical map with Django Digital Twin terrain (async)
 * Falls back to local config if Digital Twin fails to load
 */
export async function initializeTacticalMapWithDigitalTwin(useCase: string): Promise<MapConfig> {
  console.log(`[TacticalMap] Attempting to load Digital Twin terrain for: ${useCase}`);
  
  const result = await loadDigitalTwinMap(useCase);
  
  if (result.success && result.viewModel) {
    console.log(`[TacticalMap] ✓ Digital Twin terrain loaded successfully`);
    const config = convertViewModelToMapConfig(result.viewModel);
    lastConfig = config;
    renderSectors(config, 0);
    renderCompassRose();
    renderTerrainSourceBadge(config);
    return config;
  } else {
    console.warn(`[TacticalMap] ⚠ Digital Twin load failed: ${result.error}`);
    console.log(`[TacticalMap] → Falling back to local terrain layout`);
    return initializeTacticalMap(useCase);
  }
}

/**
 * Convert TacticalMapViewModel to MapConfig
 */
function convertViewModelToMapConfig(viewModel: TacticalMapViewModel): MapConfig {
  return {
    sectors: viewModel.sectors,
    hazardZones: viewModel.hazardZones,
    width: viewModel.width,
    height: viewModel.height,
    routes: viewModel.routes,
    detectionMarkers: viewModel.detectionMarkers,
    terrainSource: viewModel.terrainSource,
    terrainMeta: viewModel.terrainMeta,
    coordinateScaling: viewModel.coordinateScaling,
  };
}

/**
 * Render terrain source badge
 */
function renderTerrainSourceBadge(config: MapConfig) {
  const container = document.getElementById('tactical-map');
  if (!container) return;

  // Remove existing badge
  const existingBadge = container.querySelector('.terrain-source-badge');
  if (existingBadge) {
    existingBadge.remove();
  }

  // Create badge
  const badge = document.createElement('div');
  badge.className = 'terrain-source-badge absolute top-2 left-2 z-10 px-3 py-1 rounded-full text-xs font-medium';
  
  if (config.terrainSource === 'django-digital-twin') {
    badge.classList.add('bg-green-500/20', 'text-green-300', 'border', 'border-green-500/50');
    badge.innerHTML = `
      <span class="flex items-center gap-1.5">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/>
        </svg>
        <span>Django Digital Twin</span>
      </span>
    `;
    
    // Add tooltip with metadata
    if (config.terrainMeta) {
      badge.title = `Site: ${config.terrainMeta.siteName}\nMap: ${config.terrainMeta.terrainMapName}`;
    }
  } else {
    badge.classList.add('bg-slate-500/20', 'text-slate-300', 'border', 'border-slate-500/50');
    badge.innerHTML = `
      <span class="flex items-center gap-1.5">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
        </svg>
        <span>Local Fallback</span>
      </span>
    `;
    badge.title = 'Using local hardcoded terrain layout';
  }

  container.appendChild(badge);
}

/**
 * Update tactical map with new mission state
 */
export function updateTacticalMap(state: MissionSimulationState, config: MapConfig) {
  // Get current elapsed time from mission state
  const currentTime = state.simulation_clock?.elapsed_seconds || 0;
  
  // Update sectors with progressive reveal using simulation state
  renderSectors(config, currentTime, state.sectors);
  
  // Update agents with route-based positioning
  updateAgents(state.agents, config, currentTime);
  
  // Render network connections between agents
  renderNetworkConnections(state.agents, config);
  
  // Render live sensor detections (persistent, even after agent failure)
  if (state.sensors) {
    renderSensorDetections(state.sensors, config, currentTime);
  }
  
  // Update static detection markers (from config)
  renderDetectionMarkers(config, currentTime);
  
  // Update compass rose with navigation model
  if (state.navigation_model) {
    renderCompassRose(state.navigation_model);
  }
}
