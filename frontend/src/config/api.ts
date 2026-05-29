/**
 * API configuration for RescueMesh backend
 */

// API base URL - default to local development server
export const API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

/**
 * API endpoints
 */
export const API_ENDPOINTS = {
  useCases: {
    list: () => `${API_BASE_URL}/api/v1/usecases/`,
    detail: (slug: string) => `${API_BASE_URL}/api/v1/usecases/${slug}/`,
    demoProfile: (slug: string) => `${API_BASE_URL}/api/v1/usecases/${slug}/demo_profile/`,
  },
  sensors: {
    list: () => `${API_BASE_URL}/api/v1/sensors/`,
  },
  failures: {
    list: () => `${API_BASE_URL}/api/v1/failures/`,
  },
  outputs: {
    list: () => `${API_BASE_URL}/api/v1/outputs/outputs/`,
  },
  prompts: {
    list: () => `${API_BASE_URL}/api/v1/prompts/`,
  },
  missions: {
    list: () => `${API_BASE_URL}/api/v1/missions/`,
  },
  agents: {
    list: () => `${API_BASE_URL}/api/v1/agents/`,
  },
};

/**
 * Fetch with error handling
 */
export async function fetchAPI<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }
  return response.json();
}
