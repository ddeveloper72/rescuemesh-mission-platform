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

type CapabilityPackName = 'lighting' | 'seismic' | 'hydrophone' | 'talkback';
type CapabilityPackData = Partial<Record<CapabilityPackName, any>>;

interface EscalationRenderOptions {
  containerId?: string;
  contactRiskElementId?: string;
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

function hasCapabilityData(pack: CapabilityPackName, data: any): boolean {
  if (!data) return false;

  switch (pack) {
    case 'lighting':
      return Object.keys(data).length > 0;
    case 'seismic':
      return (data.sensors?.length || 0) > 0 || (data.detections?.length || 0) > 0;
    case 'hydrophone':
      return (data.hydrophones?.length || 0) > 0 || (data.detections?.length || 0) > 0;
    case 'talkback':
      return (data.messages?.length || 0) > 0 || (data.responses?.length || 0) > 0;
  }
}

function dispatchCapabilityUpdate(pack: CapabilityPackName, data: any): void {
  if (!data) return;

  const eventMap = {
    lighting: { name: 'lighting-update', detailKey: 'lightingStates' },
    seismic: { name: 'seismic-update', detailKey: 'seismicData' },
    hydrophone: { name: 'hydrophone-update', detailKey: 'hydrophoneData' },
    talkback: { name: 'talkback-update', detailKey: 'talkbackData' }
  } satisfies Record<CapabilityPackName, { name: string; detailKey: string }>;

  const event = eventMap[pack];
  window.dispatchEvent(new CustomEvent(event.name, {
    detail: { [event.detailKey]: data }
  }));
}

export function updateCapabilityPacks(capabilityPacks: CapabilityPackData): void {
  Object.entries(capabilityPacks).forEach(([packName, data]) => {
    const pack = packName as CapabilityPackName;
    const tab = document.querySelector<HTMLButtonElement>(`button[data-pack="${pack}"]`);
    const hasData = hasCapabilityData(pack, data);

    if (tab) {
      tab.disabled = !hasData;
      tab.classList.toggle('opacity-40', !hasData);
      tab.classList.toggle('cursor-not-allowed', !hasData);
      tab.classList.toggle('hover:bg-slate-600', hasData);
    }

    dispatchCapabilityUpdate(pack, data);
  });
}

export function initializeCapabilityPackTabs(): void {
  document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll<HTMLButtonElement>('.capability-pack-tab');
    const panels = document.querySelectorAll<HTMLElement>('.capability-panel');
    const firstEnabledTab = Array.from(tabs).find(tab => !tab.disabled);

    if (firstEnabledTab) {
      const pack = firstEnabledTab.getAttribute('data-pack');
      firstEnabledTab.classList.add('bg-rescue-600', 'font-semibold');
      firstEnabledTab.classList.remove('bg-slate-700');
      document.querySelector<HTMLElement>(`[data-panel="${pack}"]`)?.classList.remove('hidden');
    }

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        if (tab.disabled) return;

        const pack = tab.getAttribute('data-pack');

        tabs.forEach(item => {
          item.classList.remove('bg-rescue-600', 'font-semibold');
          item.classList.add('bg-slate-700');
        });

        tab.classList.add('bg-rescue-600', 'font-semibold');
        tab.classList.remove('bg-slate-700');

        panels.forEach(panel => panel.classList.add('hidden'));
        document.querySelector<HTMLElement>(`[data-panel="${pack}"]`)?.classList.remove('hidden');
      });
    });
  });
}

export function renderEscalationBanner(escalation: any, options: EscalationRenderOptions = {}): void {
  const contactRisk = escalation?.contact_continuity_risk || 'stable';

  if (options.contactRiskElementId) {
    const contactRiskEl = document.getElementById(options.contactRiskElementId);
    if (contactRiskEl) {
      const riskClasses: Record<string, string> = {
        stable: 'bg-green-900/40 text-green-300 border border-green-700',
        watch: 'bg-yellow-900/40 text-yellow-300 border border-yellow-700',
        high: 'bg-orange-900/40 text-orange-300 border border-orange-700',
        critical: 'bg-red-900/40 text-red-300 border border-red-700'
      };

      contactRiskEl.className = `font-semibold px-2 py-1 rounded text-sm ${riskClasses[contactRisk] || riskClasses.stable}`;
      contactRiskEl.textContent = String(contactRisk).toUpperCase();
    }
  }

  const bannerContainer = document.getElementById(options.containerId || 'escalation-banner-container');
  if (!bannerContainer) return;

  if (!escalation?.active) {
    bannerContainer.innerHTML = '';
    return;
  }

  const severity = escalation.severity || 'advisory';
  const severityClasses: Record<string, { container: string; icon: string; title: string; text: string }> = {
    critical: { container: 'bg-red-900/40 border-red-500', icon: 'text-red-400', title: 'text-red-200', text: 'text-red-100' },
    urgent: { container: 'bg-orange-900/40 border-orange-500', icon: 'text-orange-400', title: 'text-orange-200', text: 'text-orange-100' },
    warning: { container: 'bg-yellow-900/40 border-yellow-500', icon: 'text-yellow-400', title: 'text-yellow-200', text: 'text-yellow-100' },
    advisory: { container: 'bg-blue-900/40 border-blue-500', icon: 'text-blue-400', title: 'text-blue-200', text: 'text-blue-100' }
  };
  const riskBadgeClasses: Record<string, string> = {
    critical: 'bg-red-900/60 border-red-600 text-red-200',
    high: 'bg-orange-900/60 border-orange-600 text-orange-200',
    watch: 'bg-yellow-900/60 border-yellow-600 text-yellow-200'
  };
  const classes = severityClasses[severity] || severityClasses.advisory;
  const shouldPulse = severity === 'critical' || severity === 'urgent';

  bannerContainer.innerHTML = `
    <div class="rounded-lg border-2 p-4 mb-6 ${classes.container} ${shouldPulse ? 'animate-pulse' : ''}" role="alert" aria-live="assertive">
      <div class="flex items-start gap-3">
        <div class="flex-shrink-0 ${classes.icon}">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
        </div>
        <div class="flex-grow">
          <div class="flex items-center gap-2 mb-2">
            <h3 class="text-lg font-bold ${classes.title}">
              ${escapeHtml(String(severity).toUpperCase())}: Mission Escalation
            </h3>
            ${contactRisk && contactRisk !== 'stable'
              ? `<span class="text-xs px-2 py-1 rounded border ${riskBadgeClasses[contactRisk] || riskBadgeClasses.watch}">
                   Contact Risk: ${escapeHtml(String(contactRisk).toUpperCase())}
                 </span>`
              : ''}
          </div>
          ${escalation.reason ? `<p class="text-base ${classes.text} leading-relaxed">${escapeHtml(escalation.reason)}</p>` : ''}
          ${escalation.area_of_interest
            ? `<div class="mt-2 text-sm opacity-90">
                 <span class="font-semibold">Area of Interest:</span>
                 <span class="font-mono ml-1">${escapeHtml(escalation.area_of_interest)}</span>
               </div>`
            : ''}
        </div>
      </div>
    </div>
  `;
}
