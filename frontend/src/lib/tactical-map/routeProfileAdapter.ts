/**
 * Route Profile Adapter
 * 
 * Transforms Django Digital Twin terrain data and mission state into a Route Profile view model.
 * The Route Profile shows mission progress along the route distance (X-axis) vs depth/elevation (Y-axis).
 * 
 * Purpose:
 * - Complement the top-down tactical map with a side-view profile
 * - Show how far agents have travelled from entry point
 * - Show depth below or elevation above the origin
 * - Visualize relay gaps, return distance, and vertical hazards
 */

import type { TerrainSector, TerrainPath, Waypoint } from '../api';
import type { Agent, MissionSimulationState } from '../../types/simulation';

// ============================================================================
// Route Profile View Model Types
// ============================================================================

export interface RouteProfilePoint {
  id: string;
  label: string;
  type: 'sector' | 'agent' | 'relay' | 'hazard' | 'detection' | 'waypoint' | 'origin';
  routeDistanceM: number;
  zM: number;
  depthM: number;
  elevationM: number;
  confidence?: number;
  status?: string;
  risk?: string;
  tooltip?: string;
  metadata?: Record<string, any>;
}

export interface RouteProfileSegment {
  fromId: string;
  toId: string;
  distanceM: number;
  verticalChangeM: number;
  slopePercent?: number;
  traversalRisk?: string;
  status?: string;
  label?: string;
}

export interface RouteProfileViewModel {
  originLabel: string;
  maxRouteDistanceM: number;
  minZM: number;
  maxZM: number;
  points: RouteProfilePoint[];
  segments: RouteProfileSegment[];
  summary: {
    farthestAgentLabel?: string;
    farthestAgentDistanceM?: number;
    farthestAgentDepthM?: number;
    maxDepthM?: number;
    maxElevationM?: number;
    longestRelayGapM?: number;
    returnRisk?: string;
    contactContinuityRisk?: string;
    deepestDetectionM?: number;
  };
}

function getNumber(value: number | null | undefined, fallback = 0): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

function getSectorZ(sector: TerrainSector): number {
  return getNumber(sector.z_m);
}

function getSectorLabel(sector: TerrainSector): string {
  return sector.label || sector.sector_id || sector.id;
}

function getSectorRouteKey(sector: TerrainSector): string {
  return sector.sector_id || sector.id;
}

function getSectorKeys(sector: TerrainSector): string[] {
  return [sector.id, sector.sector_id, sector.label].filter(Boolean);
}

function pathEndpointKeys(path: TerrainPath): [string[], string[]] {
  return [
    [path.from_sector, path.from_sector_id, path.from_sector_label].filter(Boolean),
    [path.to_sector, path.to_sector_id, path.to_sector_label].filter(Boolean)
  ];
}

function hasIntersection(a: string[], b: string[]): boolean {
  return a.some(value => b.includes(value));
}

function sectorsMatchPath(path: TerrainPath, fromKeys: string[], toKeys: string[]): boolean {
  const [pathFromKeys, pathToKeys] = pathEndpointKeys(path);
  return (
    hasIntersection(pathFromKeys, fromKeys) && hasIntersection(pathToKeys, toKeys)
  ) || (
    hasIntersection(pathFromKeys, toKeys) && hasIntersection(pathToKeys, fromKeys)
  );
}

function findPointBySectorReference(points: RouteProfilePoint[], sectorReference: string): RouteProfilePoint | undefined {
  return points.find(point => {
    const sectorKeys = point.metadata?.sectorKeys as string[] | undefined;
    return point.id === sectorReference || sectorKeys?.includes(sectorReference);
  });
}

function findAgentSector(agent: Agent, sectors: TerrainSector[]): TerrainSector | undefined {
  const nav = agent.navigation as any;
  const possibleRefs = [
    (agent as any).sector,
    nav?.sector,
    nav?.sector_id,
    nav?.current_sector,
    agent.location_label
  ].filter(Boolean);

  return sectors.find(sector => {
    const keys = getSectorKeys(sector);
    return possibleRefs.some(ref => keys.includes(ref));
  });
}

