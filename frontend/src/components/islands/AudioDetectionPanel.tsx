/**
 * AudioDetectionPanel - Audio/Voice Detection Monitoring & Playback
 * 
 * Displays audio detections (voice, tapping, knocking) with:
 * - Detection log with timestamps
 * - Simulated audio playback controls
 * - Confidence metrics and classification
 * - Human review flags for critical detections
 */
import { useState, useEffect } from 'react';

interface AudioDetection {
  id: string;
  agent_id: string;
  agent_name: string;
  detected_at: string;
  location: string;
  type: 'voice_like' | 'tapping' | 'knock' | 'ambient' | 'mechanical';
  confidence: number;
  frequency_range?: string;
  human_review_required: boolean;
  status: 'detected' | 'human_review_required' | 'reviewed' | 'false_positive';
  description: string;
  position?: {
    x_m: number;
    y_m: number;
    z_m: number;
  };
  timestamp_seconds: number;
}

interface AudioDetectionPanelProps {
  audioDetections: AudioDetection[];
}

function getTypeIcon(type: string): string {
  switch (type) {
    case 'voice_like': return '🗣️';
    case 'tapping': return '👆';
    case 'knock': return '🚪';
    case 'ambient': return '🌊';
    case 'mechanical': return '⚙️';
    default: return '🔊';
  }
}

function getTypeColor(type: string): string {
  switch (type) {
    case 'voice_like': return 'text-orange-400';
    case 'tapping': return 'text-yellow-400';
    case 'knock': return 'text-yellow-300';
    case 'ambient': return 'text-blue-400';
    case 'mechanical': return 'text-gray-400';
    default: return 'text-gray-400';
  }
}

function getTypeName(type: string): string {
  switch (type) {
    case 'voice_like': return 'Voice-Like';
    case 'tapping': return 'Tapping';
    case 'knock': return 'Knocking';
    case 'ambient': return 'Ambient';
    case 'mechanical': return 'Mechanical';
    default: return type;
  }
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'detected': return 'text-blue-400';
    case 'human_review_required': return 'text-orange-400';
    case 'reviewed': return 'text-green-400';
    case 'false_positive': return 'text-gray-500';
    default: return 'text-gray-400';
  }
}

function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return 'text-green-400';
  if (confidence >= 0.6) return 'text-yellow-400';
  if (confidence >= 0.4) return 'text-orange-400';
  return 'text-red-400';
}

function formatPosition(position?: { x_m: number; y_m: number; z_m: number }): string {
  if (!position) return 'Unknown';
  return `${position.x_m.toFixed(1)}m, ${position.y_m.toFixed(1)}m, ${position.z_m.toFixed(1)}m`;
}

