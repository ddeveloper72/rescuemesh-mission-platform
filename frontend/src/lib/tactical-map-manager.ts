/**
 * Tactical Map Manager
 * 
 * Renders and updates SVG tactical maps based on mission state.
 * Use-case specific layouts for different simulation types.
 */

import type { MissionSimulationState, Agent } from '../types/simulation';

interface MapConfig {
  sectors: Sector[];
  hazardZones?: HazardZone[];
  width: number;
  height: number;
}

interface Sector {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  type?: 'accessible' | 'blocked' | 'void' | 'water' | 'hazard';
}

interface HazardZone {
  id: string;
  x: number;
  y: number;
  radius: number;
  type: 'thermal' | 'gas' | 'electrical' | 'pressure';
}

/**
 * Industrial Inspection Map Configuration
 */
export function getIndustrialInspectionMapConfig(): MapConfig {
  return {
    width: 800,
    height: 450,
    sectors: [
      { id: 'entry', label: 'Entry Point', x: 50, y: 50, width: 120, height: 80, type: 'accessible' },
      { id: 'plant-room', label: 'Plant Room', x: 50, y: 150, width: 180, height: 120, type: 'accessible' },
      { id: 'pipe-gallery', label: 'Pipe Gallery', x: 250, y: 150, width: 200, height: 120, type: 'accessible' },
      { id: 'duct-section', label: 'Duct Section', x: 470, y: 150, width: 150, height: 120, type: 'accessible' },
      { id: 'control-cabinet', label: 'Control Cabinet', x: 640, y: 150, width: 110, height: 120, type: 'accessible' },
      { id: 'tank-interior', label: 'Tank Interior', x: 250, y: 290, width: 200, height: 110, type: 'hazard' },
    ]
  };
}

/**
 * Collapsed Building Map Configuration
 */
export function getCollapsedBuildingMapConfig(): MapConfig {
  return {
    width: 800,
    height: 450,
    sectors: [
      { id: 'entry', label: 'Entry', x: 50, y: 200, width: 100, height: 80, type: 'accessible' },
      { id: 'corridor-a', label: 'Corridor A', x: 170, y: 200, width: 150, height: 80, type: 'accessible' },
      { id: 'void-1', label: 'Void Space 1', x: 340, y: 140, width: 180, height: 120, type: 'void' },
      { id: 'corridor-b', label: 'Corridor B', x: 340, y: 280, width: 180, height: 100, type: 'accessible' },
      { id: 'collapsed', label: 'Collapsed Section', x: 540, y: 180, width: 200, height: 140, type: 'blocked' },
    ]
  };
}

/**
 * Cave Rescue Map Configuration
 */
export function getCaveRescueMapConfig(): MapConfig {
  return {
    width: 800,
    height: 450,
    sectors: [
      { id: 'entrance', label: 'Entrance Chamber', x: 50, y: 180, width: 140, height: 120, type: 'accessible' },
      { id: 'main-tunnel', label: 'Main Tunnel', x: 210, y: 200, width: 180, height: 80, type: 'accessible' },
      { id: 'narrow', label: 'Narrow Passage', x: 410, y: 220, width: 100, height: 40, type: 'hazard' },
      { id: 'junction', label: 'Junction Chamber', x: 530, y: 160, width: 140, height: 140, type: 'accessible' },
      { id: 'deep-squeeze', label: 'Deep Squeeze', x: 690, y: 200, width: 60, height: 80, type: 'blocked' },
    ]
  };
}

/**
 * Flooded Structure Map Configuration
 */
export function getFloodedStructureMapConfig(): MapConfig {
  return {
    width: 800,
    height: 450,
    sectors: [
      { id: 'entry-pool', label: 'Entry Pool (surface)', x: 50, y: 50, width: 150, height: 80, type: 'water' },
      { id: 'flooded-corridor', label: 'Flooded Corridor', x: 220, y: 50, width: 200, height: 150, type: 'water' },
      { id: 'plant-room', label: 'Plant Room (shallow)', x: 440, y: 50, width: 150, height: 150, type: 'water' },
      { id: 'submerged-zone', label: 'Submerged Zone', x: 220, y: 220, width: 370, height: 180, type: 'hazard' },
    ]
  };
}

/**
 * Get map configuration by use case
 */
export function getMapConfig(useCase: string): MapConfig {
  switch (useCase) {
    case 'industrial-inspection':
      return getIndustrialInspectionMapConfig();
    case 'collapsed-building-search':
      return getCollapsedBuildingMapConfig();
    case 'cave-rescue':
      return getCaveRescueMapConfig();
    case 'flooded-structure':
      return getFloodedStructureMapConfig();
    default:
      return { width: 800, height: 450, sectors: [] };
  }
}

/**
 * Render sectors on the map
 */
