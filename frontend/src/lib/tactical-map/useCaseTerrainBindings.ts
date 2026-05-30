/**
 * Use Case Terrain Bindings
 * 
 * Maps use cases to their Django Digital Twin terrain sources.
 * Provides default terrain configuration for each mission type.
 */

export interface UseCaseTerrainBinding {
  /** Use case identifier (matches URL slug) */
  useCase: string;
  
  /** Terrain data mode */
  mode: 'django-digital-twin' | 'local-fallback';
  
  /** Django site slug (if using digital twin) */
  siteSlug?: string;
  
  /** Terrain map slug (if using digital twin) */
  terrainMapSlug?: string;
  
  /** Entry sector ID for mission start */
  entrySectorId?: string;
  
  /** Human-readable note or TODO */
  note?: string;
}

/**
 * Terrain bindings for all use cases
 * 
 * Source data verified from: backend/get_map_slugs.py
 */
export const USE_CASE_TERRAIN_BINDINGS: Record<string, UseCaseTerrainBinding> = {
  'cave-rescue': {
    useCase: 'cave-rescue',
    mode: 'django-digital-twin',
    siteSlug: 'migovec-primadona-demo',
    terrainMapSlug: 'primadona-entrance-zone',
    entrySectorId: 'chamber-1',
  },
  
  'flooded-structure': {
    useCase: 'flooded-structure',
    mode: 'django-digital-twin',
    siteSlug: 'liberty-cargo-vessel-demo',
    terrainMapSlug: 'main-deck-holds',
    entrySectorId: 'bilge-compartment',
  },
  
  'industrial-inspection': {
    useCase: 'industrial-inspection',
    mode: 'django-digital-twin',
    siteSlug: 'industrial-confined-space-demo',
    terrainMapSlug: 'processing-section-level-2',
    entrySectorId: 'access-shaft-01',
  },
  
  'archaeological-exploration': {
    useCase: 'archaeological-exploration',
    mode: 'django-digital-twin',
    siteSlug: 'heritage-underground-chamber-demo',
    terrainMapSlug: 'underground-chamber-complex',
    entrySectorId: 'access-tunnel',
  },
  
  'collapsed-building-search': {
    useCase: 'collapsed-building-search',
    mode: 'local-fallback',
    note: 'TODO: Create collapsed-building digital twin seed',
  },
};

/**
 * Get terrain binding for a use case
 */
export function getTerrainBinding(useCase: string): UseCaseTerrainBinding | null {
  return USE_CASE_TERRAIN_BINDINGS[useCase] || null;
}

/**
 * Check if use case has Digital Twin terrain available
 */
export function hasDigitalTwinTerrain(useCase: string): boolean {
  const binding = getTerrainBinding(useCase);
  return binding?.mode === 'django-digital-twin';
}

/**
 * Get all use cases with Digital Twin terrain
 */
export function getUseCasesWithDigitalTwin(): string[] {
  return Object.keys(USE_CASE_TERRAIN_BINDINGS).filter(
    useCase => USE_CASE_TERRAIN_BINDINGS[useCase].mode === 'django-digital-twin'
  );
}
