/**
 * Digital Twin Map Adapter
 * 
 * Transforms Django Digital Twin terrain data into the tactical map view model.
 * Handles coordinate scaling, sector styling, and mission state overlay.
 */

import type {
  TerrainMap,
  TerrainSector,
  TerrainPath,
  Waypoint,
} from '../api';

import type { MissionSimulationState } from '../../types/simulation';

/**
 * Tactical map view model (matches existing tactical-map-manager types)
 */
export interface TacticalMapViewModel {
  sectors: TacticalSector[];
  hazardZones?: HazardZone[];
  width: number;
  height: number;
  routes?: TacticalAgentRoute[];
  detectionMarkers?: DetectionMarker[];
  terrainSource: 'django-digital-twin' | 'local-fallback';
  terrainMeta?: {
    siteName: string;
    terrainMapName: string;
    siteSlug: string;
    terrainMapSlug: string;
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

export interface TacticalSector {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  type?: 'accessible' | 'blocked' | 'void' | 'water' | 'hazard';
  revealAt: number;
  confidenceAtReveal?: number;
  metadata?: Record<string, any>;
  depthLabel?: string;
  elevationLabel?: string;
}

export interface HazardZone {
  id: string;
  x: number;
  y: number;
  radius: number;
  type: 'thermal' | 'gas' | 'electrical' | 'pressure';
}

export interface TacticalWaypoint {
  time: number;
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
  appearsAt: number;
  label: string;
  icon: string;
}

/**
 * Coordinate scaling configuration
 */
interface ScalingConfig {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
  scaleX: number;
  scaleY: number;
  offsetX: number;
  offsetY: number;
}

/**
 * Sector alias mapping for backward compatibility
 * Maps old simulation sector names to new digital twin sector IDs
 */
export const SECTOR_ALIASES: Record<string, Record<string, string>> = {
  'cave-rescue': {
    'Entrance Chamber': 'entrance',
    'Chamber 1': 'chamber-1',
    'Chamber 2': 'chamber-2',
    'Main Tunnel': 'passage-1',
    'Narrow Passage': 'passage-2',
    'Deep Squeeze': 'squeeze-1',
    'Terminal Chamber': 'terminal',
  },
  'industrial-inspection': {
    'Entry Point': 'access-shaft-01',
    'Plant Room': 'equipment-room-a',
    'Pipe Gallery': 'pipe-corridor-01',
    'Duct Section': 'utility-corridor-main',
    'Control Cabinet': 'control-room-local',
    'Tank Interior': 'tank-chamber-01',
    'Hazard Zone': 'hazard-zone-01',
  },
  'archaeological-exploration': {
    'Access Tunnel': 'access-tunnel',
    'Antechamber': 'antechamber',
    'Main Chamber': 'main-chamber-a',
    'Artifact Alcove': 'artifact-alcove-1',
    'Inscription Wall': 'inscription-corridor',
    'Sealed Passage': 'sealed-passage-east',
    'Collapse Zone': 'collapse-zone',
  },
  'flooded-structure': {
    'Hull Breach': 'hull-breach-starboard',
    'Flooded Corridor': 'bilge-compartment',
    'Engine Room': 'engine-room-main',
    'Cargo Hold 1': 'cargo-hold-1',
    'Cargo Hold 2': 'cargo-hold-2',
    'Bridge': 'bridge-deck',
    'Crew Quarters': 'crew-quarters-b',
    'Sealed Compartment': 'compartment-sealed-1',
  },
};

/**
 * Calculate coordinate scaling from Django metres to SVG coordinates
 */
function calculateScaling(
  sectors: TerrainSector[],
  viewBoxWidth: number = 800,
  viewBoxHeight: number = 450,
  padding: number = 50
): ScalingConfig {
  if (sectors.length === 0) {
    return {
      minX: 0,
      maxX: viewBoxWidth,
      minY: 0,
      maxY: viewBoxHeight,
      scaleX: 1,
      scaleY: 1,
      offsetX: 0,
      offsetY: 0,
    };
  }

  // Find bounds in metres
  let minX = Infinity;
  let maxX = -Infinity;
  let minY = Infinity;
  let maxY = -Infinity;

  for (const sector of sectors) {
    minX = Math.min(minX, sector.x_m);
    maxX = Math.max(maxX, sector.x_m + (sector.width_m || 0));
    minY = Math.min(minY, sector.y_m);
    maxY = Math.max(maxY, sector.y_m + (sector.height_m || 0));
  }

  // Calculate available space
  const availableWidth = viewBoxWidth - (padding * 2);
  const availableHeight = viewBoxHeight - (padding * 2);

  // Calculate scale to fit
  const dataWidth = maxX - minX;
  const dataHeight = maxY - minY;

  const scaleX = dataWidth > 0 ? availableWidth / dataWidth : 1;
  const scaleY = dataHeight > 0 ? availableHeight / dataHeight : 1;

  // Use smaller scale to maintain aspect ratio
  const scale = Math.min(scaleX, scaleY);

  return {
    minX,
    maxX,
    minY,
    maxY,
    scaleX: scale,
    scaleY: -scale, // Invert Y to match SVG coordinate system
    offsetX: padding,
    offsetY: viewBoxHeight - padding, // Start from bottom
  };
}

/**
 * Transform Django terrain coordinates to SVG coordinates
 */
function toSVGCoordinates(
  xMeters: number,
  yMeters: number,
  scaling: ScalingConfig
): { x: number; y: number } {
  return {
    x: (xMeters - scaling.minX) * scaling.scaleX + scaling.offsetX,
    y: (yMeters - scaling.minY) * scaling.scaleY + scaling.offsetY,
  };
}

/**
 * Map Django sector_type to tactical map display type
 */
function mapSectorType(djangoType: string): 'accessible' | 'blocked' | 'void' | 'water' | 'hazard' {
  // Cave types
  if (['entrance', 'chamber', 'passage', 'junction'].includes(djangoType)) {
    return 'accessible';
  }
  if (['squeeze', 'vertical_shaft', 'tight_passage'].includes(djangoType)) {
    return 'void';
  }
  if (['terminal', 'dead_end', 'collapse'].includes(djangoType)) {
    return 'blocked';
  }

  // Flooded structure types
  if (['cargo_hold', 'engine_room', 'bridge', 'crew_quarters', 'corridor'].includes(djangoType)) {
    return 'accessible';
  }
  if (['hull_breach', 'bilge', 'flooded', 'submerged'].includes(djangoType)) {
    return 'water';
  }
  if (['sealed_passage'].includes(djangoType)) {
    return 'blocked';
  }

  // Industrial types
  if (['utility_corridor', 'equipment_room', 'control_room', 'maintenance_access'].includes(djangoType)) {
    return 'accessible';
  }
  if (['confined_space', 'pipe_corridor', 'tank_chamber', 'hazard_zone'].includes(djangoType)) {
    return 'hazard';
  }

  // Archaeological types
  if (['access_tunnel', 'chamber', 'antechamber', 'corridor'].includes(djangoType)) {
    return 'accessible';
  }
  if (['artifact_alcove', 'inscription_wall', 'sealed_passage'].includes(djangoType)) {
    return 'void';
  }
  if (['collapse_zone'].includes(djangoType)) {
    return 'blocked';
  }

  // Default
  return 'accessible';
}

/**
 * Generate depth/elevation label for sector
 */
function generateDepthElevationLabel(sector: TerrainSector): { depthLabel?: string; elevationLabel?: string } {
  const result: { depthLabel?: string; elevationLabel?: string } = {};

  if (sector.depth_m !== null && sector.depth_m !== undefined) {
    result.depthLabel = `${sector.depth_m.toFixed(1)}m depth`;
  }

  if (sector.elevation_m !== null && sector.elevation_m !== undefined) {
    result.elevationLabel = sector.elevation_m >= 0 
      ? `+${sector.elevation_m.toFixed(1)}m` 
      : `${sector.elevation_m.toFixed(1)}m`;
  } else if (sector.z_m !== null && sector.z_m !== undefined) {
    result.elevationLabel = sector.z_m >= 0 
      ? `+${sector.z_m.toFixed(1)}m` 
      : `${sector.z_m.toFixed(1)}m`;
  }

  return result;
}

/**
 * Transform Django Digital Twin terrain data to tactical map view model
 */
export function adaptDigitalTwinToTacticalMap(
  terrainMap: TerrainMap,
  sectors: TerrainSector[],
  paths: TerrainPath[],
  waypoints: Waypoint[],
  missionState?: MissionSimulationState,
  viewBoxWidth: number = 800,
  viewBoxHeight: number = 450
): TacticalMapViewModel {
  // Calculate coordinate scaling
  const scaling = calculateScaling(sectors, viewBoxWidth, viewBoxHeight);

  // Filter out unexplored sectors (confidence === 0)
  // Only show sectors that have been explored by agents
  const exploredSectors = sectors.filter(sector => 
    sector.confidence === undefined || sector.confidence > 0
  );

  // Transform sectors
  const tacticalSectors: TacticalSector[] = exploredSectors.map((sector, index) => {
    const svgPos = toSVGCoordinates(sector.x_m, sector.y_m, scaling);
    const width = (sector.width_m || 10) * scaling.scaleX;
    const height = Math.abs((sector.height_m || 10) * scaling.scaleY);

    const depthElevation = generateDepthElevationLabel(sector);

    return {
      id: sector.sector_id,
      label: sector.label,
      x: svgPos.x,
      y: svgPos.y - height, // Adjust for SVG top-left origin
      width,
      height,
      type: mapSectorType(sector.sector_type),
      revealAt: 0, // Sector is already explored when it appears
      confidenceAtReveal: sector.confidence,
      metadata: sector.metadata,
      ...depthElevation,
    };
  });

  // TODO: Transform paths to routes
  // TODO: Transform waypoints to tactical waypoints
  // TODO: Extract hazard zones from sector metadata
  // TODO: Generate detection markers from mission state

  return {
    sectors: tacticalSectors,
    width: viewBoxWidth,
    height: viewBoxHeight,
    terrainSource: 'django-digital-twin',
    terrainMeta: {
      siteName: terrainMap.digital_twin_site_name,
      terrainMapName: terrainMap.name,
      siteSlug: terrainMap.digital_twin_site_slug,
      terrainMapSlug: terrainMap.slug,
    },
    coordinateScaling: {
      minX: scaling.minX,
      maxX: scaling.maxX,
      minY: scaling.minY,
      maxY: scaling.maxY,
      scaleX: scaling.scaleX,
      scaleY: scaling.scaleY,
      offsetX: scaling.offsetX,
      offsetY: scaling.offsetY,
    },
  };
}

/**
 * Find sector by alias (for backward compatibility with mission simulation)
 */
export function findSectorByAlias(
  sectors: TacticalSector[],
  alias: string,
  useCase: string
): TacticalSector | undefined {
  // Try direct ID match first
  const directMatch = sectors.find(s => s.id === alias || s.label === alias);
  if (directMatch) {
    return directMatch;
  }

  // Try alias lookup
  const aliases = SECTOR_ALIASES[useCase];
  if (aliases && aliases[alias]) {
    const mappedId = aliases[alias];
    return sectors.find(s => s.id === mappedId);
  }

  return undefined;
}
