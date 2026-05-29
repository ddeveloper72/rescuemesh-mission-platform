/**
 * Use case data model for RescueMesh mission profiles
 */

export interface UseCaseProfile {
  slug: string;
  title: string;
  priority: string;
  missionObjective: string;
  terrainCharacteristics: {
    type: string;
    gps: string;
    communications: string;
    lighting: string;
    hazards: string[];
  };
  recommendedAgents: RecommendedAgent[];
  expectedFailures: ExpectedFailure[];
  expectedOutputs: ExpectedOutput[];
}

export interface RecommendedAgent {
  name: string;
  role: string;
  description: string;
  capabilities: string[];
}

export interface ExpectedFailure {
  name: string;
  description: string;
}

export interface ExpectedOutput {
  name: string;
  description: string;
}