function isOriginSector(sector: TerrainSector): boolean {
  const sectorType = sector.sector_type.toLowerCase();
  const sectorId = sector.sector_id.toLowerCase();
  const label = sector.label.toLowerCase();

  return (
    sector.metadata?.entry_point === true ||
    sector.metadata?.surface_access === true ||
    sectorType === 'entry' ||
    sectorType === 'entrance' ||
    sectorId.includes('entry') ||
    label.includes('entry')
  );
}

function findOriginSector(sectors: TerrainSector[]): TerrainSector {
  return sectors.find(isOriginSector) ||
    sectors.find(sector => Math.abs(getSectorZ(sector)) < 0.1) ||
    sectors[0] as TerrainSector;
}

function hasMissionStarted(missionState?: MissionSimulationState): boolean {
  if (!missionState) {
    return false;
  }

  return Boolean(
    missionState.simulation_clock?.is_running ||
    (missionState.simulation_clock?.elapsed_seconds ?? 0) > 0 ||
    missionState.mission?.status !== 'not_started'
  );
}

function getSectorMissionConfidence(
  missionState: MissionSimulationState | undefined,
  sector: TerrainSector
): number | undefined {
  const missionSector = missionState?.sectors?.find(stateSector => (
    stateSector.sector_id === sector.sector_id ||
    stateSector.sector_id === sector.id ||
    stateSector.label === sector.label
  ));

  return (missionSector as any)?.confidence;
}

// ============================================================================
// Route Calculation
// ============================================================================

/**
 * Calculate cumulative route distance for each sector based on path segments.
 * 
 * Strategy:
 * 1. Identify the origin/entry sector (z=0 or metadata.entry_point=true)
 * 2. Build a route sequence based on path connections
 * 3. Sum path distances to calculate route distance for each sector
 * 
 * For MVP, we use a simple sequential approach:
 * - Sort sectors by typical progression (entrance → deeper sectors)
 * - Calculate Euclidean distance if path distance not available
 * 
 * TODO: Implement graph-based route calculation for complex branching routes
 */
function calculateRouteDistances(
  sectors: TerrainSector[],
  paths: TerrainPath[]
): Map<string, number> {
  const routeDistances = new Map<string, number>();
  
  if (sectors.length === 0) {
    return routeDistances;
  }

  // Find origin sector (entry point)
  const originSector = findOriginSector(sectors);

  routeDistances.set(getSectorRouteKey(originSector), 0);

  // Build a simple route sequence
  // Sort sectors by distance from origin (Euclidean) as a first approximation
  const sortedSectors = [...sectors].sort((a, b) => {
    const distA = Math.sqrt(
      Math.pow(getNumber(a.x_m) - getNumber(originSector.x_m), 2) + 
      Math.pow(getNumber(a.y_m) - getNumber(originSector.y_m), 2)
    );
    const distB = Math.sqrt(
      Math.pow(getNumber(b.x_m) - getNumber(originSector.x_m), 2) + 
      Math.pow(getNumber(b.y_m) - getNumber(originSector.y_m), 2)
    );
    return distA - distB;
  });

  // Calculate cumulative route distance
  let cumulativeDistance = 0;
  let prevSector = originSector;

  for (const sector of sortedSectors) {
    if (sector.id === originSector.id) continue;

    // Try to find a path between prevSector and current sector
    const prevKeys = getSectorKeys(prevSector);
    const sectorKeys = getSectorKeys(sector);
    const path = paths.find(p => sectorsMatchPath(p, prevKeys, sectorKeys));

    if (path && path.distance_m) {
      cumulativeDistance += path.distance_m;
    } else {
      // Fallback: calculate Euclidean distance
      const euclideanDist = Math.sqrt(
        Math.pow(getNumber(sector.x_m) - getNumber(prevSector.x_m), 2) + 
        Math.pow(getNumber(sector.y_m) - getNumber(prevSector.y_m), 2)
      );
      cumulativeDistance += euclideanDist;
    }

    routeDistances.set(getSectorRouteKey(sector), cumulativeDistance);
    prevSector = sector;
  }

  return routeDistances;
}

// ============================================================================
// Depth and Elevation Calculation
// ============================================================================

