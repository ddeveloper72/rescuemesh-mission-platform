/**
 * Detection Modal Manager
 * 
 * Bridges tactical map detection markers with actual detection data
 * from audio detections, media feeds, and other sensor systems.
 */

import type { MissionSimulationState } from '../types/simulation';

interface DetectionDetail {
  id: string;
  type: 'thermal' | 'audio' | 'gas' | 'electrical' | 'pressure';
  label: string;
  description?: string;
  agent_name?: string;
  location_label?: string;
  mission_time?: string;
  confidence?: number;
  signal_quality?: number;
  audio_url?: string;
  spectrogram_url?: string;
  preview_url?: string;
  annotations?: string[];
}

// Mapping between map detection markers and data sources
const DETECTION_MAPPING: Record<string, { source: 'audio' | 'media' | 'sensor', matchKey?: string }> = {
  // Collapsed Building Search
  'thermal-void': { source: 'media', matchKey: 'thermal' },
  'audio-voice': { source: 'audio', matchKey: 'voice' },
  
  // Cave Rescue
  'audio-deep-squeeze': { source: 'audio', matchKey: 'voice' },
  
  // Industrial Inspection
  'thermal-hotspot': { source: 'media', matchKey: 'thermal' },
  'gas-leak': { source: 'sensor' },
};

let currentState: MissionSimulationState | null = null;

/**
 * Initialize the detection modal manager
 */
export function initDetectionModalManager() {
  // Listen for map detection marker clicks
  window.addEventListener('detection-marker-clicked', (event: Event) => {
    const customEvent = event as CustomEvent;
    const { detectionId, detectionType } = customEvent.detail;
    
    console.log('Detection marker clicked:', detectionId, detectionType);
    
    const detectionDetail = findDetectionDetail(detectionId, detectionType);
    
    if (detectionDetail) {
      console.log('Found detection detail, dispatching show-detection-modal:', detectionDetail);
      // Dispatch event to open modal with detection details
      window.dispatchEvent(new CustomEvent('show-detection-modal', {
        detail: {
          detection: detectionDetail
        }
      }));
    } else {
      console.warn(`No detection detail found for marker: ${detectionId}`);
    }
  });
}

/**
 * Update current mission state (called by simulation manager)
 */
export function updateDetectionData(state: MissionSimulationState) {
  currentState = state;
}

/**
 * Find detection detail from current state data
 */
function findDetectionDetail(detectionId: string, detectionType: string): DetectionDetail | null {
  if (!currentState) return null;
  
  const mapping = DETECTION_MAPPING[detectionId];
  
  if (!mapping) {
    // Create a generic detection detail
    return {
      id: detectionId,
      type: detectionType as any,
      label: detectionId.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      description: 'Detection details not available'
    };
  }
  
  // Look in audio detections
  if (mapping.source === 'audio' && currentState.audio_detections) {
    const matchKey = mapping.matchKey?.toLowerCase();
    const audioDetection = currentState.audio_detections.find(det => 
      matchKey ? det.audio_type.toLowerCase().includes(matchKey) : false
    );
    
    if (audioDetection) {
      return {
        id: audioDetection.id,
        type: 'audio',
        label: audioDetection.audio_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) + ' Detection',
        description: audioDetection.description,
        agent_name: audioDetection.agent_name,
        location_label: audioDetection.location_label,
        mission_time: audioDetection.mission_time,
        confidence: audioDetection.confidence,
        signal_quality: audioDetection.signal_quality,
        audio_url: audioDetection.audio_url,
        spectrogram_url: audioDetection.spectrogram_url,
        annotations: audioDetection.annotations,
      };
    }
  }
  
  // Look in media feeds
  if (mapping.source === 'media' && currentState.media_feeds) {
    const matchKey = mapping.matchKey?.toLowerCase();
    const mediaFeed = currentState.media_feeds.find(feed => 
      matchKey ? feed.sensor_type.toLowerCase().includes(matchKey) || 
                 feed.frame_type?.toLowerCase().includes(matchKey) : false
    );
    
    if (mediaFeed) {
      return {
        id: mediaFeed.frame_id,
        type: 'thermal',
        label: mediaFeed.frame_type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Thermal Detection',
        description: mediaFeed.description || undefined,
        agent_name: mediaFeed.agent_name,
        location_label: mediaFeed.location_label,
        mission_time: mediaFeed.mission_time,
        confidence: mediaFeed.confidence,
        signal_quality: mediaFeed.signal_quality,
        preview_url: mediaFeed.preview_url,
        annotations: mediaFeed.annotations,
      };
    }
  }
  
  // Generic fallback
  return {
    id: detectionId,
    type: detectionType as any,
    label: detectionId.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    description: 'Detection captured by mission sensors'
  };
}
