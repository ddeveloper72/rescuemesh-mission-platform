/**
 * RescueMesh Django API Client
 * 
 * Provides typed fetch helpers with graceful error handling.
 * Falls back to local data if Django API is unavailable.
 */

// API base URL - different for server-side (Docker) vs client-side (browser)
// Server-side (Astro SSR): Use Docker service name 'backend'
// Client-side (browser): Use localhost (Docker port forwarding)
export const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.PUBLIC_DJANGO_API_BASE_URL;
  
  // If running server-side (SSR), prefer the environment variable.
  // Docker sets this to http://backend:8000/api/v1; local Astro dev should
  // fall back to localhost because the Docker service hostname is unavailable.
  if (typeof window === 'undefined') {
    return envUrl || 'http://localhost:8000/api/v1';
  }
  
  // If running client-side (browser), always use localhost
  // This works because Docker forwards port 8000 to the host
  return 'http://localhost:8000/api/v1';
};

const API_BASE_URL = getApiBaseUrl();

/**
 * API endpoint definitions
 */
export const API_ENDPOINTS = {
  useCases: {
    list: () => `${API_BASE_URL}/usecases/`,
    detail: (slug: string) => `${API_BASE_URL}/usecases/${slug}/`,
    demoProfile: (slug: string) => `${API_BASE_URL}/usecases/${slug}/demo_profile/`,
  },
  agentRoles: {
    list: () => `${API_BASE_URL}/agent-role-templates/`,
    detail: (id: string) => `${API_BASE_URL}/agent-role-templates/${id}/`,
  },
  terrainProfiles: {
    list: () => `${API_BASE_URL}/terrain-profiles/`,
    detail: (id: string) => `${API_BASE_URL}/terrain-profiles/${id}/`,
  },
  sensors: {
    list: () => `${API_BASE_URL}/sensors/`,
    detail: (id: string) => `${API_BASE_URL}/sensors/${id}/`,
  },
  failures: {
    list: () => `${API_BASE_URL}/failures/`,
    detail: (id: string) => `${API_BASE_URL}/failures/${id}/`,
  },
  outputs: {
    list: () => `${API_BASE_URL}/outputs/outputs/`,
    detail: (id: string) => `${API_BASE_URL}/outputs/outputs/${id}/`,
  },
  prompts: {
    list: () => `${API_BASE_URL}/prompts/`,
    detail: (id: string) => `${API_BASE_URL}/prompts/${id}/`,
  },
  missions: {
    list: () => `${API_BASE_URL}/missions/`,
    detail: (id: string) => `${API_BASE_URL}/missions/${id}/`,
  },
  agents: {
    list: () => `${API_BASE_URL}/agents/`,
    detail: (id: string) => `${API_BASE_URL}/agents/${id}/`,
  },
  // Digital Twin / Mapping endpoints
  digitalTwinSites: {
    list: () => `${API_BASE_URL}/mapping/digital-twin-sites/`,
    detail: (slug: string) => `${API_BASE_URL}/mapping/digital-twin-sites/${slug}/`,
  },
  terrainMaps: {
    list: (params?: { site_slug?: string }) => {
      const url = `${API_BASE_URL}/mapping/terrain-maps/`;
      if (params?.site_slug) {
        return `${url}?site_slug=${encodeURIComponent(params.site_slug)}`;
      }
      return url;
    },
    detail: (slug: string) => `${API_BASE_URL}/mapping/terrain-maps/${slug}/`,
  },
  terrainSectors: {
    list: (params?: { terrain_map_slug?: string; sector_type?: string }) => {
      const url = `${API_BASE_URL}/mapping/terrain-sectors/`;
      const queryParams = new URLSearchParams();
      if (params?.terrain_map_slug) {
        queryParams.append('terrain_map_slug', params.terrain_map_slug);
      }
      if (params?.sector_type) {
        queryParams.append('sector_type', params.sector_type);
      }
      return queryParams.toString() ? `${url}?${queryParams.toString()}` : url;
    },
  },
  terrainPaths: {
    list: (params?: { terrain_map_slug?: string; path_type?: string }) => {
      const url = `${API_BASE_URL}/mapping/terrain-paths/`;
      const queryParams = new URLSearchParams();
      if (params?.terrain_map_slug) {
        queryParams.append('terrain_map_slug', params.terrain_map_slug);
      }
      if (params?.path_type) {
        queryParams.append('path_type', params.path_type);
      }
      return queryParams.toString() ? `${url}?${queryParams.toString()}` : url;
    },
  },
  waypoints: {
    list: (params?: { terrain_map_slug?: string; route_group?: string }) => {
      const url = `${API_BASE_URL}/mapping/waypoints/`;
      const queryParams = new URLSearchParams();
      if (params?.terrain_map_slug) {
        queryParams.append('terrain_map_slug', params.terrain_map_slug);
      }
      if (params?.route_group) {
        queryParams.append('route_group', params.route_group);
      }
      return queryParams.toString() ? `${url}?${queryParams.toString()}` : url;
    },
  },
  mapArtifacts: {
    list: () => `${API_BASE_URL}/mapping/map-artifacts/`,
  },
};

