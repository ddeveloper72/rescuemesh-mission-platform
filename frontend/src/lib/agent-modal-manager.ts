/**
 * Agent Detail Modal Manager
 * 
 * Manages the agent detail modal that displays comprehensive positioning,
 * payload, and operational status information for survey mapping and monitoring.
 */

import type { Agent } from '../types/simulation';

let currentAgentData: Agent | null = null;

/**
 * Initialize agent detail modal functionality
 */
export function initAgentModalManager(): void {
  const closeButton = document.getElementById('close-agent-modal');
  const modalBackdrop = document.getElementById('agent-modal-backdrop');
  const modal = document.getElementById('agent-detail-modal');

  if (closeButton) {
    closeButton.addEventListener('click', closeAgentModal);
  }

  if (modalBackdrop) {
    modalBackdrop.addEventListener('click', (e) => {
      if (e.target === modalBackdrop) {
        closeAgentModal();
      }
    });
  }

  if (modal) {
    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        closeAgentModal();
      }
    });
  }
}

/**
 * Show agent detail modal with comprehensive positioning and status data
 */
export function showAgentModal(agent: Agent): void {
  currentAgentData = agent;
  
  const modal = document.getElementById('agent-detail-modal');
  const backdrop = document.getElementById('agent-modal-backdrop');
  
  if (!modal || !backdrop) {
    console.warn('Agent modal elements not found');
    return;
  }

  // Populate modal with agent data
  populateAgentDetails(agent);
  
  // Show modal with animation
  backdrop.classList.remove('hidden');
  modal.classList.remove('hidden');
  
  // Trigger animation
  requestAnimationFrame(() => {
    backdrop.classList.remove('opacity-0');
    backdrop.classList.add('opacity-100');
    modal.classList.remove('scale-95', 'opacity-0');
    modal.classList.add('scale-100', 'opacity-100');
  });
}

/**
 * Close agent detail modal
 */
export function closeAgentModal(): void {
  const modal = document.getElementById('agent-detail-modal');
  const backdrop = document.getElementById('agent-modal-backdrop');
  
  if (!modal || !backdrop) return;

  // Animate out
  backdrop.classList.remove('opacity-100');
  backdrop.classList.add('opacity-0');
  modal.classList.remove('scale-100', 'opacity-100');
  modal.classList.add('scale-95', 'opacity-0');
  
  // Hide after animation
  setTimeout(() => {
    backdrop.classList.add('hidden');
    modal.classList.add('hidden');
    currentAgentData = null;
  }, 200);
}

/**
 * Populate agent detail modal with comprehensive data
 */
function populateAgentDetails(agent: Agent): void {
  // Agent identification
  setTextContent('agent-modal-name', agent.name);
  setTextContent('agent-modal-id', agent.agent_id);
  setTextContent('agent-modal-role', agent.role);
  
  // Operational status
  const statusBadge = document.getElementById('agent-modal-status');
  if (statusBadge) {
    statusBadge.textContent = agent.state;
    statusBadge.className = getStatusBadgeClass(agent.state);
  }
  
  // Battery and signal
  setTextContent('agent-modal-battery', `${agent.battery_percent}%`);
  setTextContent('agent-modal-signal', `${agent.signal_strength}%`);
  
  const batteryBar = document.getElementById('agent-modal-battery-bar');
  if (batteryBar) {
    batteryBar.style.width = `${agent.battery_percent}%`;
    batteryBar.className = getBatteryBarClass(agent.battery_percent);
  }
  
  const signalBar = document.getElementById('agent-modal-signal-bar');
  if (signalBar) {
    signalBar.style.width = `${agent.signal_strength}%`;
    signalBar.className = getSignalBarClass(agent.signal_strength);
  }
  
  // 3D Positioning data - absolute coordinates
  const pos = agent.position || { x: 0, y: 0, z: 0 };
  setTextContent('agent-modal-pos-x', pos.x?.toFixed(2) || '0.00');
  setTextContent('agent-modal-pos-y', pos.y?.toFixed(2) || '0.00');
  setTextContent('agent-modal-pos-z', pos.z?.toFixed(2) || '0.00');
  setTextContent('agent-modal-location', agent.location_label);
  
  // Navigation intelligence - relative to origin
  const nav = (agent as any).navigation;
  if (nav) {
    setTextContent('agent-modal-distance-2d', `${nav.distance_from_origin_m || 0} m`);
    setTextContent('agent-modal-distance-3d', `${nav.straight_line_3d_distance_from_origin_m || 0} m`);
    setTextContent('agent-modal-bearing', nav.bearing_from_origin_cardinal || 'N/A');
    setTextContent('agent-modal-bearing-deg', nav.bearing_from_origin_deg ? `${nav.bearing_from_origin_deg}°` : 'N/A');
    setTextContent('agent-modal-elevation', `${nav.elevation_m || 0} m`);
    setTextContent('agent-modal-depth', `${nav.depth_m || 0} m`);
    setTextContent('agent-modal-vertical-label', nav.vertical_profile_label || 'At origin level');
  } else {
    // No navigation data available
    setTextContent('agent-modal-distance-2d', 'N/A');
    setTextContent('agent-modal-distance-3d', 'N/A');
    setTextContent('agent-modal-bearing', 'N/A');
    setTextContent('agent-modal-bearing-deg', 'N/A');
    setTextContent('agent-modal-elevation', 'N/A');
    setTextContent('agent-modal-depth', 'N/A');
    setTextContent('agent-modal-vertical-label', 'No navigation data');
  }
  
  // Payload / Sensors
  const sensorsList = document.getElementById('agent-modal-sensors-list');
  if (sensorsList) {
    if (agent.sensors && agent.sensors.length > 0) {
      sensorsList.innerHTML = agent.sensors.map(sensor => 
        `<li class="flex items-center gap-2">
          <span class="w-2 h-2 bg-green-400 rounded-full"></span>
          <span class="text-slate-300">${sensor}</span>
        </li>`
      ).join('');
    } else {
      sensorsList.innerHTML = '<li class="text-slate-400 italic">No sensors equipped</li>';
    }
  }
  
  // Special capabilities
  const nfcBadge = document.getElementById('agent-modal-nfc-badge');
  if (nfcBadge) {
    if (agent.nfc_recovery_available) {
      nfcBadge.classList.remove('hidden');
    } else {
      nfcBadge.classList.add('hidden');
    }
  }
  
  // Survey data export section
  updateSurveyDataExport(agent);
}

