/**
 * Demo data model for RescueMesh mission simulations
 * 
 * TODO: These types will be replaced by Django API response shapes
 * when backend integration is implemented.
 */

export interface UseCaseDemoProfile {
  slug: string;
  title: string;
  priority: string;
  missionId: string;
  status: 'Simulated' | 'Planned' | 'Active' | 'Completed';

  missionObjective: string;

  terrain: {
    type: string;
    gps: string;
    communications: string;
    lighting: string;
    hazards: string[];
  };

  agents: DemoAgent[];

  expectedFailures: DemoFailure[];

  expectedOutputs: DemoOutput[];

  simulation: {
    mapType: 'void-map' | 'cave-map' | 'flood-map' | 'industrial-map';
    environmentTags: string[];
    defaultConfidence: number;
    communicationRisk: 'low' | 'medium' | 'high' | 'severe';
    batteryRisk: 'low' | 'medium' | 'high';
    sensorRisk: 'low' | 'medium' | 'high';
    missionDurationMinutes: number;
  };

  timeline: DemoTimelineEvent[];

  aiAnalyst: {
    role: string;
    promptSummary: string;
    expectedFindings: string[];
    humanReviewRequired: boolean;
  };
}

export interface DemoAgent {
  id: string;
  name: string;
  role: string;
  description: string;
  state:
    | 'healthy'
    | 'degraded'
    | 'intermittent'
    | 'failed'
    | 'landed_relay'
    | 'abandoned'
    | 'sacrificed'
    | 'nfc_readable'
    | 'black_box_recovered';
  batteryPercent: number;
  locationLabel: string;
  capabilities: string[];
  sensors: string[];
  nfcRecoveryAvailable?: boolean;
}

export interface DemoFailure {
  name: string;
  affectedComponent: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  dashboardEffect: string;
}

export interface DemoOutput {
  name: string;
  outputType:
    | '3d-map'
    | 'thermal'
    | 'audio'
    | 'environmental'
    | 'device-scan'
    | 'relay-map'
    | 'ai-analysis'
    | 'report';
  description: string;
  confidenceRequired: boolean;
}

export interface DemoTimelineEvent {
  time: string;
  title: string;
  description: string;
  assetId?: string;
  eventType:
    | 'mission-start'
    | 'mapping'
    | 'relay'
    | 'sensor-detection'
    | 'failure'
    | 'ai-analysis'
    | 'operator-review'
    | 'mission-end';
  confidence?: number;
}
