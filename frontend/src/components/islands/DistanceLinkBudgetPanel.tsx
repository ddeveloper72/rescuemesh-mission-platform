/**
 * Distance & Link Budget Panel
 * 
 * Displays navigation intelligence for GPS-denied environments.
 * Shows distance, bearing, elevation, and communication metrics
 * for agents and detections in 3D mission space.
 */

import { useEffect, useState } from 'react';

interface NavigationData {
  distance_from_origin_m?: number;
  straight_line_3d_distance_from_origin_m?: number;
  bearing_from_origin_deg?: number | null;
  bearing_from_origin_cardinal?: string | null;
  heading_deg?: number | null;
  elevation_m?: number;
  depth_m?: number;
  vertical_offset_from_origin_m?: number;
  vertical_profile_label?: string;
  depth_elevation_label?: string;
  estimated_return_route_distance_m?: number;
  estimated_return_time_seconds?: number;
  nearest_relay?: {
    relay_id: string;
    relay_name: string;
    distance_m: number;
    bearing_deg: number;
    bearing_cardinal: string;
  };
  contact_path_length_m?: number;
  route_distance_from_origin_m?: number;
  comms_risk?: string;
}

interface Agent {
  agent_id: string;
  name: string;
  role: string;
  state: string;
  battery_percent: number;
  signal_strength: number;
  location_label: string;
  navigation?: NavigationData;
}

interface AudioDetection {
  id: string;
  agent_name: string;
  audio_type: string;
  location_label: string;
  confidence: number;
  signal_quality: number;
  navigation?: NavigationData;
}

interface NavigationModel {
  coordinate_system: string;
  origin_label: string;
  north_reference: string;
  bearing_reference: string;
  bearing_confidence: number;
  bearing_reliability: string;
  bearing_reliability_reason: string;
}

interface MissionSimulationState {
  navigation_model?: NavigationModel;
  agents: Agent[];
  audio_detections?: AudioDetection[];
}