/**
 * Update survey data export section with formatted positioning data
 */
function updateSurveyDataExport(agent: Agent): void {
  const surveyDataEl = document.getElementById('agent-modal-survey-data');
  if (!surveyDataEl) return;
  
  const pos = agent.position || { x: 0, y: 0, z: 0 };
  const nav = (agent as any).navigation;
  
  const surveyData = {
    agent_id: agent.agent_id,
    timestamp: new Date().toISOString(),
    position: {
      x: pos.x,
      y: pos.y,
      z: pos.z,
      location: agent.location_label
    },
    navigation: nav ? {
      distance_from_origin_m: nav.distance_from_origin_m,
      bearing_deg: nav.bearing_from_origin_deg,
      elevation_m: nav.elevation_m,
      depth_m: nav.depth_m
    } : null,
    status: {
      state: agent.state,
      battery_percent: agent.battery_percent,
      signal_strength: agent.signal_strength
    }
  };
  
  surveyDataEl.textContent = JSON.stringify(surveyData, null, 2);
}

/**
 * Helper function to safely set text content
 */
function setTextContent(elementId: string, content: string): void {
  const el = document.getElementById(elementId);
  if (el) el.textContent = content;
}

/**
 * Get CSS classes for status badge
 */
function getStatusBadgeClass(state: string): string {
  const baseClasses = 'px-3 py-1 rounded-full text-sm font-semibold';
  
  switch (state) {
    case 'healthy':
    case 'active':
      return `${baseClasses} bg-green-900 text-green-300`;
    case 'degraded':
    case 'intermittent':
      return `${baseClasses} bg-yellow-900 text-yellow-300`;
    case 'failed':
    case 'lost':
      return `${baseClasses} bg-red-900 text-red-300`;
    case 'landed_relay':
    case 'sacrificed':
      return `${baseClasses} bg-purple-900 text-purple-300`;
    default:
      return `${baseClasses} bg-slate-700 text-slate-300`;
  }
}

/**
 * Get CSS classes for battery bar
 */
function getBatteryBarClass(percent: number): string {
  if (percent > 60) {
    return 'h-full bg-green-500 transition-all duration-500';
  } else if (percent > 30) {
    return 'h-full bg-yellow-500 transition-all duration-500';
  } else {
    return 'h-full bg-red-500 transition-all duration-500';
  }
}

/**
 * Get CSS classes for signal bar
 */
function getSignalBarClass(percent: number): string {
  if (percent > 70) {
    return 'h-full bg-cyan-500 transition-all duration-500';
  } else if (percent > 40) {
    return 'h-full bg-yellow-500 transition-all duration-500';
  } else {
    return 'h-full bg-red-500 transition-all duration-500';
  }
}
