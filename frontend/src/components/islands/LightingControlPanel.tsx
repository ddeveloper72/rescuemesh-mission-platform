/**
 * LightingControlPanel - Visual Mode & Illumination Controls
 * 
 * Displays current lighting mode (low-light RGB, IR, thermal, visible spotlight)
 * and allows operator to view lighting state, battery cost, and image confidence.
 */
import { useState, useEffect } from 'react';

interface LightingState {
  agent_id: string;
  current_mode: string;
  previous_mode: string;
  light_active: boolean;
  light_intensity_percent: number;
  battery_cost_percent_per_second: number;
  image_confidence: number;
  confidence_penalty_factors: {
    dust?: number;
    smoke?: number;
    moisture?: number;
    reflection_glare?: number;
  };
  changed_at_seconds: number;
  reason: string;
}

interface LightingControlPanelProps {
  lightingStates: Record<string, LightingState> | null;
  agents?: Array<{agent_id: string; name: string}>;
}

function getModeIcon(mode: string): string {
  switch (mode) {
    case 'low_light_rgb': return '🌙';
    case 'ir_assisted': return '🔦';
    case 'thermal': return '🔥';
    case 'visible_spotlight': return '💡';
    case 'ir_only': return '👁️';
    default: return '📷';
  }
}

function getModeColor(mode: string): string {
  switch (mode) {
    case 'low_light_rgb': return 'text-blue-300';
    case 'ir_assisted': return 'text-purple-300';
    case 'thermal': return 'text-orange-400';
    case 'visible_spotlight': return 'text-yellow-300';
    case 'ir_only': return 'text-purple-400';
    default: return 'text-gray-400';
  }
}

function getModeName(mode: string): string {
  switch (mode) {
    case 'low_light_rgb': return 'Low-Light RGB';
    case 'ir_assisted': return 'IR-Assisted';
    case 'thermal': return 'Thermal';
    case 'visible_spotlight': return 'Visible Spotlight';
    case 'ir_only': return 'IR Only';
    default: return mode;
  }
}

function getPenaltyName(key: string): string {
  switch (key) {
    case 'dust': return 'Dust';
    case 'smoke': return 'Smoke';
    case 'moisture': return 'Moisture';
    case 'reflection_glare': return 'Reflection/Glare';
    default: return key;
  }
}