/**
 * Calculate depth and elevation relative to origin.
 * 
 * Definitions:
 * - z = 0 at origin (entry point)
 * - positive z = above origin (elevation)
 * - negative z = below origin (depth)
 * - depthM = abs(z) when z < 0
 * - elevationM = z when z > 0
 */
function calculateDepthElevation(sector: TerrainSector): { depthM: number; elevationM: number } {
  const zM = getSectorZ(sector);
  
  // Use explicit depth_m or elevation_m if available
  if (sector.depth_m !== undefined && sector.depth_m !== null && sector.depth_m > 0) {
    return { depthM: sector.depth_m, elevationM: 0 };
  }
  if (sector.elevation_m !== undefined && sector.elevation_m !== null && sector.elevation_m > 0) {
    return { depthM: 0, elevationM: sector.elevation_m };
  }

  // Calculate from z_m
  if (zM < 0) {
    return { depthM: Math.abs(zM), elevationM: 0 };
  } else if (zM > 0) {
    return { depthM: 0, elevationM: zM };
  } else {
    return { depthM: 0, elevationM: 0 };
  }
}

// ============================================================================
// Main Adapter Function
// ============================================================================

export function adaptToRouteProfile(
  sectors: TerrainSector[],
  paths: TerrainPath[],
  _waypoints: Waypoint[],
  missionState?: MissionSimulationState,
  originLabel: string = 'Entry Point'
): RouteProfileViewModel {
  
  const routeDistances = calculateRouteDistances(sectors, paths);
  const points: RouteProfilePoint[] = [];
  const segments: RouteProfileSegment[] = [];

  let maxRouteDistanceM = 0;
  let maxDepthM = 0;
  let maxElevationM = 0;

  // Add origin point
  const originSector = findOriginSector(sectors);

  if (originSector) {
    points.push({
      id: 'origin',
      label: originLabel,
      type: 'origin',
      routeDistanceM: 0,
      zM: 0,
      depthM: 0,
      elevationM: 0,
      confidence: 1.0,
      status: 'entry',
      tooltip: `${originLabel} (Route: 0 m, Elevation: 0 m)`
    });
  }

  // Filter sectors to only show explored ones (confidence > 0)
  const exploredSectors = sectors.filter(sector => {
    const missionConfidence = getSectorMissionConfidence(missionState, sector);
    if (missionConfidence !== undefined) {
      return missionConfidence > 0;
    }

    return sector.confidence === undefined || sector.confidence > 0;
  });

  // Add sector points (but don't use them for scale calculation yet)
  for (const sector of exploredSectors) {
    const routeDistanceM = routeDistances.get(getSectorRouteKey(sector)) || 0;
    const { depthM, elevationM } = calculateDepthElevation(sector);
    const zM = getSectorZ(sector);
    const label = getSectorLabel(sector);
    const confidence = getSectorMissionConfidence(missionState, sector) ?? sector.confidence;

    maxRouteDistanceM = Math.max(maxRouteDistanceM, routeDistanceM);
    maxDepthM = Math.max(maxDepthM, depthM);
    maxElevationM = Math.max(maxElevationM, elevationM);

    const depthLabel = depthM > 0 ? `↓ ${depthM.toFixed(0)} m` : elevationM > 0 ? `↑ ${elevationM.toFixed(0)} m` : '0 m';

    points.push({
      id: sector.id,
      label,
      type: 'sector',
      routeDistanceM,
      zM,
      depthM,
      elevationM,
      confidence,
      status: sector.sector_type,
      risk: sector.metadata?.risk_level as string | undefined,
      tooltip: `${label}\nRoute: ${routeDistanceM.toFixed(0)} m\n${depthLabel}\nType: ${sector.sector_type}`,
      metadata: {
        ...sector.metadata,
        sectorKeys: getSectorKeys(sector)
      }
    });
  }

  // Add path segments
  for (const path of paths) {
    const fromDistance = routeDistances.get(path.from_sector_id) || routeDistances.get(path.from_sector) || 0;
    const toDistance = routeDistances.get(path.to_sector_id) || routeDistances.get(path.to_sector) || 0;
    const distanceM = path.distance_m || Math.abs(toDistance - fromDistance);
    const verticalChangeM = getNumber(path.vertical_change_m);
    const slopePercent = distanceM > 0 ? (Math.abs(verticalChangeM) / distanceM) * 100 : 0;

    segments.push({
      fromId: findPointBySectorReference(points, path.from_sector_id || path.from_sector)?.id || path.from_sector,
      toId: findPointBySectorReference(points, path.to_sector_id || path.to_sector)?.id || path.to_sector,
      distanceM,
      verticalChangeM,
      slopePercent,
      traversalRisk: path.traversal_risk,
      status: 'mapped',
      label: `${path.from_sector_label || path.from_sector_id} to ${path.to_sector_label || path.to_sector_id}`
    });
  }

  // Add mission state overlays if available
  let farthestAgentLabel: string | undefined;
  let farthestAgentDistanceM = 0;
  let farthestAgentDepthM = 0;
  let deepestDetectionM = 0;
  let longestRelayGapM = 0;

  // Track agent Z positions for dynamic scale calculation
  const agentZPositions: number[] = [0]; // Always include ground level (origin)

  if (hasMissionStarted(missionState) && missionState?.agents) {
    for (const agent of missionState.agents) {
      const agentSector = findAgentSector(agent, sectors);

      if (agentSector) {
        const routeDistanceM = routeDistances.get(getSectorRouteKey(agentSector)) || 0;
        const { depthM, elevationM } = calculateDepthElevation(agentSector);
        const zM = getSectorZ(agentSector);

        // Track agent Z position for scale calculation
        agentZPositions.push(zM);

        if (routeDistanceM > farthestAgentDistanceM) {
          farthestAgentDistanceM = routeDistanceM;
          farthestAgentLabel = agent.name;
          farthestAgentDepthM = depthM;
        }

        const agentType = agent.state === 'landed_relay' ? 'relay' : 'agent';

        points.push({
          id: `agent-${agent.agent_id}`,
          label: agent.name,
          type: agentType,
          routeDistanceM,
          zM,
          depthM,
          elevationM,
          status: agent.state,
          tooltip: `${agent.name}\nRoute: ${routeDistanceM.toFixed(0)} m\n${depthM > 0 ? `↓ ${depthM.toFixed(0)} m` : elevationM > 0 ? `↑ ${elevationM.toFixed(0)} m` : '0 m'}\nBattery: ${agent.battery_percent}%\nStatus: ${agent.state}`
        });
      }
    }
  }

  // Calculate dynamic scale based on ACTUAL agent positions (not full terrain data)
  // This reveals depth/height progressively as agents explore
  const actualMinZ = Math.min(...agentZPositions);
  const actualMaxZ = Math.max(...agentZPositions);
  
  // Add 20% padding for visual clarity
  const zRange = Math.max(Math.abs(actualMaxZ - actualMinZ), 10); // Minimum 10m range
  const padding = zRange * 0.2;
  
  const minZM = Math.floor(actualMinZ - padding);
  const maxZM = Math.ceil(actualMaxZ + padding);

  // TODO: Add detection markers, hazard markers from mission state

  // Calculate summary
  const summary = {
    farthestAgentLabel,
    farthestAgentDistanceM,
    farthestAgentDepthM,
    maxDepthM,
    maxElevationM,
    longestRelayGapM,
    returnRisk: farthestAgentDistanceM > 1000 ? 'high' : farthestAgentDistanceM > 500 ? 'moderate' : 'low',
    contactContinuityRisk: longestRelayGapM > 300 ? 'critical' : longestRelayGapM > 150 ? 'high' : 'stable',
    deepestDetectionM
  };
  
  console.log('[RouteProfileAdapter] Calculated summary:', {
    farthestAgentLabel,
    farthestAgentDistanceM,
    farthestAgentDepthM,
    maxDepthM,
    maxElevationM,
    missionStateProvided: !!missionState,
    agentCount: missionState?.agents?.length || 0,
    dynamicScale: { minZM, maxZM },
    agentZPositions: agentZPositions.length
  });

  return {
    originLabel,
    maxRouteDistanceM,
    minZM,
    maxZM,
    points,
    segments,
    summary
  };
}
