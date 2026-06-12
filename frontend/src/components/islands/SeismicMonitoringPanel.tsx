/**
 * SeismicMonitoringPanel - Ground Acoustic Sensor Dashboard
 * 
 * Displays deployed seismic/acoustic ground sensors and their detections.
 * Used for tapping/knocking detection in collapsed buildings and caves.
 */
import { useState, useEffect } from 'react';

interface SeismicDetection {
  id: string;
  sensor_id: string;
  detected_at_seconds: number;
  timestamp: string;
  location: string;
  type: string;
  confidence: number;
  pattern: string;
  frequency_hz: number;
  human_cue_probability: number;
  classification: string;
  requires_human_review: boolean;
  description: string;
}

interface SeismicSensor {
  sensor_id: string;
  state: string;
  location: string;
  sector_id: string;
  position: {
    x_m: number;
    y_m: number;
    z_m: number;
  };
  deployed_at_seconds: number;
  background_noise_level: number;
  detection_threshold: number;
  detections: SeismicDetection[];
}

interface SeismicData {
  sensors: SeismicSensor[];
  detections: SeismicDetection[];
}

interface SeismicMonitoringPanelProps {
  seismicData: SeismicData | null;
}

function getStateColor(state: string): string {
  switch (state) {
    case 'listening': return 'text-green-400';
    case 'noise_contaminated': return 'text-yellow-400';
    case 'signal_detected': return 'text-blue-400';
    case 'triangulation_ready': return 'text-purple-400';
    case 'failed': return 'text-red-400';
    default: return 'text-gray-400';
  }
}

function getStateIcon(state: string): string {
  switch (state) {
    case 'listening': return 'LIVE';
    case 'noise_contaminated': return 'NOISE';
    case 'signal_detected': return 'SIGNAL';
    case 'triangulation_ready': return 'TRI';
    case 'failed': return 'FAIL';
    default: return 'IDLE';
  }
}

function getClassificationColor(classification: string): string {
  if (classification.includes('human')) return 'text-orange-400';
  if (classification.includes('structural')) return 'text-gray-400';
  return 'text-blue-400';
}

