/**
 * Build-time Mission UUID Validator
 * 
 * This script runs during Astro build to verify that missions exist before
 * embedding their UUIDs in static HTML.
 * 
 * Prevents:
 * - Deploying pages with stale UUIDs
 * - 404 errors in production
 * - Confusion from database/frontend mismatches
 * 
 * Usage in Astro pages:
 * ```typescript
 * import { validateMissionForBuild } from '../../../lib/build-uuid-validator';
 * const missionData = await validateMissionForBuild('collapsed-building-search');
 * ```
 */

import { getApiBaseUrl } from './api';

export interface BuildValidationResult {
  valid: boolean;
  missionPk?: string;
  missionName?: string;
  scenario?: string;
  error?: string;
  suggestions?: string[];
}

/**
 * Fetch health check data from backend to get available missions.
 */
async function fetchAvailableMissions(): Promise<any[]> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/missions/health/`;
  
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.missions || [];
  } catch (error) {
    console.error('[Build Validator] Failed to fetch health check:', error);
    throw new Error(
      `Cannot validate missions at build time. Backend may not be running.\n` +
      `Expected: ${url}\n` +
      `Error: ${error instanceof Error ? error.message : String(error)}`
    );
  }
}

/**
 * Validate that a mission exists during build time.
 * 
 * @param scenarioSlug - Scenario slug to match (e.g., 'collapsed-building-search')
 * @returns Mission data if found
 * @throws Error if mission not found or backend unreachable
 */
export async function validateMissionForBuild(
  scenarioSlug: string
): Promise<BuildValidationResult> {
  
  try {
    const missions = await fetchAvailableMissions();
    
    // Find mission matching scenario slug
    const mission = missions.find(m => m.scenario === scenarioSlug);
    
    if (!mission) {
      return {
        valid: false,
        error: `No mission found for scenario: ${scenarioSlug}`,
        suggestions: [
          'Run backend seeding: docker exec rescuemesh_backend python manage.py seed_scenarios',
          'Check available scenarios in backend',
          `Available missions: ${missions.map(m => m.scenario).join(', ')}`
        ]
      };
    }
    
    console.log(`[Build Validator] ✅ Found mission for ${scenarioSlug}: ${mission.uuid}`);
    
    return {
      valid: true,
      missionPk: mission.uuid,
      missionName: mission.name,
      scenario: mission.scenario
    };
    
  } catch (error) {
    return {
      valid: false,
      error: error instanceof Error ? error.message : String(error),
      suggestions: [
        'Ensure backend is running: docker compose up -d backend',
        'Verify backend is accessible at http://backend:8000 (SSR) or http://localhost:8000 (client)',
        'Check docker-compose.yml network configuration'
      ]
    };
  }
}

/**
 * Strict validation that throws on failure.
 * Use this in Astro pages to prevent building with stale UUIDs.
 */
export async function requireMissionForBuild(scenarioSlug: string): Promise<{
  missionPk: string;
  missionName: string;
  scenario: string;
}> {
  const result = await validateMissionForBuild(scenarioSlug);
  
  if (!result.valid || !result.missionPk) {
    const errorMessage = [
      '❌ Build-time validation failed!',
      '',
      result.error || 'Unknown error',
      '',
      ...(result.suggestions || []).map(s => `  - ${s}`)
    ].join('\n');
    
    throw new Error(errorMessage);
  }
  
  return {
    missionPk: result.missionPk,
    missionName: result.missionName || '',
    scenario: result.scenario || scenarioSlug
  };
}

/**
 * Lenient validation that warns but doesn't fail build.
 * Use this for non-critical scenarios or development.
 */
export async function validateMissionForBuildSoft(scenarioSlug: string): Promise<{
  missionPk: string;
  missionName?: string;
}> {
  const result = await validateMissionForBuild(scenarioSlug);
  
  if (!result.valid) {
    console.warn('[Build Validator] ⚠️ Validation failed (continuing anyway)');
    console.warn(result.error);
    if (result.suggestions) {
      result.suggestions.forEach(s => console.warn(`  - ${s}`));
    }
    
    // Return a placeholder UUID (will cause runtime 404, but build succeeds)
    return {
      missionPk: `00000000-0000-4000-0000-${scenarioSlug.slice(0, 12).padEnd(12, '0')}`,
      missionName: `[Placeholder for ${scenarioSlug}]`
    };
  }
  
  return {
    missionPk: result.missionPk!,
    missionName: result.missionName
  };
}
