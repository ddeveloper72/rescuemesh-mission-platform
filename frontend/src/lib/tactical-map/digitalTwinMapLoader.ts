/**
 * Digital Twin Map Loader
 * 
 * Async loader for Django Digital Twin terrain data.
 * Bridges the gap between async API calls and sync tactical map rendering.
 */

import {
  getTerrainMaps,
  getTerrainSectors,
  getTerrainPaths,
  getWaypoints,
  type TerrainMap,
  type TerrainSector,
  type TerrainPath,
  type Waypoint,
} from '../api';

import {
  adaptDigitalTwinToTacticalMap,
  type TacticalMapViewModel,
} from './digitalTwinMapAdapter';

import {
  getTerrainBinding,
  hasDigitalTwinTerrain,
} from './useCaseTerrainBindings';

/**
 * Result of Digital Twin loading
 */
export interface DigitalTwinLoadResult {
  success: boolean;
  viewModel?: TacticalMapViewModel;
  error?: string;
  terrainSource: 'django-digital-twin' | 'local-fallback';
}

/**
 * Cache for loaded Digital Twin data (per use case)
 */
const digitalTwinCache = new Map<string, TacticalMapViewModel>();

/**
 * Load Digital Twin map data for a use case
 * 
 * @param useCase - Use case identifier (e.g., 'cave-rescue')
 * @param forceReload - Force reload even if cached
 * @returns Digital Twin load result with view model or error
 */
export async function loadDigitalTwinMap(
  useCase: string,
  forceReload: boolean = false
): Promise<DigitalTwinLoadResult> {
  // Check if use case has Digital Twin terrain
  if (!hasDigitalTwinTerrain(useCase)) {
    return {
      success: false,
      error: 'Use case does not have Digital Twin terrain configured',
      terrainSource: 'local-fallback',
    };
  }

  // Check cache
  if (!forceReload && digitalTwinCache.has(useCase)) {
    return {
      success: true,
      viewModel: digitalTwinCache.get(useCase)!,
      terrainSource: 'django-digital-twin',
    };
  }

  // Get binding
  const binding = getTerrainBinding(useCase);
  if (!binding || !binding.terrainMapSlug) {
    return {
      success: false,
      error: 'Invalid terrain binding configuration',
      terrainSource: 'local-fallback',
    };
  }

  try {
    // Fetch terrain map
    const mapsResult = await getTerrainMaps(binding.siteSlug);
    if (!mapsResult.success || !mapsResult.data || mapsResult.data.length === 0) {
      return {
        success: false,
        error: `Failed to load terrain map: ${mapsResult.error || 'No data'}`,
        terrainSource: 'local-fallback',
      };
    }

    const terrainMap = mapsResult.data.find(m => m.slug === binding.terrainMapSlug);
    if (!terrainMap) {
      return {
        success: false,
        error: `Terrain map not found: ${binding.terrainMapSlug}`,
        terrainSource: 'local-fallback',
      };
    }

    // Fetch related data in parallel
    const [sectorsResult, pathsResult, waypointsResult] = await Promise.all([
      getTerrainSectors(binding.terrainMapSlug),
      getTerrainPaths(binding.terrainMapSlug),
      getWaypoints(binding.terrainMapSlug),
    ]);

    if (!sectorsResult.success || !sectorsResult.data) {
      return {
        success: false,
        error: `Failed to load sectors: ${sectorsResult.error}`,
        terrainSource: 'local-fallback',
      };
    }

    const sectors = sectorsResult.data;
    const paths = pathsResult.data || [];
    const waypoints = waypointsResult.data || [];

    // Adapt to tactical map view model
    const viewModel = adaptDigitalTwinToTacticalMap(
      terrainMap,
      sectors,
      paths,
      waypoints,
      undefined,
      800,
      450
    );

    // Cache result
    digitalTwinCache.set(useCase, viewModel);

    return {
      success: true,
      viewModel,
      terrainSource: 'django-digital-twin',
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      terrainSource: 'local-fallback',
    };
  }
}

/**
 * Clear Digital Twin cache for a use case (or all if not specified)
 */
export function clearDigitalTwinCache(useCase?: string) {
  if (useCase) {
    digitalTwinCache.delete(useCase);
  } else {
    digitalTwinCache.clear();
  }
}

/**
 * Preload Digital Twin data for multiple use cases
 * Useful for warming the cache on app startup
 */
export async function preloadDigitalTwinMaps(useCases: string[]): Promise<void> {
  await Promise.all(useCases.map(uc => loadDigitalTwinMap(uc)));
}
