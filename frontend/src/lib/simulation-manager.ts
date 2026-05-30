/**
 * Mission Simulation Manager
 * 
 * Manages the lifecycle and state of mission simulations:
 * - Polls Django REST API for mission state updates (2-second interval)
 * - Updates dashboard UI elements with live mission data
 * - Handles user control interactions (start/pause/reset/speed)
 * - Coordinates auto-scroll behavior to guide user attention
 * 
 * Architecture: Vanilla TypeScript with direct DOM manipulation.
 * Future enhancement path: Convert to reactive framework (React/Preact/Svelte) for better state management.
 * Future enhancement path: Replace polling with WebSocket for real-time updates.
 * 
 * @module simulation-manager
 */

import type { MissionSimulationState } from '../types/simulation';
import {
  getMissionState,
  startSimulation,
  pauseSimulation,
  resetSimulation,
  setSimulationSpeed,
} from './api';
import { updateDetectionData } from './detection-modal-manager';

// ====================
// DOM SELECTOR CONSTANTS
// ====================

/** Primary UI element selectors */
const SELECTORS = {
  // Simulation Controls
  CLOCK: 'sim-clock',
  SPEED: 'sim-speed',
  STATUS: 'sim-status',
  SPEED_SELECT: 'speed-select',
  
  // Network Status
  MESH_HEALTH: 'mesh-health',
  PACKET_LOSS: 'packet-loss',
  BASE_SIGNAL: 'base-signal',
  NETWORK_HEALTH_INDICATOR: 'network-health-indicator',
  NETWORK_HEALTH_ICON: 'network-health-icon',
  NETWORK_HEALTH_LABEL: 'network-health-label',
  RELAY_CHAIN: 'relay-chain',
  
  // Map Status
  MAP_COVERAGE: 'map-coverage',
  MAP_CONFIDENCE: 'map-confidence',
  MAP_POINTS: 'map-points',
  
  // Sensors
  THERMAL_COUNT: 'thermal-count',
  AUDIO_COUNT: 'audio-count',
  
  // AI Analysis
  AI_SUMMARY: 'ai-summary',
  AI_CONFIDENCE: 'ai-confidence',
  
  // Events
  EVENT_COUNT: 'event-count',
  
  // Tactical Map Container (for auto-scroll)
  TACTICAL_MAP_CONTAINER: 'tactical-map-container',
} as const;

/** Data attribute selectors for agent-specific elements */
const AGENT_SELECTORS = {
  BATTERY: 'data-agent-battery',
  BATTERY_BAR: 'data-agent-battery-bar',
  SIGNAL: 'data-agent-signal',
  STATE: 'data-agent-state',
} as const;

/** Control button action identifiers */
const CONTROL_ACTIONS = {
  START: 'start',
  PAUSE: 'pause',
  RESET: 'reset',
} as const;

/** Custom event names for inter-component communication */
const CUSTOM_EVENTS = {
  AUDIO_DETECTIONS_UPDATE: 'audio-detections-update',
} as const;

// ====================
// CONFIGURATION CONSTANTS
// ====================

/** Polling interval in milliseconds */
const POLLING_INTERVAL_MS = 2000;

/** Battery level thresholds for visual indicators */
const BATTERY_THRESHOLDS = {
  HEALTHY: 50,
  WARNING: 20,
} as const;

/** Network health thresholds */
const NETWORK_THRESHOLDS = {
  HEALTHY: { MESH_HEALTH: 80, PACKET_LOSS: 10 },
  DEGRADED: { MESH_HEALTH: 60, PACKET_LOSS: 20 },
} as const;

/** Smooth scroll configuration */
const SCROLL_CONFIG = {
  BEHAVIOR: 'smooth' as ScrollBehavior,
  BLOCK: 'start' as ScrollLogicalPosition,
  INLINE: 'nearest' as ScrollLogicalPosition,
} as const;

// ====================
// TYPE DEFINITIONS
// ====================

/** Agent identifier to display name mapping */
type AgentNameMap = Record<string, string>;

/** Network health status levels */
type NetworkHealthStatus = 'healthy' | 'degraded' | 'critical';

/** Agent state classification for visual styling */
type AgentStateType = 'healthy' | 'active' | 'degraded' | 'intermittent' | 'failed' | 'lost' | 'landed_relay' | 'sacrificed' | 'abandoned';

// ====================
// UTILITY FUNCTIONS
// ====================

/**
 * Safely retrieve a DOM element by ID.
 * Logs a warning if element is not found (helps catch template issues).
 */
