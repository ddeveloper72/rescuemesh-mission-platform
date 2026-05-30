/**
 * Client-side mission simulation manager.
 * 
 * Handles:
 * - Polling mission state from Django API
 * - Updating dashboard UI with live data
 * - Control button interactions (start/pause/reset/speed)
 * 
 * TODO: This is a simple vanilla implementation.
 * TODO: Future: Convert to React/Preact/Svelte island for better state management.
 * TODO: Future: Add WebSocket support for real-time updates instead of polling.
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

export class SimulationManager {
  private missionPk: string;
  private pollingInterval: number = 2000; // 2 seconds
  private pollTimer: number | null = null;
  private lastState: MissionSimulationState | null = null;
  private isPolling: boolean = false;

  constructor(missionPk: string) {
    this.missionPk = missionPk;
  }

  /**
   * Start polling for mission state updates.
   */
  startPolling() {
    if (this.isPolling) return;
    
    this.isPolling = true;
    this.poll(); // Initial poll
    
    this.pollTimer = window.setInterval(() => {
      this.poll();
    }, this.pollingInterval);
  }

  /**
   * Stop polling.
   */
  stopPolling() {
    this.isPolling = false;
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  }

  /**
   * Poll the mission state endpoint.
   */
  private async poll() {
    try {
      const result = await getMissionState(this.missionPk);
      
      if (result.success && result.data) {
        this.lastState = result.data;
        this.updateUI(result.data);
      } else {
        console.warn('Failed to fetch mission state:', result.error);
      }
    } catch (error) {
      console.error('Polling error:', error);
    }
  }

  /**
   * Update the dashboard UI with new state.
   * 
   * TODO: This updates DOM elements directly.
   * TODO: Future: Use a reactive framework for cleaner updates.
   */
  private updateUI(state: MissionSimulationState) {
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
    
    // Dispatch audio detections event for AudioDetectionsPanel
    if (state.audio_detections) {
      window.dispatchEvent(new CustomEvent('audio-detections-update', {
        detail: { audioDetections: state.audio_detections }
      }));
    }
    
    // Update control button states
    this.updateControlButtons(state.simulation_clock.is_running);
  }

  private updateClock(clock: MissionSimulationState['simulation_clock']) {
    const minutes = Math.floor(clock.elapsed_seconds / 60);
    const seconds = Math.floor(clock.elapsed_seconds % 60);
    const timeStr = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    const clockEl = document.getElementById('sim-clock');
    if (clockEl) {
      clockEl.textContent = timeStr;
    }
    
    const speedEl = document.getElementById('sim-speed');
    if (speedEl) {
      speedEl.textContent = clock.speed_multiplier.toString();
    }
    
    const statusEl = document.getElementById('sim-status');
    if (statusEl) {
      statusEl.textContent = clock.is_running ? '● Running' : '⏸ Paused';
      statusEl.className = clock.is_running
        ? 'px-3 py-1 bg-green-900 text-green-300 rounded-full'
        : 'px-3 py-1 bg-slate-700 text-slate-300 rounded-full';
    }
  }

  private updateAgents(agents: MissionSimulationState['agents']) {
    agents.forEach(agent => {
      // Update battery
      const batteryEl = document.querySelector(`[data-agent-battery="${agent.agent_id}"]`);
      if (batteryEl) {
        batteryEl.textContent = `${agent.battery_percent}%`;
        
        // Update battery bar if exists
        const batteryBarEl = document.querySelector(`[data-agent-battery-bar="${agent.agent_id}"]`) as HTMLElement;
        if (batteryBarEl) {
          batteryBarEl.style.width = `${agent.battery_percent}%`;
          
          // Color based on battery level
          if (agent.battery_percent > 50) {
            batteryBarEl.className = 'h-full bg-green-500 transition-all duration-500';
          } else if (agent.battery_percent > 20) {
            batteryBarEl.className = 'h-full bg-yellow-500 transition-all duration-500';
          } else {
            batteryBarEl.className = 'h-full bg-red-500 transition-all duration-500';
          }
        }
      }
      
      // Update signal strength
      const signalEl = document.querySelector(`[data-agent-signal="${agent.agent_id}"]`);
      if (signalEl) {
        signalEl.textContent = `${agent.signal_strength}%`;
      }
      
      // Update state
      const stateEl = document.querySelector(`[data-agent-state="${agent.agent_id}"]`);
      if (stateEl) {
        stateEl.textContent = agent.state;
        // Add color classes based on state
        stateEl.className = this.getStateClass(agent.state);
      }
    });
  }

  private updateNetwork(network: MissionSimulationState['network']) {
    const meshHealthEl = document.getElementById('mesh-health');
    if (meshHealthEl) {
      meshHealthEl.textContent = `${network.mesh_health}%`;
    }
    
    const packetLossEl = document.getElementById('packet-loss');
    if (packetLossEl) {
      packetLossEl.textContent = `${network.packet_loss_percent}%`;
    }

    const baseSignalEl = document.getElementById('base-signal');
    if (baseSignalEl) {
      baseSignalEl.textContent = `${network.base_signal_strength}%`;
    }

    // Update network health indicator
    this.updateNetworkHealthIndicator(network.mesh_health, network.packet_loss_percent);

    // Update relay chain
    this.updateRelayChain(network.relay_chain || []);
  }

  private updateNetworkHealthIndicator(meshHealth: number, packetLoss: number) {
    const indicatorEl = document.getElementById('network-health-indicator');
    const iconEl = document.getElementById('network-health-icon');
    const labelEl = document.getElementById('network-health-label');

    if (!indicatorEl || !iconEl || !labelEl) return;

    // Determine health status
    let status: 'healthy' | 'degraded' | 'critical';
    let icon: string;
    let label: string;
    let bgClass: string;

    if (meshHealth >= 80 && packetLoss <= 10) {
      status = 'healthy';
      icon = '🟢';
      label = 'Network Healthy';
      bgClass = 'bg-green-900/30';
    } else if (meshHealth >= 60 && packetLoss <= 20) {
      status = 'degraded';
      icon = '🟡';
      label = 'Network Degraded';
      bgClass = 'bg-amber-900/30';
    } else {
      status = 'critical';
      icon = '🔴';
      label = 'Network Critical';
      bgClass = 'bg-red-900/30';
    }

    iconEl.textContent = icon;
    labelEl.textContent = label;
    indicatorEl.className = `mb-4 p-3 rounded-lg ${bgClass}`;
  }

  private updateRelayChain(relayChain: string[]) {
    const relayChainEl = document.getElementById('relay-chain');
    if (!relayChainEl) return;

    if (!relayChain || relayChain.length === 0) {
      relayChainEl.innerHTML = '<p class="text-slate-500">No relays active</p>';
      return;
    }

    // Build relay chain visualization
    const relayItems = relayChain.map((agentId, index) => {
      const agentName = this.getAgentName(agentId);
      const isLast = index === relayChain.length - 1;
      const arrow = isLast ? '' : '↓';
      
      return `
        <div class="flex items-center gap-2">
          <span class="text-slate-400">→</span>
          <span class="text-slate-100">${agentName}</span>
          ${agentId === 'relay-1' ? '<span class="text-xs text-slate-500">(Base)</span>' : ''}
        </div>
        ${!isLast ? '<div class="text-slate-600 ml-3">↓</div>' : ''}
      `;
    }).join('');

    relayChainEl.innerHTML = relayItems;
  }

  private getAgentName(agentId: string): string {
    const agentNames: Record<string, string> = {
      'relay-1': 'Static Relay',
      'drone-a': 'Scout Drone A',
      'drone-b': 'Thermal/Audio Drone',
      'drone-c': 'Relay Drone',
    };
    return agentNames[agentId] || agentId;
  }

  private updateMap(map: MissionSimulationState['map']) {
    const coverageEl = document.getElementById('map-coverage');
    if (coverageEl) {
      coverageEl.textContent = `${map.coverage_percent}%`;
    }
    
    const confidenceEl = document.getElementById('map-confidence');
    if (confidenceEl) {
      confidenceEl.textContent = `${(map.confidence * 100).toFixed(0)}%`;
    }
    
    const pointsEl = document.getElementById('map-points');
    if (pointsEl) {
      pointsEl.textContent = map.total_points.toLocaleString();
    }
  }

  private updateSensors(sensors: MissionSimulationState['sensors']) {
    // Update counts
    const thermalCountEl = document.getElementById('thermal-count');
    if (thermalCountEl) {
      thermalCountEl.textContent = sensors.thermal_anomalies.length.toString();
    }
    
    const audioCountEl = document.getElementById('audio-count');
    if (audioCountEl) {
      audioCountEl.textContent = sensors.audio_events.length.toString();
    }
  }

  private updateEvents(events: MissionSimulationState['events']) {
    const eventCountEl = document.getElementById('event-count');
    if (eventCountEl) {
      eventCountEl.textContent = events.length.toString();
    }
  }

  private updateAI(ai: MissionSimulationState['ai_analysis']) {
    const aiSummaryEl = document.getElementById('ai-summary');
    if (aiSummaryEl) {
      aiSummaryEl.textContent = ai.summary;
    }
    
    const aiConfidenceEl = document.getElementById('ai-confidence');
    if (aiConfidenceEl) {
      aiConfidenceEl.textContent = `${(ai.confidence * 100).toFixed(0)}%`;
    }
  }

  private updateControlButtons(isRunning: boolean) {
    const startBtn = document.querySelector('[data-action="start"]') as HTMLButtonElement;
    const pauseBtn = document.querySelector('[data-action="pause"]') as HTMLButtonElement;
    
    if (startBtn) {
      startBtn.disabled = isRunning;
    }
    if (pauseBtn) {
      pauseBtn.disabled = !isRunning;
    }
  }

  private getStateClass(state: string): string {
    const baseClass = 'px-2 py-1 rounded text-xs font-semibold';
    
    if (state === 'healthy' || state === 'active') {
      return `${baseClass} bg-green-900 text-green-300`;
    } else if (state === 'degraded' || state === 'intermittent') {
      return `${baseClass} bg-yellow-900 text-yellow-300`;
    } else if (state === 'failed' || state === 'lost') {
      return `${baseClass} bg-red-900 text-red-300`;
    } else if (state === 'landed_relay') {
      return `${baseClass} bg-purple-900 text-purple-300`;
    } else if (state === 'sacrificed' || state === 'abandoned') {
      return `${baseClass} bg-slate-700 text-slate-300`;
    } else {
      return `${baseClass} bg-slate-800 text-slate-300`;
    }
  }

  /**
   * Control actions
   */
  
  async start() {
    const result = await startSimulation(this.missionPk);
    if (result.success) {
      console.log('Simulation started');
      this.poll(); // Immediate poll
    } else {
      console.error('Failed to start simulation:', result.error);
      alert(`Failed to start simulation: ${result.error}`);
    }
  }

  async pause() {
    const result = await pauseSimulation(this.missionPk);
    if (result.success) {
      console.log('Simulation paused');
      this.poll(); // Immediate poll
    } else {
      console.error('Failed to pause simulation:', result.error);
      alert(`Failed to pause simulation: ${result.error}`);
    }
  }

  async reset() {
    const result = await resetSimulation(this.missionPk);
    if (result.success) {
      console.log('Simulation reset');
      this.poll(); // Immediate poll
    } else {
      console.error('Failed to reset simulation:', result.error);
      alert(`Failed to reset simulation: ${result.error}`);
    }
  }

  async setSpeed(speed: number) {
    const result = await setSimulationSpeed(this.missionPk, speed);
    if (result.success && result.data) {
      console.log(`Speed set to ${result.data.speed_multiplier}x`);
      this.poll(); // Immediate poll
    } else {
      console.error('Failed to set speed:', result.error);
      alert(`Failed to set speed: ${result.error}`);
    }
  }

  /**
   * Get last known state (for debugging/testing).
   */
  getLastState(): MissionSimulationState | null {
    return this.lastState;
  }
}

/**
 * Initialize simulation manager when page loads.
 * 
 * Usage in Astro pages:
 * 
 * <script>
 *   import { initializeSimulation } from '../lib/simulation-manager';
 *   initializeSimulation('mission-uuid-here');
 * </script>
 */
export function initializeSimulation(missionPk: string): SimulationManager {
  const manager = new SimulationManager(missionPk);
  manager.startPolling();
  
  // Setup control button event listeners
  document.querySelectorAll('.sim-control-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const target = e.target as HTMLButtonElement;
      const action = target.dataset.action;
      
      if (action === 'start') {
        await manager.start();
      } else if (action === 'pause') {
        await manager.pause();
      } else if (action === 'reset') {
        await manager.reset();
      }
    });
  });
  
  // Setup speed selector
  const speedSelect = document.getElementById('speed-select') as HTMLSelectElement;
  if (speedSelect) {
    speedSelect.addEventListener('change', async (e) => {
      const speed = parseFloat((e.target as HTMLSelectElement).value);
      await manager.setSpeed(speed);
    });
  }
  
  // Cleanup on page unload
  window.addEventListener('beforeunload', () => {
    manager.stopPolling();
  });
  
  return manager;
}
