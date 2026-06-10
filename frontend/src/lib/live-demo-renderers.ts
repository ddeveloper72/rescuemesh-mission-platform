import type {
  Agent,
  AudioDetection,
  EnvironmentalReading,
  MediaFrame,
  MissionEvent,
} from '../types/simulation';

type SensorElementMap = Record<string, string>;

interface EventRenderOptions {
  containerId?: string;
  showSeverity?: boolean;
}

interface EnvironmentalReadingsOptions {
  resetMissing?: boolean;
  missingText?: string;
}

function escapeHtml(value: unknown): string {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function getSensorStatusClass(status: string): string {
  switch (status) {
    case 'normal':
      return 'text-green-400';
    case 'watch':
      return 'text-yellow-400';
    case 'warning':
      return 'text-orange-400';
    case 'critical':
      return 'text-red-400';
    default:
      return 'text-slate-300';
  }
}

export function renderAgentStatusPanel(
  agents: Agent[] | undefined,
  containerId = 'agents-container'
): void {
  const container = document.getElementById(containerId);
  if (!container || !agents) return;

  container.innerHTML = agents.map(agent => `
    <div class="p-4 bg-slate-700 rounded-lg">
      <div class="flex justify-between items-start mb-2">
        <div>
          <h3 class="font-semibold">${escapeHtml(agent.name)}</h3>
          <p class="text-xs text-slate-400">${escapeHtml(agent.role)}</p>
        </div>
        <span data-agent-state="${escapeHtml(agent.agent_id)}" class="px-2 py-1 rounded text-xs font-semibold bg-slate-800 text-slate-300">
          ${escapeHtml(agent.state)}
        </span>
      </div>
      <div class="space-y-2 text-sm">
        <div class="flex justify-between">
          <span class="text-slate-400">Battery:</span>
          <span data-agent-battery="${escapeHtml(agent.agent_id)}">${agent.battery_percent}%</span>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-400">Signal:</span>
          <span data-agent-signal="${escapeHtml(agent.agent_id)}">${agent.signal_strength}%</span>
        </div>
        <div class="flex justify-between">
          <span class="text-slate-400">Location:</span>
          <span class="text-xs">${escapeHtml(agent.location_label)}</span>
        </div>
        ${agent.nfc_recovery_available ? '<div class="text-xs text-yellow-400 mt-2">NFC recovery available</div>' : ''}
      </div>
      <div class="mt-2 h-2 bg-slate-900 rounded-full overflow-hidden">
        <div
          data-agent-battery-bar="${escapeHtml(agent.agent_id)}"
          class="h-full bg-green-500 transition-all duration-500"
          style="width: ${agent.battery_percent}%"
        ></div>
      </div>
    </div>
  `).join('');
}

function renderSeverityBadge(event: MissionEvent): string {
  const severity = (event as any).severity;
  if (severity === 'critical') {
    return '<span class="ml-2 px-2 py-0.5 bg-red-900 text-red-300 rounded text-xs font-semibold">CRITICAL</span>';
  }
  if (severity === 'high') {
    return '<span class="ml-2 px-2 py-0.5 bg-orange-900 text-orange-300 rounded text-xs font-semibold">HIGH</span>';
  }
  if (severity === 'moderate') {
    return '<span class="ml-2 px-2 py-0.5 bg-yellow-900 text-yellow-300 rounded text-xs font-semibold">MODERATE</span>';
  }
  return '';
}

export function renderMissionEvents(
  events: MissionEvent[] | undefined,
  options: EventRenderOptions = {}
): void {
  const container = document.getElementById(options.containerId || 'events-container');
  if (!container || !events) return;

  if (events.length === 0) {
    container.innerHTML = '<p class="text-slate-400">No events yet...</p>';
    return;
  }

  container.innerHTML = events.slice().reverse().map(event => `
    <div class="p-3 bg-slate-700 rounded-lg text-sm">
      <div class="flex justify-between items-start mb-1">
        <span class="font-semibold">${escapeHtml(event.title)}${options.showSeverity ? renderSeverityBadge(event) : ''}</span>
        <span class="text-xs text-slate-400">${escapeHtml(event.time)}</span>
      </div>
      <p class="text-slate-300 text-xs">${escapeHtml(event.description)}</p>
    </div>
  `).join('');
}

export function renderEnvironmentalReadings(
  readings: EnvironmentalReading[] | undefined,
  sensorElementMap: SensorElementMap,
  options: EnvironmentalReadingsOptions = {}
): void {
  Object.entries(sensorElementMap).forEach(([sensorType, elementId]) => {
    const element = document.getElementById(elementId);
    if (!element) return;

    const reading = readings?.find(item => item.sensor_type === sensorType);
    if (!reading) {
      if (options.resetMissing) {
        element.className = 'font-semibold text-slate-500';
        element.textContent = options.missingText || '--';
      }
      return;
    }

    element.className = `font-semibold ${getSensorStatusClass(reading.status)}`;
    element.textContent = `${reading.value}${reading.unit}`;
  });
}

export function dispatchMediaFeeds(mediaFeeds: MediaFrame[] | undefined): void {
  if (!mediaFeeds) return;

  window.dispatchEvent(new CustomEvent('media-feeds-update', {
    detail: { mediaFeeds }
  }));
}

export function dispatchAudioDetections(audioDetections: AudioDetection[] | undefined): void {
  if (!audioDetections) return;

  const transformedDetections = audioDetections.map((detection: any) => ({
    id: detection.id,
    agent_id: detection.agent_id,
    agent_name: detection.agent_name,
    sensor_type: 'microphone' as const,
    audio_type: detection.type,
    status: detection.status,
    mission_time: detection.detected_at,
    signal_quality: detection.confidence,
    confidence: detection.confidence,
    location_label: detection.location,
    annotations: detection.human_review_required ? ['Requires human review'] : [],
    description: detection.description,
    audio_url: undefined,
    spectrogram_url: undefined
  }));

  window.dispatchEvent(new CustomEvent('audio-detections-update', {
    detail: { audioDetections: transformedDetections }
  }));
}
