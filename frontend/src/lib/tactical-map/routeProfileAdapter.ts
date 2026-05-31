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
import type { MissionSimulationState } from '../types/simulation';

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
  const originSector = sectors.find(s => 
    s.metadata?.entry_point === true || 
    s.sector_type === 'entry' ||
    Math.abs(s.z_m) < 0.1
  ) || sectors[0];

  routeDistances.set(originSector.id, 0);

  // Build a simple route sequence
  // Sort sectors by distance from origin (Euclidean) as a first approximation
  const sortedSectors = [...sectors].sort((a, b) => {
    const distA = Math.sqrt(
      Math.pow(a.x_m - originSector.x_m, 2) + 
      Math.pow(a.y_m - originSector.y_m, 2)
    );
    const distB = Math.sqrt(
      Math.pow(b.x_m - originSector.x_m, 2) + 
      Math.pow(b.y_m - originSector.y_m, 2)
    );
    return distA - distB;
  });

  // Calculate cumulative route distance
  let cumulativeDistance = 0;
  let prevSector = originSector;

  for (const sector of sortedSectors) {
    if (sector.id === originSector.id) continue;

    // Try to find a path between prevSector and current sector
    const path = paths.find(p => 
      (p.from_sector === prevSector.id && p.to_sector === sector.id) ||
      (p.to_sector === prevSector.id && p.from_sector === sector.id)
    );

    if (path && path.distance_m) {
      cumulativeDistance += path.distance_m;
    } else {
      // Fallback: calculate Euclidean distance
      const euclideanDist = Math.sqrt(
        Math.pow(sector.x_m - prevSector.x_m, 2) + 
        Math.pow(sector.y_m - prevSector.y_m, 2)
      );
      cumulativeDistance += euclideanDist;
    }

    routeDistances.set(sector.id, cumulativeDistance);
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
  const zM = sector.z_m;
  
  // Use explicit depth_m or elevation_m if available
  if (sector.depth_m !== undefined && sector.depth_m > 0) {
    return { depthM: sector.depth_m, elevationM: 0 };
  }
  if (sector.elevation_m !== undefined && sector.elevation_m > 0) {
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
  waypoints: Waypoint[],
  missionState?: MissionSimulationState,
  originLabel: string = 'Entry Point'
): RouteProfileViewModel {
  
  const routeDistances = calculateRouteDistances(sectors, paths);
  const points: RouteProfilePoint[] = [];
  const segments: RouteProfileSegment[] = [];

  let maxRouteDistanceM = 0;
  let minZM = 0;
  let maxZM = 0;
  let maxDepthM = 0;
  let maxElevationM = 0;

  // Add origin point
  const originSector = sectors.find(s => 
    s.metadata?.entry_point === true || 
    s.sector_type === 'entry' ||
    Math.abs(s.z_m) < 0.1
  ) || sectors[0];

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

  // Add sector points
  for (const sector of sectors) {
    const routeDistanceM = routeDistances.get(sector.id) || 0;
    const { depthM, elevationM } = calculateDepthElevation(sector);
    const zM = sector.z_m;

    maxRouteDistanceM = Math.max(maxRouteDistanceM, routeDistanceM);
    minZM = Math.min(minZM, zM);
    maxZM = Math.max(maxZM, zM);
    maxDepthM = Math.max(maxDepthM, depthM);
    maxElevationM = Math.max(maxElevationM, elevationM);

    const depthLabel = depthM > 0 ? `↓ ${depthM.toFixed(0)} m` : elevationM > 0 ? `↑ ${elevationM.toFixed(0)} m` : '0 m';

    points.push({
      id: sector.id,
      label: sector.name || `Sector ${sector.id}`,
      type: 'sector',
      routeDistanceM,
      zM,
      depthM,
      elevationM,
      confidence: sector.confidence,
      status: sector.sector_type,
      risk: sector.metadata?.risk_level as string | undefined,
      tooltip: `${sector.name || sector.id}\nRoute: ${routeDistanceM.toFixed(0)} m\n${depthLabel}\nType: ${sector.sector_type}`,
      metadata: sector.metadata
    });
  }

  // Add path segments
  for (const path of paths) {
    const fromDistance = routeDistances.get(path.from_sector) || 0;
    const toDistance = routeDistances.get(path.to_sector) || 0;
    const distanceM = path.distance_m || Math.abs(toDistance - fromDistance);
    const verticalChangeM = path.vertical_change_m || 0;
    const slopePercent = distanceM > 0 ? (Math.abs(verticalChangeM) / distanceM) * 100 : 0;

    segments.push({
      fromId: path.from_sector,
      toId: path.to_sector,
      distanceM,
      verticalChangeM,
      slopePercent,
      traversalRisk: path.traversal_risk,
      status: 'mapped',
      label: path.name || undefined
    });
  }

  // Add mission state overlays if available
  let farthestAgentLabel: string | undefined;
  let farthestAgentDistanceM = 0;
  let farthestAgentDepthM = 0;
  let deepestDetectionM = 0;
  let longestRelayGapM = 0;

  if (missionState && missionState.agents) {
    for (const agent of missionState.agents) {
      // Find sector agent is in
      const agentSector = sectors.find(s => 
        agent.sector === s.id || 
        agent.sector === s.name ||
        (s.metadata?.aliases && (s.metadata.aliases as string[]).includes(agent.sector))
      );

      if (agentSector) {
        const routeDistanceM = routeDistances.get(agentSector.id) || 0;
        const { depthM, elevationM } = calculateDepthElevation(agentSector);
        const zM = agentSector.z_m;

        if (routeDistanceM > farthestAgentDistanceM) {
          farthestAgentDistanceM = routeDistanceM;
          farthestAgentLabel = agent.name;
          farthestAgentDepthM = depthM;
        }

        const agentType = agent.state === 'landed_relay' ? 'relay' : 'agent';

        points.push({
          id: `agent-${agent.id}`,
          label: agent.name,
          type: agentType,
          routeDistanceM,
          zM,
          depthM,
          elevationM,
          status: agent.state,
          tooltip: `${agent.name}\nRoute: ${routeDistanceM.toFixed(0)} m\n${depthM > 0 ? `↓ ${depthM.toFixed(0)} m` : elevationM > 0 ? `↑ ${elevationM.toFixed(0)} m` : '0 m'}\nBattery: ${agent.battery}%\nStatus: ${agent.state}`
        });
      }
    }
  }

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
