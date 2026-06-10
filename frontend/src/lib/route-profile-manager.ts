import {
  getTerrainPaths,
  getTerrainSectors,
  getWaypoints,
  type APIResult,
  type PaginatedResponse,
  type TerrainPath,
  type TerrainSector,
  type Waypoint,
} from './api';
import { initializeRouteProfile, updateRouteProfile } from './route-profile-renderer';
import { adaptToRouteProfile } from './tactical-map/routeProfileAdapter';
import { getTerrainBinding } from './tactical-map/useCaseTerrainBindings';
import type { MissionSimulationState } from '../types/simulation';

interface RouteProfileTerrainData {
  sectors: TerrainSector[];
  paths: TerrainPath[];
  waypoints: Waypoint[];
}

interface RouteProfileOptions {
  containerId?: string;
  originLabel: string;
}

const terrainCache = new Map<string, RouteProfileTerrainData>();

function unpackList<T>(result: APIResult<T[] | PaginatedResponse<T>>): T[] {
  if (!result.success || !result.data) {
    return [];
  }

  return Array.isArray(result.data) ? result.data : result.data.results || [];
}

async function loadRouteProfileTerrain(useCase: string): Promise<RouteProfileTerrainData | null> {
  const cached = terrainCache.get(useCase);
  if (cached) {
    return cached;
  }

  const binding = getTerrainBinding(useCase);
  if (!binding?.terrainMapSlug) {
    return null;
  }

  const [sectorsResult, pathsResult, waypointsResult] = await Promise.all([
    getTerrainSectors(binding.terrainMapSlug),
    getTerrainPaths(binding.terrainMapSlug),
    getWaypoints(binding.terrainMapSlug)
  ]);

  const sectors = unpackList<TerrainSector>(sectorsResult);
  if (sectors.length === 0) {
    return null;
  }

  const terrain = {
    sectors,
    paths: unpackList<TerrainPath>(pathsResult),
    waypoints: unpackList<Waypoint>(waypointsResult)
  };

  terrainCache.set(useCase, terrain);
  return terrain;
}

function setRouteProfileMessage(containerId: string, message: string): void {
  const loadingEl = document.getElementById(`${containerId}-loading`);
  if (loadingEl) {
    loadingEl.textContent = message;
    loadingEl.style.display = 'block';
  }
}

export async function initializeLiveRouteProfile(
  useCase: string,
  options: RouteProfileOptions
): Promise<void> {
  const containerId = options.containerId || 'route-profile';

  try {
    const terrain = await loadRouteProfileTerrain(useCase);
    if (!terrain) {
      setRouteProfileMessage(containerId, 'No route profile data available');
      return;
    }

    const viewModel = adaptToRouteProfile(
      terrain.sectors,
      terrain.paths,
      terrain.waypoints,
      undefined,
      options.originLabel
    );

    initializeRouteProfile(viewModel, { containerId });
  } catch (err) {
    console.error('Route profile initialization failed:', err);
    setRouteProfileMessage(containerId, 'Failed to load route profile');
  }
}

export async function updateLiveRouteProfile(
  useCase: string,
  missionState: MissionSimulationState,
  options: RouteProfileOptions
): Promise<void> {
  const containerId = options.containerId || 'route-profile';

  try {
    const terrain = await loadRouteProfileTerrain(useCase);
    if (!terrain) {
      return;
    }

    const viewModel = adaptToRouteProfile(
      terrain.sectors,
      terrain.paths,
      terrain.waypoints,
      missionState,
      options.originLabel
    );

    updateRouteProfile(viewModel, { containerId });
  } catch (err) {
    console.error('Route profile update failed:', err);
  }
}
