/**
 * RescueMesh Django API Client
 * 
 * Provides typed fetch helpers with graceful error handling.
 * Falls back to local data if Django API is unavailable.
 */

// API base URL from environment or default to local development
const API_BASE_URL = import.meta.env.PUBLIC_DJANGO_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

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