export default function AudioDetectionPanel({ audioDetections: initialDetections }: AudioDetectionPanelProps) {
  const [audioDetections, setAudioDetections] = useState<AudioDetection[]>(initialDetections);
  const [selectedDetectionId, setSelectedDetectionId] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'time' | 'confidence' | 'type'>('time');

  // Listen for audio detection updates
  useEffect(() => {
    const handleUpdate = (event: CustomEvent) => {
      if (event.detail?.audio_detections) {
        setAudioDetections(event.detail.audio_detections);
      }
    };
    
    window.addEventListener('audio-detections-update', handleUpdate as EventListener);
    return () => window.removeEventListener('audio-detections-update', handleUpdate as EventListener);
  }, []);

  // Auto-select first high-confidence detection requiring review
  useEffect(() => {
    if (!selectedDetectionId && audioDetections.length > 0) {
      const criticalDetection = audioDetections.find(d => d.human_review_required && d.confidence >= 0.6);
      if (criticalDetection) {
        setSelectedDetectionId(criticalDetection.id);
      } else {
        setSelectedDetectionId(audioDetections[0].id);
      }
    }
  }, [audioDetections, selectedDetectionId]);

  // Simulate audio playback
  const handlePlayback = (detectionId: string) => {
    setIsPlaying(detectionId);
    // Simulate 3-second playback
    setTimeout(() => {
      setIsPlaying(null);
    }, 3000);
  };

  const sortedDetections = [...audioDetections].sort((a, b) => {
    switch (sortBy) {
      case 'time':
        return b.timestamp_seconds - a.timestamp_seconds; // Most recent first
      case 'confidence':
        return b.confidence - a.confidence; // Highest confidence first
      case 'type':
        return a.type.localeCompare(b.type);
      default:
        return 0;
    }
  });

  if (audioDetections.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <span className="text-gray-500">🔊</span>
          Audio Detections
        </h3>
        <p className="text-gray-400 text-sm">
          No audio detections recorded yet.
        </p>
        <p className="text-gray-500 text-xs mt-2">
          Waiting for microphone array data...
        </p>
      </div>
    );
  }

  const selectedDetection = sortedDetections.find(d => d.id === selectedDetectionId);
  const criticalCount = audioDetections.filter(d => d.human_review_required).length;
  const voiceCount = audioDetections.filter(d => d.type === 'voice_like').length;

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <span>🔊</span>
          Audio Detections
          <span className="text-sm text-gray-400">({audioDetections.length})</span>
        </h3>
        
        <div className="flex items-center gap-3">
          {voiceCount > 0 && (
            <div className="text-xs px-2 py-1 rounded bg-orange-900/30 text-orange-400 border border-orange-700">
              {voiceCount} Voice-Like
            </div>
          )}
          {criticalCount > 0 && (
            <div className="text-xs px-2 py-1 rounded bg-red-900/30 text-red-400 border border-red-700">
              {criticalCount} Need Review
            </div>
          )}
        </div>
      </div>

      {/* Sort Controls */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-gray-400">Sort by:</span>
        <button
          onClick={() => setSortBy('time')}
          className={`px-2 py-1 rounded ${
            sortBy === 'time'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          Time
        </button>
        <button
          onClick={() => setSortBy('confidence')}
          className={`px-2 py-1 rounded ${
            sortBy === 'confidence'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          Confidence
        </button>
        <button
          onClick={() => setSortBy('type')}
          className={`px-2 py-1 rounded ${
            sortBy === 'type'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          Type
        </button>
      </div>

      {/* Detection List */}
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {sortedDetections.map(detection => (
          <div
            key={detection.id}
            onClick={() => setSelectedDetectionId(detection.id)}
            className={`p-3 rounded border cursor-pointer transition-colors ${
              selectedDetectionId === detection.id
                ? 'bg-blue-900/30 border-blue-600'
                : 'bg-gray-900/50 border-gray-700 hover:border-gray-600'
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-start gap-2 flex-1">
                <span className="text-xl">{getTypeIcon(detection.type)}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`font-medium ${getTypeColor(detection.type)}`}>
                      {getTypeName(detection.type)}
                    </span>
                    <span className="text-xs text-gray-500">•</span>
                    <span className="text-xs text-gray-400">{detection.detected_at}</span>
                  </div>
                  <div className="text-xs text-gray-400 mb-1">
                    {detection.agent_name} • {detection.location}
                  </div>
                  {detection.human_review_required && (
                    <div className="text-xs text-orange-400 font-medium">
                      ⚠ Human Review Required
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex flex-col items-end gap-1">
                <div className={`text-sm font-semibold ${getConfidenceColor(detection.confidence)}`}>
                  {(detection.confidence * 100).toFixed(0)}%
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handlePlayback(detection.id);
                  }}
                  disabled={isPlaying === detection.id}
                  className={`text-xs px-2 py-1 rounded ${
                    isPlaying === detection.id
                      ? 'bg-green-700 text-white'
                      : 'bg-blue-600 hover:bg-blue-500 text-white'
                  }`}
                >
                  {isPlaying === detection.id ? '▶ Playing...' : '▶ Play'}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Selected Detection Details */}
      {selectedDetection && (
        <div className="border-t border-gray-700 pt-4 space-y-3">
          <h4 className="text-sm font-semibold text-white">Detection Details</h4>
          
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="text-gray-400 text-xs mb-1">Agent</div>
              <div className="text-white">{selectedDetection.agent_name}</div>
            </div>
            
            <div>
              <div className="text-gray-400 text-xs mb-1">Location</div>
              <div className="text-white">{selectedDetection.location}</div>
            </div>
            
            <div>
              <div className="text-gray-400 text-xs mb-1">Position</div>
              <div className="text-white text-xs">{formatPosition(selectedDetection.position)}</div>
            </div>
            
            <div>
              <div className="text-gray-400 text-xs mb-1">Frequency</div>
              <div className="text-white">{selectedDetection.frequency_range || 'Unknown'}</div>
            </div>
            
            <div className="col-span-2">
              <div className="text-gray-400 text-xs mb-1">Classification</div>
              <div className={`text-sm ${getStatusColor(selectedDetection.status)}`}>
                {selectedDetection.status.replace(/_/g, ' ').toUpperCase()}
              </div>
            </div>
            
            <div className="col-span-2">
              <div className="text-gray-400 text-xs mb-1">Description</div>
              <div className="text-white text-sm">{selectedDetection.description}</div>
            </div>
          </div>

          {/* Playback Controls */}
          <div className="bg-gray-900/50 rounded p-3 border border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Audio Playback (Simulated)</span>
              <span className="text-xs text-gray-500">
                Duration: {selectedDetection.type === 'voice_like' ? '2.4s' : '1.8s'}
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => handlePlayback(selectedDetection.id)}
                disabled={isPlaying === selectedDetection.id}
                className={`flex-1 py-2 rounded font-medium ${
                  isPlaying === selectedDetection.id
                    ? 'bg-green-700 text-white'
                    : 'bg-blue-600 hover:bg-blue-500 text-white'
                }`}
              >
                {isPlaying === selectedDetection.id ? '▶ Playing...' : '▶ Play Audio'}
              </button>
              
              <button
                className="px-3 py-2 rounded bg-gray-700 hover:bg-gray-600 text-white"
                title="Download audio file (simulated)"
              >
                💾
              </button>
              
              <button
                className="px-3 py-2 rounded bg-gray-700 hover:bg-gray-600 text-white"
                title="Export waveform"
              >
                📊
              </button>
            </div>

            {/* Simulated Waveform */}
            {isPlaying === selectedDetection.id && (
              <div className="mt-3 flex items-center justify-center gap-1 h-12">
                {[...Array(32)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 bg-green-500 rounded animate-pulse"
                    style={{
                      height: `${Math.random() * 40 + 20}%`,
                      animationDelay: `${i * 30}ms`
                    }}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Review Actions */}
          {selectedDetection.human_review_required && (
            <div className="flex gap-2">
              <button className="flex-1 py-2 rounded bg-green-600 hover:bg-green-500 text-white font-medium">
                ✓ Confirm Detection
              </button>
              <button className="flex-1 py-2 rounded bg-gray-600 hover:bg-gray-500 text-white font-medium">
                ✗ Mark False Positive
              </button>
            </div>
          )}

          {/* Simulation Notice */}
          <div className="text-xs text-gray-500 italic border-t border-gray-700 pt-2">
            ⚠ Audio playback is simulated. In a real deployment, actual audio files would be streamed or downloaded from the agent.
          </div>
        </div>
      )}
    </div>
  );
}