/**
 * API fetch result with success flag and optional data
 */
export interface APIResult<T> {
  success: boolean;
  data?: T;
  error?: string;
}

/**
 * Fetch data from Django API with error handling
 * Returns a result object instead of throwing
 */
export async function fetchAPI<T>(url: string): Promise<APIResult<T>> {
  try {
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      return {
        success: false,
        error: `API request failed: ${response.status} ${response.statusText}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      data,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Fetch with automatic fallback to local data
 */
export async function fetchWithFallback<T>(
  url: string,
  fallbackData: T
): Promise<T> {
  const result = await fetchAPI<T>(url);
  return result.success && result.data ? result.data : fallbackData;
}

/**
 * Fetch with fallback while preserving which source was used.
 */
export async function fetchWithFallbackSource<T>(
  url: string,
  fallbackData: T
): Promise<{ data: T; source: 'django' | 'fallback' }> {
  const result = await fetchAPI<T>(url);
  if (result.success && result.data) {
    return { data: result.data, source: 'django' };
  }
  return { data: fallbackData, source: 'fallback' };
}

/**
 * Django API response types
 */
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface UseCaseListItem {
  id: string;
  slug: string;
  title: string;
  priority: string;
  summary: string;
  is_active: boolean;
  is_demo: boolean;
  created_at: string;
}

export interface SensorPackage {
  id: string;
  agent_role: string;
  agent_role_name: string;
  use_case_slug: string;
  sensor_type: string;
  display_name: string;
  description: string;
  data_format: string;
  expected_output: string;
  specifications: Record<string, any>;
  failure_modes: string[];
  created_at: string;
  updated_at: string;
}

export interface FailureProfile {
  id: string;
  use_case: string;
  use_case_slug: string;
  use_case_title: string;
  name: string;
  description: string;
  affected_component: string;
  severity: string;
  trigger_type: string;
  trigger_conditions: Record<string, any>;
  effects: Record<string, any>;
  operator_message: string;
  is_recoverable: boolean;
  recovery_actions: string[];
  created_at: string;
  updated_at: string;
}

export interface ExpectedOutput {
  id: string;
  use_case: string;
  use_case_slug: string;
  use_case_title: string;
  name: string;
  output_type: string;
  description: string;
  confidence_required: boolean;
  human_review_required: boolean;
  display_priority: number;
  icon_name: string;
  output_schema: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface AgentRoleTemplate {
  id: string;
  use_case: string;
  use_case_slug: string;
  use_case_title: string;
  name: string;
  role: string;
  agent_type: string;
  description: string;
  capabilities: Record<string, any>;
  specifications: Record<string, any>;
  is_required: boolean;
  recommended_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * Digital Twin / Mapping API types
 */
export interface DigitalTwinSite {
  id: string;
  slug: string;
  name: string;
  site_type: 'cave' | 'archaeology' | 'industrial' | 'synthetic';
  country: string;
  description: string;
  source_name: string;
  source_url: string;
  source_license: string;
  attribution: string;
  sensitivity_level: 'public_demo' | 'reduced_precision' | 'restricted' | 'synthetic_only';
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface TerrainMap {
  id: string;
  slug: string;
  digital_twin_site: string;
  digital_twin_site_slug: string;
  digital_twin_site_name: string;
  name: string;
  description: string;
  coordinate_system: string;
  origin_lat: number | null;
  origin_lon: number | null;
  origin_label: string;
  units: string;
  source_format: string;
  sector_count: number;
  waypoint_count: number;
  created_at: string;
  updated_at: string;
}

export interface TerrainSector {
  id: string;
  terrain_map: string;
  terrain_map_slug: string;
  sector_id: string;
  label: string;
  sector_type: string;
  x_m: number;
  y_m: number;
  z_m: number | null;
  width_m: number | null;
  height_m: number | null;
  depth_m: number | null;
  elevation_m: number | null;
  confidence: number;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface TerrainPath {
  id: string;
  terrain_map: string;
  terrain_map_slug: string;
  from_sector: string;
  from_sector_id: string;
  from_sector_label: string;
  to_sector: string;
  to_sector_id: string;
  to_sector_label: string;
  distance_m: number;
  bearing_deg: number | null;
  vertical_change_m: number | null;
  path_type: string;
  traversal_risk: string;
  capabilities_required: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Waypoint {
  id: string;
  terrain_map: string;
  terrain_map_slug: string;
  waypoint_id: string;
  label: string;
  x_m: number;
  y_m: number;
  z_m: number | null;
  sequence: number | null;
  route_group: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface MapArtifact {
  id: string;
  digital_twin_site: string;
  artifact_type: string;
  file_format: string;
  description: string;
  file_path: string;
  external_url: string;
  licensing_notes: string;
  created_at: string;
  updated_at: string;
}

/**
 * Fetch functions for common data
 */
export async function getUseCases(): Promise<APIResult<PaginatedResponse<UseCaseListItem>>> {
  return fetchAPI<PaginatedResponse<UseCaseListItem>>(API_ENDPOINTS.useCases.list());
}

export async function getSensors(): Promise<APIResult<PaginatedResponse<SensorPackage>>> {
  return fetchAPI<PaginatedResponse<SensorPackage>>(API_ENDPOINTS.sensors.list());
}

export async function getFailures(): Promise<APIResult<PaginatedResponse<FailureProfile>>> {
  return fetchAPI<PaginatedResponse<FailureProfile>>(API_ENDPOINTS.failures.list());
}

export async function getOutputs(): Promise<APIResult<PaginatedResponse<ExpectedOutput>>> {
  return fetchAPI<PaginatedResponse<ExpectedOutput>>(API_ENDPOINTS.outputs.list());
}

export async function getAgentRoles(): Promise<APIResult<PaginatedResponse<AgentRoleTemplate>>> {
  return fetchAPI<PaginatedResponse<AgentRoleTemplate>>(API_ENDPOINTS.agentRoles.list());
}

/**
 * Digital Twin / Mapping fetch functions
 */

/**
 * Fetch Digital Twin Sites
 */
export async function getDigitalTwinSites(): Promise<APIResult<DigitalTwinSite[]>> {
  return await fetchAPI<DigitalTwinSite[]>(API_ENDPOINTS.digitalTwinSites.list());
}

/**
 * Fetch Terrain Maps (optionally filtered by site slug)
 */
export async function getTerrainMaps(siteSlug?: string): Promise<APIResult<TerrainMap[]>> {
  const url = siteSlug 
    ? API_ENDPOINTS.terrainMaps.list({ site_slug: siteSlug })
    : API_ENDPOINTS.terrainMaps.list();
  return await fetchAPI<TerrainMap[]>(url);
}

/**
 * Fetch Terrain Sectors (optionally filtered by terrain map slug)
 */
export async function getTerrainSectors(
  terrainMapSlug?: string, 
  sectorType?: string
): Promise<APIResult<TerrainSector[]>> {
  const url = API_ENDPOINTS.terrainSectors.list({ 
    terrain_map_slug: terrainMapSlug,
    sector_type: sectorType 
  });
  return await fetchAPI<TerrainSector[]>(url);
}

/**
 * Fetch Terrain Paths (optionally filtered by terrain map slug)
 */
export async function getTerrainPaths(
  terrainMapSlug?: string,
  pathType?: string
): Promise<APIResult<TerrainPath[]>> {
  const url = API_ENDPOINTS.terrainPaths.list({ 
    terrain_map_slug: terrainMapSlug,
    path_type: pathType 
  });
  return await fetchAPI<TerrainPath[]>(url);
}

/**
 * Fetch Waypoints (optionally filtered by terrain map slug)
 */
export async function getWaypoints(
  terrainMapSlug?: string,
  routeGroup?: string
): Promise<APIResult<Waypoint[]>> {
  const url = API_ENDPOINTS.waypoints.list({ 
    terrain_map_slug: terrainMapSlug,
    route_group: routeGroup 
  });
  return await fetchAPI<Waypoint[]>(url);
}

/**
 * Mission simulation functions
 */
import type {
  MissionSimulationState,
  SpeedControlRequest,
  SpeedControlResponse,
  SimulationControlResponse
} from '../types/simulation';

/**
 * Get the current mission simulation state.
 * 
 * @param missionPk - Mission primary key (UUID)
 * @returns Current simulation state including agents, sensors, map, events, AI analysis
 */
export async function getMissionState(
  missionPk: string
): Promise<APIResult<MissionSimulationState>> {
  return fetchAPI<MissionSimulationState>(
    `${API_BASE_URL}/missions/${missionPk}/state/`
  );
}

/**
 * Start the mission simulation.
 * 
 * @param missionPk - Mission primary key (UUID)
 * @returns Control response with status
 */
export async function startSimulation(
  missionPk: string
): Promise<APIResult<SimulationControlResponse>> {
  const response = await fetch(`${API_BASE_URL}/missions/${missionPk}/start-sim/`, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    return {
      success: false,
      error: `Start simulation failed: ${response.status} ${response.statusText}`,
    };
  }

  const data = await response.json();
  return {
    success: true,
    data,
  };
}

/**
 * Pause the mission simulation.
 * 
 * @param missionPk - Mission primary key (UUID)
 * @returns Control response with status
 */
export async function pauseSimulation(
  missionPk: string
): Promise<APIResult<SimulationControlResponse>> {
  const response = await fetch(`${API_BASE_URL}/missions/${missionPk}/pause-sim/`, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    return {
      success: false,
      error: `Pause simulation failed: ${response.status} ${response.statusText}`,
    };
  }

  const data = await response.json();
  return {
    success: true,
    data,
  };
}

/**
 * Reset the mission simulation.
 * 
 * @param missionPk - Mission primary key (UUID)
 * @returns Control response with status
 */
export async function resetSimulation(
  missionPk: string
): Promise<APIResult<SimulationControlResponse>> {
  const response = await fetch(`${API_BASE_URL}/missions/${missionPk}/reset-sim/`, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    return {
      success: false,
      error: `Reset simulation failed: ${response.status} ${response.statusText}`,
    };
  }

  const data = await response.json();
  return {
    success: true,
    data,
  };
}

/**
 * Set simulation speed multiplier.
 * 
 * @param missionPk - Mission primary key (UUID)
 * @param speed - Speed multiplier (0.5, 1.0, 2.0, 5.0, 10.0, 20.0)
 * @returns Speed control response
 */
export async function setSimulationSpeed(
  missionPk: string,
  speed: number
): Promise<APIResult<SpeedControlResponse>> {
  const response = await fetch(`${API_BASE_URL}/missions/${missionPk}/speed-sim/`, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ speed_multiplier: speed }),
  });

  if (!response.ok) {
    return {
      success: false,
      error: `Set speed failed: ${response.status} ${response.statusText}`,
    };
  }

  const data = await response.json();
  return {
    success: true,
    data,
  };
}