export default function SeismicMonitoringPanel({ seismicData: initialData }: SeismicMonitoringPanelProps) {
  const [seismicData, setSeismicData] = useState<SeismicData | null>(initialData);
  const [expandedSensorId, setExpandedSensorId] = useState<string | null>(null);

  // Listen for seismic updates
  useEffect(() => {
    const handleUpdate = (event: CustomEvent) => {
      if (event.detail?.seismicData) {
        setSeismicData(event.detail.seismicData);
      }
    };
    
    window.addEventListener('seismic-update', handleUpdate as EventListener);
    return () => window.removeEventListener('seismic-update', handleUpdate as EventListener);
  }, []);

  if (!seismicData || seismicData.sensors.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <span className="text-gray-500 text-xs font-semibold tracking-wide">SEIS</span>
          Seismic / Acoustic Ground Monitoring
        </h3>
        <p className="text-gray-400 text-sm">
          No seismic sensors deployed yet.
        </p>
        <button
          disabled
          className="mt-3 bg-gray-600 text-gray-400 font-medium py-2 px-4 rounded cursor-not-allowed"
        >
          Deploy Sensor (Simulation)
        </button>
      </div>
    );
  }

  const activeSensors = seismicData.sensors.filter(s => s.state !== 'failed');
  const failedSensors = seismicData.sensors.filter(s => s.state === 'failed');
  const humanCueDetections = seismicData.detections.filter(d => d.human_cue_probability > 0.6);

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
        <span className="text-green-400 text-xs font-semibold tracking-wide">SEIS</span>
        Seismic / Acoustic Ground Monitoring
      </h3>

      {/* Summary */}
      <div className="mb-4 text-sm text-gray-300">
        <p>
          <span className="font-medium">Deployed Sensors:</span> {activeSensors.length} active
          {failedSensors.length > 0 && <span>, {failedSensors.length} failed</span>}
        </p>
        {humanCueDetections.length > 0 && (
          <p className="text-orange-400 font-medium mt-1">
            {humanCueDetections.length} possible human cue{humanCueDetections.length !== 1 ? 's' : ''} detected
          </p>
        )}
      </div>

      {/* Sensors List */}
      <div className="space-y-3">
        {seismicData.sensors.map((sensor) => (
          <div
            key={sensor.sensor_id}
            className={`bg-gray-700 rounded-lg p-3 border ${
              sensor.state === 'signal_detected' || sensor.state === 'triangulation_ready'
                ? 'border-blue-500'
                : sensor.state === 'failed'
                ? 'border-red-500'
                : 'border-gray-600'
            }`}
          >
            <div
              className="flex items-start justify-between cursor-pointer"
              onClick={() => setExpandedSensorId(
                expandedSensorId === sensor.sensor_id ? null : sensor.sensor_id
              )}
            >
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                  <span className={getStateColor(sensor.state)}>
                    {getStateIcon(sensor.state)}
                  </span>
                  {sensor.sensor_id}
                </h4>
                <p className="text-xs text-gray-300 mt-1">
                  {sensor.location} ({sensor.position.z_m.toFixed(1)}m depth)
                </p>
                <p className={`text-xs mt-1 ${getStateColor(sensor.state)}`}>
                  Status: {sensor.state.replace(/_/g, ' ')}
                </p>
              </div>
              <button className="text-gray-400 hover:text-white">
                {expandedSensorId === sensor.sensor_id ? 'Hide' : 'Show'}
              </button>
            </div>

            {expandedSensorId === sensor.sensor_id && (
              <div className="mt-3 space-y-2 border-t border-gray-600 pt-3">
                {/* Background Noise */}
                <div>
                  <p className="text-xs text-gray-400 mb-1">Background Noise:</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-600 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          sensor.background_noise_level > 0.6 ? 'bg-red-500' :
                          sensor.background_noise_level > 0.4 ? 'bg-yellow-500' :
                          'bg-green-500'
                        }`}
                        style={{ width: `${sensor.background_noise_level * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-300 w-12 text-right">
                      {Math.round(sensor.background_noise_level * 100)}%
                    </span>
                  </div>
                </div>

                {/* Detections */}
                {sensor.detections.length > 0 ? (
                  <div>
                    <p className="text-xs font-semibold text-gray-300 mb-2">
                      Detections:
                    </p>
                    <div className="space-y-2">
                      {sensor.detections.map((detection) => (
                        <div
                          key={detection.id}
                          className={`bg-gray-800 rounded p-2 border ${
                            detection.classification.includes('human')
                              ? 'border-orange-500'
                              : 'border-gray-600'
                          }`}
                        >
                          <p className={`text-xs font-semibold ${getClassificationColor(detection.classification)}`}>
                            {detection.type === 'tapping' && 'TAP '}
                            {detection.classification.replace(/_/g, ' ').toUpperCase()}
                          </p>
                          <p className="text-xs text-gray-300 mt-1">
                            {detection.pattern}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {detection.timestamp} / Confidence: {Math.round(detection.confidence * 100)}%
                          </p>
                          {detection.human_cue_probability > 0.6 && (
                            <p className="text-xs text-orange-400 font-medium mt-1">
                              Human cue probability: {Math.round(detection.human_cue_probability * 100)}%
                            </p>
                          )}
                          {detection.requires_human_review && (
                            <p className="text-xs text-yellow-400 font-medium mt-1">
                              Human review required
                            </p>
                          )}
                          <button className="text-xs text-blue-400 hover:text-blue-300 mt-1">
                            [View Waveform]
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
      {seismicData.sensors.length > 0 && seismicData.sensors.length < 3 && (
        <div className="mt-4 bg-blue-900 bg-opacity-20 border border-blue-700 rounded p-3">
          <p className="text-xs text-blue-200">
            <strong>Recommendation:</strong> Deploy additional sensor for triangulation and false-positive reduction.
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-4 flex gap-2">
        <button
          disabled
          className="flex-1 bg-gray-600 text-gray-400 font-medium py-2 px-3 rounded cursor-not-allowed text-sm"
        >
          Request Quiet Period
        </button>
        <button
          disabled
          className="flex-1 bg-gray-600 text-gray-400 font-medium py-2 px-3 rounded cursor-not-allowed text-sm"
        >
          Deploy Sensor (Simulation)
        </button>
      </div>

      {/* Safety Note */}
      <div className="mt-3 bg-yellow-900 bg-opacity-20 border border-yellow-700 rounded p-2">
        <p className="text-xs text-yellow-200">
          Simulation only. All human cue detections require operator verification and search/rescue coordination.
        </p>
      </div>
    </div>
  );
}