function getElementByIdSafe(id: string): HTMLElement | null {
  const element = document.getElementById(id);
  if (!element) {
    console.warn(`[SimulationManager] Element not found: #${id}`);
  }
  return element;
}

/**
 * Safely query a DOM element by selector.
 */
function querySelectorSafe<T extends Element>(selector: string): T | null {
  return document.querySelector<T>(selector);
}

/**
 * Format elapsed seconds into ISO 8601-compliant HH:MM:SS display format.
 * Follows ISO 8601 time representation for mission elapsed time display.
 */
function formatMissionTime(elapsedSeconds: number): string {
  const hours = Math.floor(elapsedSeconds / 3600);
  const minutes = Math.floor((elapsedSeconds % 3600) / 60);
  const seconds = Math.floor(elapsedSeconds % 60);
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

/**
 * Determine battery health CSS classes based on percentage.
 */
function getBatteryHealthClass(batteryPercent: number): string {
  if (batteryPercent > BATTERY_THRESHOLDS.HEALTHY) {
    return 'h-full bg-green-500 transition-all duration-500';
  } else if (batteryPercent > BATTERY_THRESHOLDS.WARNING) {
    return 'h-full bg-yellow-500 transition-all duration-500';
  } else {
    return 'h-full bg-red-500 transition-all duration-500';
  }
}

/**
 * Map agent IDs to human-readable display names.
 */
function getAgentDisplayName(agentId: string): string {
  const agentNames: AgentNameMap = {
    'relay-1': 'Static Relay',
    'drone-a': 'Scout Drone A',
    'drone-b': 'Thermal/Audio Drone',
    'drone-c': 'Relay Drone',
  };
  return agentNames[agentId] || agentId;
}

/**
 * Get CSS classes for agent state badges.
 */
function getAgentStateClass(state: string): string {
  const baseClass = 'px-2 py-1 rounded text-xs font-semibold';
  
  const stateClassMap: Record<string, string> = {
    'healthy': `${baseClass} bg-green-900 text-green-300`,
    'active': `${baseClass} bg-green-900 text-green-300`,
    'degraded': `${baseClass} bg-yellow-900 text-yellow-300`,
    'intermittent': `${baseClass} bg-yellow-900 text-yellow-300`,
    'failed': `${baseClass} bg-red-900 text-red-300`,
    'lost': `${baseClass} bg-red-900 text-red-300`,
    'landed_relay': `${baseClass} bg-purple-900 text-purple-300`,
    'sacrificed': `${baseClass} bg-slate-700 text-slate-300`,
    'abandoned': `${baseClass} bg-slate-700 text-slate-300`,
  };
  
  return stateClassMap[state] || `${baseClass} bg-slate-800 text-slate-300`;
}

/**
 * Smoothly scroll to the tactical map to bring mission activity into view.
 * Called when simulation starts to guide user attention.
 */
function scrollToTacticalMap(): void {
  // Try multiple possible container IDs/classes (different use cases may use different IDs)
  const possibleSelectors = [
    '#tactical-map-container',
    '[class*="tactical-map"]',
    '.tactical-map',
  ];
  
  for (const selector of possibleSelectors) {
    const mapElement = document.querySelector(selector);
    if (mapElement) {
      // Small delay to let the UI update first
      setTimeout(() => {
        mapElement.scrollIntoView({
          behavior: SCROLL_CONFIG.BEHAVIOR,
          block: SCROLL_CONFIG.BLOCK,
          inline: SCROLL_CONFIG.INLINE,
        });
      }, 300);
      return;
    }
  }
  
  console.warn('[SimulationManager] Could not find tactical map element for auto-scroll');
}

/**
 * SimulationManager Class
 * 
 * Orchestrates mission simulation state management and UI updates.
 * Implements polling-based synchronization with Django backend.
 */
export class SimulationManager {
  private readonly missionPk: string;
  private readonly pollingInterval: number = POLLING_INTERVAL_MS;
  private pollTimer: number | null = null;
  private lastState: MissionSimulationState | null = null;
  private isPolling: boolean = false;

  /**
   * Create a new SimulationManager instance.
   * @param missionPk - Unique identifier for the mission to manage
   */
  constructor(missionPk: string) {
    this.missionPk = missionPk;
  }

  /**
   * Start polling for mission state updates from the API.
   * Performs an immediate poll followed by recurring polls at configured interval.
   * Safe to call multiple times (idempotent).
   */
  startPolling(): void {
    if (this.isPolling) {
      console.debug('[SimulationManager] Polling already active');
      return;
    }
    
    this.isPolling = true;
    this.poll(); // Immediate initial poll
    
    this.pollTimer = window.setInterval(() => {
      this.poll();
    }, this.pollingInterval);
    
    console.debug(`[SimulationManager] Started polling (interval: ${this.pollingInterval}ms)`);
  }

  /**
   * Stop polling for mission state updates.
   * Cleans up interval timer to prevent memory leaks.
   */
  stopPolling(): void {
    this.isPolling = false;
    
    if (this.pollTimer !== null) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
    
    console.debug('[SimulationManager] Stopped polling');
  }

  /**
   * Execute a single poll of the mission state endpoint.
   * Updates UI if successful, logs errors if failed.
   * @private
   */
  private async poll(): Promise<void> {
    try {
      const result = await getMissionState(this.missionPk);
      
      if (result.success && result.data) {
        this.lastState = result.data;
        this.updateUI(result.data);
      } else {
        console.warn('[SimulationManager] Failed to fetch mission state:', result.error);
      }
    } catch (error) {
      console.error('[SimulationManager] Polling error:', error);
      // Continue polling despite errors (transient network issues should auto-recover)
    }
  }

  /**
   * Update all dashboard UI elements with fresh mission state.
   * Coordinates updates across multiple subsystems (clock, agents, network, map, sensors, AI).
   * 
   * @param state - Complete mission state from backend API
   * @private
   */
  private updateUI(state: MissionSimulationState): void {
    // Update detection data for modal manager
    updateDetectionData(state);
    
    // Update simulation clock
    this.updateClock(state.simulation_clock);
    
    // Update agents
    this.updateAgents(state.agents);
    
    // Update network
    this.updateNetwork(state.network);
    
    // Update map
    this.updateMap(state.map);
    
    // Update sensors
    this.updateSensors(state.sensors);
    
    // Update events
    this.updateEvents(state.events);
    
    // Update AI analysis
    this.updateAI(state.ai_analysis);
    
    // Dispatch audio detections event for AudioDetectionsPanel (React island)
    if (state.audio_detections) {
      window.dispatchEvent(new CustomEvent(CUSTOM_EVENTS.AUDIO_DETECTIONS_UPDATE, {
        detail: { audioDetections: state.audio_detections }
      }));
    }
    
    // Update control button states based on running status
    this.updateControlButtons(state.simulation_clock.is_running);
  }

  /**
   * Update simulation clock display elements.
   * @param clock - Simulation clock state from backend
   * @private
   */
  private updateClock(clock: MissionSimulationState['simulation_clock']): void {
    const timeStr = formatMissionTime(clock.elapsed_seconds);
    
    const clockEl = getElementByIdSafe(SELECTORS.CLOCK);
    if (clockEl) {
      clockEl.textContent = timeStr;
    }
    
    const speedEl = getElementByIdSafe(SELECTORS.SPEED);
    if (speedEl) {
      speedEl.textContent = `${clock.speed_multiplier}x`;
    }
    
    const statusEl = getElementByIdSafe(SELECTORS.STATUS);
    if (statusEl) {
      statusEl.textContent = clock.is_running ? '● Running' : '⏸ Paused';
      statusEl.className = clock.is_running
        ? 'px-3 py-1 bg-green-900 text-green-300 rounded-full'
        : 'px-3 py-1 bg-slate-700 text-slate-300 rounded-full';
    }
  }

  /**
   * Update all agent status displays (battery, signal, state).
   * @param agents - Array of agent states from backend
   * @private
   */
  private updateAgents(agents: MissionSimulationState['agents']): void {
    agents.forEach(agent => {
      this.updateAgentBattery(agent.agent_id, agent.battery_percent);
      this.updateAgentSignal(agent.agent_id, agent.signal_strength);
      this.updateAgentState(agent.agent_id, agent.state);
    });
  }

  /**
   * Update battery display and visual indicator for a specific agent.
   * @private
   */
  private updateAgentBattery(agentId: string, batteryPercent: number): void {
    const batteryEl = querySelectorSafe(`[${AGENT_SELECTORS.BATTERY}="${agentId}"]`);
    if (batteryEl) {
      batteryEl.textContent = `${batteryPercent}%`;
    }
    
    const batteryBarEl = querySelectorSafe<HTMLElement>(`[${AGENT_SELECTORS.BATTERY_BAR}="${agentId}"]`);
    if (batteryBarEl) {
      batteryBarEl.style.width = `${batteryPercent}%`;
      batteryBarEl.className = getBatteryHealthClass(batteryPercent);
    }
  }

  /**
   * Update signal strength display for a specific agent.
   * @private
   */
  private updateAgentSignal(agentId: string, signalStrength: number): void {
    const signalEl = querySelectorSafe(`[${AGENT_SELECTORS.SIGNAL}="${agentId}"]`);
    if (signalEl) {
      signalEl.textContent = `${signalStrength}%`;
    }
  }

  /**
   * Update state badge for a specific agent.
   * @private
   */
  private updateAgentState(agentId: string, state: string): void {
    const stateEl = querySelectorSafe(`[${AGENT_SELECTORS.STATE}="${agentId}"]`);
    if (stateEl) {
      stateEl.textContent = state;
      stateEl.className = getAgentStateClass(state);
    }
  }

  /**
   * Update network status displays (mesh health, packet loss, signal, relay chain).
   * @param network - Network state from backend
   * @private
   */
  private updateNetwork(network: MissionSimulationState['network']): void {
    const meshHealthEl = getElementByIdSafe(SELECTORS.MESH_HEALTH);
    if (meshHealthEl) {
      meshHealthEl.textContent = `${network.mesh_health}%`;
    }
    
    const packetLossEl = getElementByIdSafe(SELECTORS.PACKET_LOSS);
    if (packetLossEl) {
      packetLossEl.textContent = `${network.packet_loss_percent}%`;
    }

    const baseSignalEl = getElementByIdSafe(SELECTORS.BASE_SIGNAL);
    if (baseSignalEl) {
      baseSignalEl.textContent = `${network.base_signal_strength}%`;
    }

    this.updateNetworkHealthIndicator(network.mesh_health, network.packet_loss_percent);
    this.updateRelayChain(network.relay_chain || []);
  }

  /**
   * Update network health indicator based on mesh health and packet loss metrics.
   * Displays visual status (icon, label, background color) reflecting network quality.
   * @param meshHealth - Mesh network health percentage (0-100)
   * @param packetLoss - Packet loss percentage (0-100)
   * @private
   */
  private updateNetworkHealthIndicator(meshHealth: number, packetLoss: number): void {
    const indicatorEl = getElementByIdSafe(SELECTORS.NETWORK_HEALTH_INDICATOR);
    const iconEl = getElementByIdSafe(SELECTORS.NETWORK_HEALTH_ICON);
    const labelEl = getElementByIdSafe(SELECTORS.NETWORK_HEALTH_LABEL);

    if (!indicatorEl || !iconEl || !labelEl) return;

    const healthStatus = this.determineNetworkHealthStatus(meshHealth, packetLoss);
    const { icon, label, bgClass } = this.getNetworkHealthDisplayProps(healthStatus);

    iconEl.textContent = icon;
    labelEl.textContent = label;
    indicatorEl.className = `mb-4 p-3 rounded-lg ${bgClass}`;
  }

  /**
   * Determine network health status based on metrics.
   * @private
   */
  private determineNetworkHealthStatus(meshHealth: number, packetLoss: number): NetworkHealthStatus {
    if (meshHealth >= NETWORK_THRESHOLDS.HEALTHY.MESH_HEALTH && 
        packetLoss <= NETWORK_THRESHOLDS.HEALTHY.PACKET_LOSS) {
      return 'healthy';
    } else if (meshHealth >= NETWORK_THRESHOLDS.DEGRADED.MESH_HEALTH && 
               packetLoss <= NETWORK_THRESHOLDS.DEGRADED.PACKET_LOSS) {
      return 'degraded';
    } else {
      return 'critical';
    }
  }

  /**
   * Get display properties (icon, label, CSS class) for network health status.
   * @private
   */
  private getNetworkHealthDisplayProps(status: NetworkHealthStatus): { icon: string; label: string; bgClass: string } {
    const displayProps = {
      'healthy': {
        icon: '🟢',
        label: 'Network Healthy',
        bgClass: 'bg-green-900/30',
      },
      'degraded': {
        icon: '🟡',
        label: 'Network Degraded',
        bgClass: 'bg-amber-900/30',
      },
      'critical': {
        icon: '🔴',
        label: 'Network Critical',
        bgClass: 'bg-red-900/30',
      },
    };
    
    return displayProps[status];
  }

  /**
   * Update relay chain visualization showing communication path through agents.
   * @param relayChain - Ordered array of agent IDs forming the relay chain
   * @private
   */
  private updateRelayChain(relayChain: string[]): void {
    const relayChainEl = getElementByIdSafe(SELECTORS.RELAY_CHAIN);
    if (!relayChainEl) return;

    if (!relayChain || relayChain.length === 0) {
      relayChainEl.innerHTML = '<p class="text-slate-500">No relays active</p>';
      return;
    }

    const relayItems = relayChain.map((agentId, index) => {
      const agentName = getAgentDisplayName(agentId);
      const isLast = index === relayChain.length - 1;
      const isBaseRelay = agentId === 'relay-1';
      
      return `
        <div class="flex items-center gap-2">
          <span class="text-slate-400">→</span>
          <span class="text-slate-100">${agentName}</span>
          ${isBaseRelay ? '<span class="text-xs text-slate-500">(Base)</span>' : ''}
        </div>
        ${!isLast ? '<div class="text-slate-600 ml-3">↓</div>' : ''}
      `;
    }).join('');

    relayChainEl.innerHTML = relayItems;
  }

  /**
   * Update map status displays (coverage, confidence, point count).
   * @private
   */
  private updateMap(map: MissionSimulationState['map']): void {
    const coverageEl = getElementByIdSafe(SELECTORS.MAP_COVERAGE);
    if (coverageEl) {
      coverageEl.textContent = `${map.coverage_percent}%`;
    }
    
    const confidenceEl = getElementByIdSafe(SELECTORS.MAP_CONFIDENCE);
    if (confidenceEl) {
      confidenceEl.textContent = `${(map.confidence * 100).toFixed(0)}%`;
    }
    
    const pointsEl = getElementByIdSafe(SELECTORS.MAP_POINTS);
    if (pointsEl) {
      pointsEl.textContent = map.total_points.toLocaleString();
    }
  }

  /**
   * Update sensor event count displays.
   * @private
   */
  private updateSensors(sensors: MissionSimulationState['sensors']): void {
    const thermalCountEl = getElementByIdSafe(SELECTORS.THERMAL_COUNT);
    if (thermalCountEl) {
      thermalCountEl.textContent = sensors.thermal_anomalies.length.toString();
    }
    
    const audioCountEl = getElementByIdSafe(SELECTORS.AUDIO_COUNT);
    if (audioCountEl) {
      audioCountEl.textContent = sensors.audio_events.length.toString();
    }
  }

  /**
   * Update mission events count display.
   * @private
   */
  private updateEvents(events: MissionSimulationState['events']): void {
    const eventCountEl = getElementByIdSafe(SELECTORS.EVENT_COUNT);
    if (eventCountEl) {
      eventCountEl.textContent = events.length.toString();
    }
  }

  /**
   * Update AI analysis displays (summary text, confidence).
   * @private
   */
  private updateAI(ai: MissionSimulationState['ai_analysis']): void {
    const aiSummaryEl = getElementByIdSafe(SELECTORS.AI_SUMMARY);
    if (aiSummaryEl) {
      aiSummaryEl.textContent = ai.summary;
    }
    
    const aiConfidenceEl = getElementByIdSafe(SELECTORS.AI_CONFIDENCE);
    if (aiConfidenceEl) {
      aiConfidenceEl.textContent = `${(ai.confidence * 100).toFixed(0)}%`;
    }
  }

  /**
   * Update enabled/disabled state of control buttons based on simulation status.
   * @param isRunning - Whether simulation is currently running
   * @private
   */
  private updateControlButtons(isRunning: boolean): void {
    const startBtn = querySelectorSafe<HTMLButtonElement>(`[data-action="${CONTROL_ACTIONS.START}"]`);
    const pauseBtn = querySelectorSafe<HTMLButtonElement>(`[data-action="${CONTROL_ACTIONS.PAUSE}"]`);
    
    if (startBtn) {
      startBtn.disabled = isRunning;
    }
    if (pauseBtn) {
      pauseBtn.disabled = !isRunning;
    }
  }

  // ====================
  // PUBLIC CONTROL METHODS
  // ====================

  /**
   * Start the mission simulation.
   * Sends start command to backend and immediately polls for updated state.
   * Auto-scrolls to tactical map to bring mission activity into user's view.
   */
  async start(): Promise<void> {
    const result = await startSimulation(this.missionPk);
    
    if (result.success) {
      console.log('[SimulationManager] Simulation started successfully');
      await this.poll(); // Immediate poll to update UI
      
      // Auto-scroll to tactical map to bring mission data into view
      scrollToTacticalMap();
    } else {
      console.error('[SimulationManager] Failed to start simulation:', result.error);
      this.showErrorNotification('Failed to start simulation', result.error);
    }
  }

  /**
   * Pause the mission simulation.
   * Sends pause command to backend and immediately polls for updated state.
   */
  async pause(): Promise<void> {
    const result = await pauseSimulation(this.missionPk);
    
    if (result.success) {
      console.log('[SimulationManager] Simulation paused');
      await this.poll();
    } else {
      console.error('[SimulationManager] Failed to pause simulation:', result.error);
      this.showErrorNotification('Failed to pause simulation', result.error);
    }
  }

  /**
   * Reset the mission simulation to initial state.
   * Sends reset command to backend and immediately polls for updated state.
   */
  async reset(): Promise<void> {
    const result = await resetSimulation(this.missionPk);
    
    if (result.success) {
      console.log('[SimulationManager] Simulation reset');
      await this.poll();
    } else {
      console.error('[SimulationManager] Failed to reset simulation:', result.error);
      this.showErrorNotification('Failed to reset simulation', result.error);
    }
  }

  /**
   * Set simulation speed multiplier.
   * @param speed - Speed multiplier (e.g., 1.0 = real-time, 3.0 = 3x speed)
   */
  async setSpeed(speed: number): Promise<void> {
    const result = await setSimulationSpeed(this.missionPk, speed);
    
    if (result.success && result.data) {
      console.log(`[SimulationManager] Speed set to ${result.data.speed_multiplier}x`);
      await this.poll();
    } else {
      console.error('[SimulationManager] Failed to set speed:', result.error);
      this.showErrorNotification('Failed to set speed', result.error);
    }
  }

  /**
   * Display user-friendly error notification.
   * Currently uses browser alert; future enhancement: use toast/notification system.
   * @private
   */
  private showErrorNotification(title: string, error: string | undefined): void {
    const message = error ? `${title}: ${error}` : title;
    alert(message);
    // Future: Replace with toast notification system
  }

  /**
   * Get the last known mission state.
   * Useful for debugging, testing, or accessing current state without triggering a poll.
   * @returns Most recent mission state, or null if no state has been received yet
   */
  getLastState(): MissionSimulationState | null {
    return this.lastState;
  }
}

// ====================
// INITIALIZATION FUNCTION
// ====================


/**
 * Initialize and start the simulation manager for a mission.
 * 
 * Sets up:
 * - SimulationManager instance
 * - Automatic polling (2-second interval)
 * - Control button event listeners (start/pause/reset)
 * - Speed selector event listener
 * - Cleanup on page unload
 * 
 * Usage in Astro pages:
 * ```typescript
 * <script>
 *   import { initializeSimulation } from '../lib/simulation-manager';
 *   const manager = initializeSimulation('mission-uuid-here');
 * </script>
 * ```
 * 
 * @param missionPk - Unique identifier for the mission
 * @returns SimulationManager instance (for advanced control if needed)
 */
export function initializeSimulation(missionPk: string): SimulationManager {
  const manager = new SimulationManager(missionPk);
  manager.startPolling();
  
  setupControlButtonListeners(manager);
  setupSpeedSelectorListener(manager);
  setupCleanupHandler(manager);
  
  return manager;
}

/**
 * Setup event listeners for simulation control buttons.
 * @private
 */
function setupControlButtonListeners(manager: SimulationManager): void {
  document.querySelectorAll('.sim-control-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const target = e.target as HTMLButtonElement;
      const action = target.dataset.action;
      
      switch (action) {
        case CONTROL_ACTIONS.START:
          await manager.start();
          break;
        case CONTROL_ACTIONS.PAUSE:
          await manager.pause();
          break;
        case CONTROL_ACTIONS.RESET:
          await manager.reset();
          break;
        default:
          console.warn(`[SimulationManager] Unknown control action: ${action}`);
      }
    });
  });
}

/**
 * Setup event listener for speed selector dropdown.
 * @private
 */
function setupSpeedSelectorListener(manager: SimulationManager): void {
  const speedSelect = getElementByIdSafe(SELECTORS.SPEED_SELECT) as HTMLSelectElement;
  if (speedSelect) {
    speedSelect.addEventListener('change', async (e) => {
      const speed = parseFloat((e.target as HTMLSelectElement).value);
      await manager.setSpeed(speed);
    });
  }
}

/**
 * Setup cleanup handler to stop polling when page unloads.
 * @private
 */
function setupCleanupHandler(manager: SimulationManager): void {
  window.addEventListener('beforeunload', () => {
    manager.stopPolling();
  });
}