export default function DistanceLinkBudgetPanel() {
  const [agentsData, setAgentsData] = useState<Agent[]>([]);
  const [detectionsData, setDetectionsData] = useState<AudioDetection[]>([]);
  const [navigationModel, setNavigationModel] = useState<NavigationModel | null>(null);

  useEffect(() => {
    const handleUpdate = (event: CustomEvent<MissionSimulationState>) => {
      const state = event.detail;
      setAgentsData(state.agents || []);
      setDetectionsData(state.audio_detections || []);
      setNavigationModel(state.navigation_model || null);
    };

    // Listen for updates from simulation manager
    window.addEventListener('audio-detections-update', handleUpdate as EventListener);

    return () => {
      window.removeEventListener('audio-detections-update', handleUpdate as EventListener);
    };
  }, []);

  // Filter agents with navigation data (exclude base relay unless it has interesting data)
  // Changed to show all agents, not just those with navigation
  const activeAgents = agentsData.filter(
    (agent) => agent.agent_id !== 'relay-1' && agent.state !== 'failed' && agent.state !== 'sacrificed'
  );

  // Get critical detections (high confidence or high risk)
  const criticalDetections = detectionsData.filter(
    (detection) =>
      detection.confidence > 60 ||
      (detection.navigation && detection.navigation.comms_risk === 'high')
  );

  return (
    <div className="bg-slate-800 rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Distance & Link Budget</h2>
        {navigationModel && (
          <div className="text-xs text-slate-400">
            {navigationModel.north_reference} / {navigationModel.bearing_reference}
          </div>
        )}
      </div>

      {navigationModel && navigationModel.bearing_reliability !== 'good' && (
        <div className="bg-yellow-900/30 border border-yellow-700 rounded px-3 py-2">
          <div className="text-xs font-medium text-yellow-300">
            Compass Reliability: {navigationModel.bearing_reliability}
          </div>
          <div className="text-xs text-yellow-400 mt-1">
            {navigationModel.bearing_reliability_reason}
          </div>
        </div>
      )}

      {/* Active Agents */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-slate-300 uppercase tracking-wide">
          Active Agents
        </h3>

        {activeAgents.length === 0 && (
          <div className="text-sm text-slate-500 italic">No agents deployed yet</div>
        )}

        {activeAgents.map((agent) => {
          const nav = agent.navigation;

          return (
            <div
              key={agent.agent_id}
              className="bg-slate-700/50 rounded-lg p-3 border border-slate-600"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <div className="font-medium text-white">{agent.name}</div>
                  <div className="text-xs text-slate-400">{agent.location_label}</div>
                </div>
                <div
                  className={`text-xs px-2 py-1 rounded ${
                    agent.state === 'healthy'
                      ? 'bg-green-900/30 text-green-300'
                      : agent.state === 'degraded'
                      ? 'bg-yellow-900/30 text-yellow-300'
                      : 'bg-red-900/30 text-red-300'
                  }`}
                >
                  {agent.state}
                </div>
              </div>

              {!nav ? (
                <div className="text-xs text-slate-400 italic">Navigation data pending...</div>
              ) : (
                <>
                  <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                    {/* Distance & Bearing */}
                    <div>
                      <div className="text-xs text-slate-400">From Base</div>
                      <div className="text-white font-mono">
                        {(nav.distance_from_origin_m || nav.straight_line_3d_distance_from_origin_m || 0).toFixed(1)} m
                      </div>
                    </div>

                    {(nav.bearing_from_origin_deg !== null && nav.bearing_from_origin_deg !== undefined) && (
                      <div>
                        <div className="text-xs text-slate-400">Bearing</div>
                        <div className="text-white font-mono">
                          {nav.bearing_from_origin_deg?.toFixed(0)} deg {nav.bearing_from_origin_cardinal}
                        </div>
                      </div>
                    )}

                {/* Elevation / Depth */}
                <div>
                  <div className="text-xs text-slate-400">Depth/Elevation</div>
                  <div className="text-white font-mono">
                    {nav.depth_elevation_label || '+/-0 m'}
                  </div>
                </div>

                {/* Heading */}
                {nav.heading_deg !== null && nav.heading_deg !== undefined && (
                  <div>
                    <div className="text-xs text-slate-400">Heading</div>
                    <div className="text-white font-mono">
                      {nav.heading_deg.toFixed(0)} deg
                    </div>
                  </div>
                )}

                {/* Return Distance */}
                {nav.estimated_return_route_distance_m && (
                  <div>
                    <div className="text-xs text-slate-400">Return Distance</div>
                    <div className="text-white font-mono">
                      {nav.estimated_return_route_distance_m.toFixed(1)} m
                    </div>
                  </div>
                )}

                {/* Return Time */}
                {nav.estimated_return_time_seconds && nav.estimated_return_time_seconds < 3600 && (
                  <div>
                    <div className="text-xs text-slate-400">Est. Return Time</div>
                    <div className="text-white font-mono">
                      {Math.floor(nav.estimated_return_time_seconds / 60)}:
                      {String(Math.floor(nav.estimated_return_time_seconds % 60)).padStart(2, '0')}
                    </div>
                  </div>
                )}

                {/* Nearest Relay */}
                {nav.nearest_relay && (
                  <div className="col-span-2">
                    <div className="text-xs text-slate-400">Nearest Relay</div>
                    <div className="text-white text-sm">
                      {nav.nearest_relay.relay_name} / {nav.nearest_relay.distance_m.toFixed(1)} m /{' '}
                      {nav.nearest_relay.bearing_deg.toFixed(0)} deg {nav.nearest_relay.bearing_cardinal}
                    </div>
                  </div>
                )}

                {/* Contact Path Length */}
                {nav.contact_path_length_m && (
                  <div>
                    <div className="text-xs text-slate-400">Contact Path</div>
                    <div className="text-white font-mono">
                      {nav.contact_path_length_m.toFixed(1)} m
                    </div>
                  </div>
                )}

                {/* Signal Strength */}
                <div>
                  <div className="text-xs text-slate-400">Signal</div>
                  <div className="text-white font-mono">{agent.signal_strength}%</div>
                </div>
              </div>

              {/* Vertical Profile */}
              {nav.vertical_profile_label && (
                <div className="mt-2 text-xs text-slate-400 italic">
                  {nav.vertical_profile_label}
                </div>
              )}
              </>
              )}
            </div>
          );
        })}
      </div>

      {/* Critical Detections */}
      {criticalDetections.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-slate-300 uppercase tracking-wide">
            Critical Detections
          </h3>

          {criticalDetections.map((detection) => {
            const nav = detection.navigation;
            if (!nav) return null;

            const hasValidBearing = nav.bearing_from_origin_deg !== null && nav.bearing_from_origin_deg !== undefined;

            return (
              <div
                key={detection.id}
                className="bg-orange-900/20 border border-orange-700 rounded-lg p-3"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="font-medium text-orange-200">
                      {detection.audio_type.replace('_', ' ').toUpperCase()}
                    </div>
                    <div className="text-xs text-orange-300">{detection.location_label}</div>
                  </div>
                  <div className="text-xs px-2 py-1 rounded bg-orange-900/40 text-orange-200">
                    {detection.confidence}% confidence
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                  {/* Distance */}
                  <div>
                    <div className="text-xs text-orange-400/70">Route Distance</div>
                    <div className="text-orange-100 font-mono">
                      {nav.route_distance_from_origin_m?.toFixed(1)} m
                    </div>
                  </div>

                  {/* Bearing */}
                  {hasValidBearing && (
                    <div>
                      <div className="text-xs text-orange-400/70">Bearing</div>
                      <div className="text-orange-100 font-mono">
                        {nav.bearing_from_origin_deg?.toFixed(0)} deg {nav.bearing_from_origin_cardinal}
                      </div>
                    </div>
                  )}

                  {/* Depth/Elevation */}
                  <div>
                    <div className="text-xs text-orange-400/70">Depth/Elevation</div>
                    <div className="text-orange-100 font-mono">
                      {nav.depth_elevation_label || '+/-0 m'}
                    </div>
                  </div>

                  {/* Contact Path Length */}
                  {nav.contact_path_length_m && (
                    <div>
                      <div className="text-xs text-orange-400/70">Contact Path</div>
                      <div className="text-orange-100 font-mono">
                        {nav.contact_path_length_m.toFixed(1)} m
                      </div>
                    </div>
                  )}

                  {/* Comms Risk */}
                  {nav.comms_risk && (
                    <div className="col-span-2">
                      <div className="text-xs text-orange-400/70">Comms Risk</div>
                      <div
                        className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                          nav.comms_risk === 'high'
                            ? 'bg-red-900/40 text-red-200'
                            : nav.comms_risk === 'medium'
                            ? 'bg-yellow-900/40 text-yellow-200'
                            : 'bg-green-900/40 text-green-200'
                        }`}
                      >
                        {nav.comms_risk.toUpperCase()}
                      </div>
                    </div>
                  )}
                </div>

                {/* Vertical Context */}
                {nav.vertical_context_label && (
                  <div className="mt-2 text-xs text-orange-300 italic">
                    {nav.vertical_context_label}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Info Footer */}
      <div className="text-xs text-slate-500 pt-2 border-t border-slate-700">
        GPS-denied navigation / Local 3D mission coordinates
      </div>
    </div>
  );
}