export function renderSectors(config: MapConfig) {
  const sectorsGroup = document.getElementById('map-sectors');
  if (!sectorsGroup) return;

  sectorsGroup.innerHTML = config.sectors.map(sector => {
    let fillColor = 'rgba(71, 85, 105, 0.3)'; // slate-600 default
    let strokeColor = 'rgba(148, 163, 184, 0.5)'; // slate-400

    if (sector.type === 'blocked') {
      fillColor = 'rgba(153, 27, 27, 0.3)'; // red-900
      strokeColor = 'rgba(252, 165, 165, 0.5)'; // red-300
    } else if (sector.type === 'void') {
      fillColor = 'rgba(88, 28, 135, 0.3)'; // purple-900
      strokeColor = 'rgba(216, 180, 254, 0.5)'; // purple-300
    } else if (sector.type === 'water') {
      fillColor = 'rgba(12, 74, 110, 0.3)'; // cyan-900
      strokeColor = 'rgba(103, 232, 249, 0.5)'; // cyan-300
    } else if (sector.type === 'hazard') {
      fillColor = 'rgba(133, 77, 14, 0.3)'; // yellow-900
      strokeColor = 'rgba(252, 211, 77, 0.5)'; // yellow-300
    }

    return `
      <rect 
        id="sector-${sector.id}"
        class="sector-area"
        x="${sector.x}" 
        y="${sector.y}" 
        width="${sector.width}" 
        height="${sector.height}"
        fill="${fillColor}"
        stroke="${strokeColor}"
        stroke-width="2"
        rx="4"
      />
      <text 
        x="${sector.x + sector.width / 2}" 
        y="${sector.y + sector.height / 2}"
        text-anchor="middle"
        dominant-baseline="middle"
        class="text-xs"
      >${sector.label}</text>
    `;
  }).join('');
}

/**
 * Update agent markers on the map
 */
export function updateAgents(agents: Agent[], config: MapConfig) {
  const agentsGroup = document.getElementById('map-agents');
  if (!agentsGroup) return;

  agentsGroup.innerHTML = agents.map(agent => {
    // Map agent location to sector
    const location = agent.location_label.toLowerCase();
    let sector = config.sectors.find(s => 
      location.includes(s.id) || location.includes(s.label.toLowerCase())
    );
    
    if (!sector) {
      // Default to first sector if no match
      sector = config.sectors[0];
    }

    // Position agent within sector (with some randomness for multiple agents)
    const x = sector.x + sector.width / 2 + (Math.random() - 0.5) * (sector.width * 0.3);
    const y = sector.y + sector.height / 2 + (Math.random() - 0.5) * (sector.height * 0.3);

    // Color based on agent state
    let color = '#10b981'; // green-500 for active/healthy
    if (agent.state === 'degraded' || agent.state === 'intermittent') {
      color = '#eab308'; // yellow-500
    } else if (agent.state === 'failed' || agent.state === 'lost') {
      color = '#ef4444'; // red-500
    } else if (agent.state === 'landed_relay' || agent.state === 'sacrificed') {
      color = '#a855f7'; // purple-500
    }

    return `
      <g id="agent-${agent.agent_id}" class="agent-marker">
        <circle 
          cx="${x}" 
          cy="${y}" 
          r="8"
          fill="${color}"
          stroke="#1e293b"
          stroke-width="2"
        />
        <title>${agent.name} - ${agent.state} (Battery: ${agent.battery_percent}%)</title>
      </g>
    `;
  }).join('');
}

/**
 * Render hazard markers (thermal, gas, etc.)
 */
export function renderHazards(state: MissionSimulationState) {
  const hazardsGroup = document.getElementById('map-hazards');
  if (!hazardsGroup) return;

  const markers: string[] = [];

  // Thermal anomalies
  state.sensors.thermal_anomalies.forEach((thermal, index) => {
    const x = 100 + index * 150; // Simple layout
    const y = 100;
    markers.push(`
      <g class="hazard-marker">
        <circle 
          cx="${x}" 
          cy="${y}" 
          r="12"
          fill="rgba(239, 68, 68, 0.3)"
          stroke="#ef4444"
          stroke-width="2"
        />
        <text x="${x}" y="${y + 25}" text-anchor="middle" class="text-xs">🔥</text>
      </g>
    `);
  });

  hazardsGroup.innerHTML = markers.join('');
}

/**
 * Initialize tactical map
 */
export function initializeTacticalMap(useCase: string) {
  const config = getMapConfig(useCase);
  renderSectors(config);
  
  return config;
}

/**
 * Update tactical map with new mission state
 */
export function updateTacticalMap(state: MissionSimulationState, config: MapConfig) {
  updateAgents(state.agents, config);
  renderHazards(state);
}
