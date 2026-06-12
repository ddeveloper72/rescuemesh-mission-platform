/**
 * HydrophonePanel - Water / Hydrophone Acoustic Monitoring
 * 
 * Displays underwater acoustic sensors and water sound detections.
 * Used for flooded structures, underground rivers, and submerged operations.
 */
import { useState, useEffect } from 'react';

interface HydrophoneDetection {
  id: string;
  sensor_id: string;
  detected_at_seconds: number;
  timestamp: string;
  location: string;
  detection_type: string;
  confidence: number;
  frequency_range: string;
  flow_direction?: string;
  intensity: string;
  classification: string;
  description: string;
}

interface Hydrophone {
  sensor_id: string;
  state: string;
  location: string;
  sector_id: string;
  position: {
    x_m: number;
    y_m: number;
    z_m: number;
  };
  water_depth_m: number;
  deployed_at_seconds: number;
  turbulence_level: number;
  detections: HydrophoneDetection[];
}

interface HydrophoneData {
  hydrophones: Hydrophone[];
  detections: HydrophoneDetection[];
}

interface HydrophonePanelProps {
  hydrophoneData: HydrophoneData | null;
}

function getStateColor(state: string): string {
  switch (state) {
    case 'deployed_surface': return 'text-blue-400';
    case 'deployed_submerged': return 'text-cyan-400';
    case 'listening': return 'text-green-400';
    case 'turbulence_contaminated': return 'text-yellow-400';
    case 'signal_detected': return 'text-purple-400';
    case 'failed': return 'text-red-400';
    default: return 'text-gray-400';
  }
}

function getDetectionIcon(detectionType: string): string {
  switch (detectionType) {
    case 'underground_river': return 'FLOW';
    case 'mechanical_pump': return 'PUMP';
    case 'underwater_knock': return 'KNOCK';
    case 'underwater_tapping': return 'TAP';
    case 'leak': return 'LEAK';
    case 'cavitation': return 'CAV';
    default: return 'AUDIO';
  }
}

function getClassificationColor(classification: string): string {
  if (classification.includes('human') || classification.includes('knock') || classification.includes('tapping')) {
    return 'text-orange-400';
  }
  if (classification.includes('mechanical') || classification.includes('pump')) {
    return 'text-blue-400';
  }
  if (classification.includes('natural')) {
    return 'text-cyan-400';
  }
  return 'text-gray-400';
}