export default function LightingControlPanel({ lightingStates: initialStates, agents = [] }: LightingControlPanelProps) {
  const [lightingStates, setLightingStates] = useState<Record<string, LightingState> | null>(initialStates);
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

  // Listen for lighting updates
  useEffect(() => {
    const handleUpdate = (event: CustomEvent) => {
      if (event.detail?.lightingStates) {
        setLightingStates(event.detail.lightingStates);
      }
    };
    
    window.addEventListener('lighting-update', handleUpdate as EventListener);
    return () => window.removeEventListener('lighting-update', handleUpdate as EventListener);
  }, []);

  // Auto-select first agent with lighting state
  if (!selectedAgentId && lightingStates) {
    const firstAgentId = Object.keys(lightingStates)[0];
    if (firstAgentId) {
      setSelectedAgentId(firstAgentId);
    }
  }

  if (!lightingStates || Object.keys(lightingStates).length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <span className="text-gray-500">📷</span>
          Lighting & Visual Mode
        </h3>
        <p className="text-gray-400 text-sm">
          No lighting data available.
        </p>
      </div>
    );
  }

  const agentIds = Object.keys(lightingStates);
  const currentState = selectedAgentId ? lightingStates[selectedAgentId] : null;
  const agentName = agents.find(a => a.agent_id === selectedAgentId)?.name || selectedAgentId;

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
        <span className="text-yellow-400">📷</span>
        Lighting & Visual Mode
      </h3>

      {/* Agent Selection */}
      {agentIds.length > 1 && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Select Agent
          </label>
          <select
            value={selectedAgentId || ''}
            onChange={(e) => setSelectedAgentId(e.target.value)}
            className="w-full bg-gray-700 text-white border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-500"
          >
            {agentIds.map(agentId => {
              const name = agents.find(a => a.agent_id === agentId)?.name || agentId;
              return (
                <option key={agentId} value={agentId}>
                  {name}
                </option>
              );
            })}
          </select>
        </div>
      )}

      {currentState && (
        <>
          {/* Current Mode */}
          <div className="bg-gray-700 rounded-lg p-3 mb-3">
            <p className="text-xs text-gray-400 mb-2">Current Mode</p>
            <div className="flex items-center gap-2">
              <span className={`text-2xl ${getModeColor(currentState.current_mode)}`}>
                {getModeIcon(currentState.current_mode)}
              </span>
              <div className="flex-1">
                <p className={`text-base font-semibold ${getModeColor(currentState.current_mode)}`}>
                  {getModeName(currentState.current_mode)}
                </p>
                {currentState.previous_mode !== currentState.current_mode && (
                  <p className="text-xs text-gray-400">
                    (switched from {getModeName(currentState.previous_mode)})
                  </p>
                )}
              </div>
            </div>

            {/* Reason */}
            {currentState.reason && (
              <p className="text-xs text-gray-400 mt-2 italic">
                Reason: {currentState.reason.replace(/_/g, ' ')}
              </p>
            )}
          </div>

          {/* Light Status */}
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div className="bg-gray-700 rounded p-2">
              <p className="text-xs text-gray-400 mb-1">Light Status</p>
              <p className={`text-sm font-semibold ${
                currentState.light_active ? 'text-yellow-400' : 'text-gray-400'
              }`}>
                {currentState.light_active ? '● ON' : '○ OFF'}
              </p>
              {currentState.light_active && currentState.light_intensity_percent > 0 && (
                <p className="text-xs text-gray-400 mt-1">
                  Intensity: {currentState.light_intensity_percent}%
                </p>
              )}
            </div>

            <div className="bg-gray-700 rounded p-2">
              <p className="text-xs text-gray-400 mb-1">Battery Cost</p>
              <p className="text-sm font-semibold text-white">
                {currentState.battery_cost_percent_per_second.toFixed(3)}%/sec
              </p>
              {currentState.battery_cost_percent_per_second > 0.05 && (
                <p className="text-xs text-orange-400 mt-1">
                  ⚠ High drain
                </p>
              )}
            </div>
          </div>

          {/* Image Confidence */}
          <div className="mb-3">
            <p className="text-xs text-gray-400 mb-2">Image Confidence</p>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-gray-600 rounded-full h-3">
                <div
                  className={`h-3 rounded-full ${
                    currentState.image_confidence > 0.7 ? 'bg-green-500' :
                    currentState.image_confidence > 0.4 ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${currentState.image_confidence * 100}%` }}
                />
              </div>
              <span className="text-sm font-semibold text-white w-12 text-right">
                {Math.round(currentState.image_confidence * 100)}%
              </span>
            </div>
          </div>

          {/* Confidence Penalties */}
          {Object.keys(currentState.confidence_penalty_factors).length > 0 && (
            <div className="bg-orange-900 bg-opacity-20 border border-orange-700 rounded p-3 mb-3">
              <p className="text-xs font-semibold text-orange-200 mb-2">
                Confidence Penalties:
              </p>
              <div className="space-y-1">
                {Object.entries(currentState.confidence_penalty_factors).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-xs">
                    <span className="text-orange-200">{getPenaltyName(key)}</span>
                    <span className="text-orange-400 font-medium">
                      -{Math.round((value as number) * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Mode Controls (Simulation) */}
          <div className="grid grid-cols-2 gap-2">
            <button
              disabled
              className="bg-gray-600 text-gray-400 font-medium py-2 px-3 rounded cursor-not-allowed text-sm"
            >
              {currentState.light_active ? 'Light Off' : 'Light On'}
            </button>
            <button
              disabled
              className="bg-gray-600 text-gray-400 font-medium py-2 px-3 rounded cursor-not-allowed text-sm"
            >
              IR Mode
            </button>
            <button
              disabled
              className="bg-gray-600 text-gray-400 font-medium py-2 px-3 rounded cursor-not-allowed text-sm"
            >
              Thermal
            </button>
            <button
              disabled
              className="bg-gray-600 text-gray-400 font-medium py-2 px-3 rounded cursor-not-allowed text-sm"
            >
              Visible
            </button>
          </div>

          <div className="mt-2 flex gap-2">
            <button
              disabled
              className="flex-1 bg-gray-600 text-gray-400 font-medium py-2 px-3 rounded cursor-not-allowed text-sm"
            >
              Capture Still
            </button>
            <button
              disabled
              className="flex-1 bg-gray-600 text-gray-400 font-medium py-2 px-3 rounded cursor-not-allowed text-sm"
            >
              Strobe Beacon
            </button>
          </div>

          {/* Safety Note */}
          <div className="mt-3 bg-blue-900 bg-opacity-20 border border-blue-700 rounded p-2">
            <p className="text-xs text-blue-200">
              💡 Simulation only. Lighting controls would require authorized operator command in real deployment.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
