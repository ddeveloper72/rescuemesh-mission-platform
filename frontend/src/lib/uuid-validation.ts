/**
 * UUID Validation Utilities
 * 
 * Prevents stale UUID issues by validating mission identifiers before API calls.
 */

const UUID_V4_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export interface UUIDValidationResult {
  valid: boolean;
  normalized?: string;
  error?: string;
  suggestions?: string[];
}

/**
 * Validate UUID format.
 */
export function isValidUUID(uuid: string): boolean {
  if (!uuid || typeof uuid !== 'string') {
    return false;
  }
  
  return UUID_V4_REGEX.test(uuid.toLowerCase());
}

/**
 * Validate and normalize a mission UUID.
 */
export function validateMissionUUID(uuid: string): UUIDValidationResult {
  if (!uuid) {
    return {
      valid: false,
      error: 'Mission UUID is required',
      suggestions: ['Check that data-mission-pk attribute is set in the HTML']
    };
  }
  
  if (typeof uuid !== 'string') {
    return {
      valid: false,
      error: 'Mission UUID must be a string',
    };
  }
  
  const normalized = uuid.toLowerCase().trim();
  
  if (!UUID_V4_REGEX.test(normalized)) {
    return {
      valid: false,
      error: `Invalid UUID format: "${uuid}"`,
      suggestions: [
        'Expected format: xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx',
        'This may indicate a stale UUID from a previous database',
        'Try rebuilding frontend: docker compose build --no-cache frontend',
        'Or check available UUIDs: GET /api/v1/missions/health/'
      ]
    };
  }
  
  return {
    valid: true,
    normalized
  };
}

/**
 * Validate mission UUID and throw error if invalid.
 * Use this before making API calls.
 */
export function assertValidMissionUUID(uuid: string): string {
  const result = validateMissionUUID(uuid);
  
  if (!result.valid) {
    const errorMessage = [
      result.error,
      ...(result.suggestions || [])
    ].join('\n  - ');
    
    throw new Error(`UUID Validation Failed:\n${errorMessage}`);
  }
  
  return result.normalized!;
}

/**
 * Check if a 404 error might be due to UUID mismatch.
 */
export function isUUIDMismatchError(error: any, uuid: string): boolean {
  if (!error) return false;
  
  // Check if it's a 404 error
  const is404 = 
    error.status === 404 ||
    error.response?.status === 404 ||
    error.message?.includes('404') ||
    error.message?.includes('not found');
  
  if (!is404) return false;
  
  // If UUID is valid format but still 404, likely database mismatch
  return isValidUUID(uuid);
}

/**
 * Get helpful error message for UUID mismatch.
 */
export function getUUIDMismatchGuidance(uuid: string): string {
  return `
Mission UUID not found: ${uuid}

This usually means the database was recreated but the frontend still has old UUIDs.

To fix:
1. Rebuild frontend: docker compose build --no-cache frontend
2. Restart frontend: docker compose up -d frontend
3. Or check available missions: http://localhost:8000/api/v1/missions/health/

The UUID format is valid, but the mission doesn't exist in the current database.
`.trim();
}

/**
 * Development mode: Check for hardcoded UUIDs and warn.
 */
export function warnIfHardcodedUUID(uuid: string, source: string): void {
  if (import.meta.env.DEV && isValidUUID(uuid)) {
    // Check if this looks like a hardcoded UUID (not fetched from API)
    if (source === 'hardcoded' || source.startsWith('data-')) {
      console.warn(
        `⚠️ Potentially stale UUID detected from ${source}: ${uuid}\n` +
        `Consider fetching UUIDs dynamically from: /api/v1/missions/health/`
      );
    }
  }
}