export default function HydrophonePanel({ hydrophoneData: initialData }: HydrophonePanelProps) {
  const [hydrophoneData, setHydrophoneData] = useState<HydrophoneData | null>(initialData);
  const [expandedHydrophoneId, setExpandedHydrophoneId] = useState<string | null>(null);

  // Listen for hydrophone updates
  useEffect(() => {
    const handleUpdate = (event: CustomEvent) => {
      if (event.detail?.hydrophoneData) {
        setHydrophoneData(event.detail.hydrophoneData);
      }
    };
    
    window.addEventListener('hydrophone-update', handleUpdate as EventListener);
    return () => window.removeEventListener('hydrophone-update', handleUpdate as EventListener);
  }, []);

  if (!hydrophoneData || hydrophoneData.hydrophones.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <span className="text-gray-500 text-xs font-semibold tracking-wide">HYDRO</span>
          Water / Hydrophone Acoustic Monitoring
        </h3>
        <p className="text-gray-400 text-sm">
          No hydrophones deployed yet.
        </p>
        <button
          disabled
          className="mt-3 bg-gray-600 text-gray-400 font-medium py-2 px-4 rounded cursor-not-allowed"
        >
          Deploy Hydrophone (Simulation)
        </button>
      </div>
    );
  }

  const activeHydrophones = hydrophoneData.hydrophones.filter(h => h.state !== 'failed');
  const failedHydrophones = hydrophoneData.hydrophones.filter(h => h.state === 'failed');
  const survivorCueDetections = hydrophoneData.detections.filter(d => 
    d.detection_type.includes('knock') || d.detection_type.includes('tapping')
  );

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
        <span className="text-cyan-400 text-xs font-semibold tracking-wide">HYDRO</span>
        Water / Hydrophone Acoustic Monitoring
      </h3>

      {/* Summary */}
      <div className="mb-4 text-sm text-gray-300">
        <p>
          <span className="font-medium">Deployed Hydrophones:</span> {activeHydrophones.length} active
          {failedHydrophones.length > 0 && <span>, {failedHydrophones.length} failed</span>}
        </p>
        {survivorCueDetections.length > 0 && (
          <p className="text-orange-400 font-medium mt-1">
            {survivorCueDetections.length} possible underwater signal{survivorCueDetections.length !== 1 ? 's' : ''} detected
          </p>
        )}
      </div>

      {/* Hydrophones List */}
      <div className="space-y-3">
        {hydrophoneData.hydrophones.map((hydrophone) => (
          <div
            key={hydrophone.sensor_id}
            className={`bg-gray-700 rounded-lg p-3 border ${
              hydrophone.state === 'signal_detected'
                ? 'border-cyan-500'
                : hydrophone.state === 'failed'
                ? 'border-red-500'
                : 'border-gray-600'
            }`}
          >
            <div
              className="flex items-start justify-between cursor-pointer"
              onClick={() => setExpandedHydrophoneId(
                expandedHydrophoneId === hydrophone.sensor_id ? null : hydrophone.sensor_id
              )}
            >
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                  <span className={`inline-block h-2 w-2 rounded-full ${getStateColor(hydrophone.state).replace('text-', 'bg-')}`} aria-hidden="true"></span>
                  {hydrophone.sensor_id}
                </h4>
                <p className="text-xs text-gray-300 mt-1">
                  {hydrophone.location} ({hydrophone.position.z_m.toFixed(1)}m depth)
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  Water Depth: {hydrophone.water_depth_m.toFixed(1)}m
                </p>
                <p className={`text-xs mt-1 ${getStateColor(hydrophone.state)}`}>
                  Status: {hydrophone.state.replace(/_/g, ' ')}
                </p>
              </div>
              <button className="text-gray-400 hover:text-white">
                {expandedHydrophoneId === hydrophone.sensor_id ? 'Hide' : 'Show'}
              </button>
            </div>

            {expandedHydrophoneId === hydrophone.sensor_id && (
              <div className="mt-3 space-y-2 border-t border-gray-600 pt-3">
                {/* Turbulence Level */}
                <div>
                  <p className="text-xs text-gray-400 mb-1">Turbulence:</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-600 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          hydrophone.turbulence_level > 0.6 ? 'bg-red-500' :
                          hydrophone.turbulence_level > 0.4 ? 'bg-yellow-500' :
                          'bg-green-500'
                        }`}
                        style={{ width: `${hydrophone.turbulence_level * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-300 w-12 text-right">
                      {Math.round(hydrophone.turbulence_level * 100)}%
                    </span>
                  </div>
                </div>

                {/* Detections */}
                {hydrophone.detections.length > 0 ? (
                  <div>
                    <p className="text-xs font-semibold text-gray-300 mb-2">
                      Detections:
                    </p>
                    <div className="space-y-2">
                      {hydrophone.detections.map((detection) => (
                        <div
                          key={detection.id}
                          className={`bg-gray-800 rounded p-2 border ${
                            detection.detection_type.includes('knock') || detection.detection_type.includes('tapping')
                              ? 'border-orange-500'
                              : 'border-cyan-600'
                          }`}
                        >
                          <p className={`text-xs font-semibold ${getClassificationColor(detection.classification)}`}>
                            {getDetectionIcon(detection.detection_type)}{' '}
                            {detection.detection_type.replace(/_/g, ' ').toUpperCase()}
                          </p>
                          <p className="text-xs text-gray-300 mt-1">
                            {detection.description}
                          </p>
                          <div className="mt-1 space-y-1">
                            <p className="text-xs text-gray-400">
                              {detection.timestamp} / Confidence: {Math.round(detection.confidence * 100)}%
                            </p>
                            <p className="text-xs text-gray-400">
                              Frequency: {detection.frequency_range}
                            </p>
                            {detection.flow_direction && (
                              <p className="text-xs text-gray-400">
                                Flow Direction: {detection.flow_direction}
                              </p>
                            )}
                            <p className="text-xs text-gray-400">
                              Intensity: {detection.intensity}
                            </p>
                          </div>
                          {(detection.detection_type.includes('knock') || detection.detection_type.includes('tapping')) && (
                            <p className="text-xs text-orange-400 font-medium mt-1">
                              Possible survivor signal - Human review required
                            </p>
                          )}
                          <button className="text-xs text-cyan-400 hover:text-cyan-300 mt-1">
                            [View Spectrogram]
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-gray-400 italic">
                    No detections yet
                  </p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Recommendations */}
      {hydrophoneData.hydrophones.some(h => h.detections.length > 0) && (
        <div className="mt-4 bg-cyan-900 bg-opacity-20 border border-cyan-700 rounded p-3">
          <p className="text-xs text-cyan-200">
            <strong>Recommendation:</strong> Continue monitoring for underwater tapping or knocking patterns.
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-4 flex gap-2">
        <button
          disabled
          className="flex-1 bg-gray-600 text-gray-400 font-medium py-2 px-3 rounded cursor-not-allowed text-sm"
        >
          Deploy Hydrophone (Simulation)
        </button>
        <button
          disabled
          className="flex-1 bg-gray-600 text-gray-400 font-medium py-2 px-3 rounded cursor-not-allowed text-sm"
        >
          Request Analysis
        </button>
      </div>

      {/* Safety Note */}
      <div className="mt-3 bg-yellow-900 bg-opacity-20 border border-yellow-700 rounded p-2">
        <p className="text-xs text-yellow-200">
          Simulation only. All underwater signal detections require operator verification and dive team coordination.
        </p>
      </div>
    </div>
  );
}
