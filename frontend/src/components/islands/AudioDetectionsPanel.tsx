import { useEffect, useState, useRef } from 'react';

interface AudioDetection {
  id: string;
  agent_id: string;
  agent_name: string;
  sensor_type: 'microphone' | 'audio_sensor' | 'hydrophone';
  audio_type: 'knocking' | 'tapping' | 'voice_like' | 'static' | 'ambient';
  status: 'detected' | 'analyzing' | 'human_review_required' | 'confirmed' | 'dismissed';
  mission_time: string;
  signal_quality: number;
  confidence: number;
  location_label: string;
  annotations: string[];
  description: string;
  audio_url?: string;
  spectrogram_url?: string;
}

interface AudioDetectionsPanelProps {
  missionId: string;
  audioDetections?: AudioDetection[];
}

export default function AudioDetectionsPanel({ missionId, audioDetections = [] }: AudioDetectionsPanelProps) {
  const [displayedDetections, setDisplayedDetections] = useState<AudioDetection[]>(audioDetections);
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string | null>(null);
  const audioRefs = useRef<{ [key: string]: HTMLAudioElement }>({});

  useEffect(() => {
    // Listen for audio detections updates from simulation
    const handleAudioDetectionsUpdate = (event: CustomEvent) => {
      if (event.detail && event.detail.audioDetections) {
        setDisplayedDetections(event.detail.audioDetections);
      }
    };

    window.addEventListener('audio-detections-update', handleAudioDetectionsUpdate as EventListener);

    return () => {
      window.removeEventListener('audio-detections-update', handleAudioDetectionsUpdate as EventListener);
      // Clean up audio elements
      Object.values(audioRefs.current).forEach(audio => {
        audio.pause();
        audio.src = '';
      });
    };
  }, []);

  // Helper function to get status badge color
  const getStatusBadgeColor = (status: AudioDetection['status']): string => {
    switch (status) {
      case 'detected':
        return 'bg-blue-900/40 text-blue-400 border-blue-600/50';
      case 'analyzing':
        return 'bg-yellow-900/40 text-yellow-400 border-yellow-600/50 animate-pulse';
      case 'human_review_required':
        return 'bg-red-900/50 text-red-300 border-red-500/70 animate-pulse';
      case 'confirmed':
        return 'bg-green-900/40 text-green-400 border-green-600/50';
      case 'dismissed':
        return 'bg-gray-900/40 text-gray-400 border-gray-600/50';
      default:
        return 'bg-gray-900/40 text-gray-400 border-gray-600/50';
    }
  };

  // Helper function to get audio type icon
  const getAudioTypeIcon = (audioType: AudioDetection['audio_type']): string => {
    switch (audioType) {
      case 'knocking':
        return '🔨';
      case 'tapping':
        return '👆';
      case 'voice_like':
        return '🗣️';
      case 'static':
        return '📡';
      case 'ambient':
        return '🌊';
      default:
        return '🎵';
    }
  };

  // Helper function to get audio type label
  const getAudioTypeLabel = (audioType: AudioDetection['audio_type']): string => {
    switch (audioType) {
      case 'knocking':
        return 'Knocking';
      case 'tapping':
        return 'Tapping Pattern';
      case 'voice_like':
        return 'Voice-Like Audio';
      case 'static':
        return 'Static/Interference';
      case 'ambient':
        return 'Ambient Sound';
      default:
        return 'Audio';
    }
  };

  // Play/pause audio
  const toggleAudioPlayback = (detectionId: string, audioUrl: string) => {
    const audio = audioRefs.current[detectionId];
    
    if (currentlyPlaying === detectionId) {
      // Pause current audio
      if (audio) {
        audio.pause();
      }
      setCurrentlyPlaying(null);
    } else {
      // Stop any currently playing audio
      if (currentlyPlaying && audioRefs.current[currentlyPlaying]) {
        audioRefs.current[currentlyPlaying].pause();
      }

      // Play new audio
      if (!audio) {
        const newAudio = new Audio(audioUrl);
        audioRefs.current[detectionId] = newAudio;
        newAudio.onended = () => setCurrentlyPlaying(null);
        newAudio.play();
      } else {
        audio.currentTime = 0;
        audio.play();
      }
      setCurrentlyPlaying(detectionId);
    }
  };

  if (!displayedDetections || displayedDetections.length === 0) {
    return (
      <div className="bg-gray-900/50 rounded-lg border border-gray-700/50 p-6">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
          Audio Detections
        </h2>
        <div className="text-gray-400 text-center py-8">
          <p className="text-sm">Listening for audio signatures...</p>
          <p className="text-xs text-gray-500 mt-2">Audio detections will appear when sensors detect sound patterns</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900/50 rounded-lg border border-gray-700/50 p-6">
      <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
        Audio Detections
        <span className="ml-auto text-sm font-normal text-gray-400">
          {displayedDetections.length} {displayedDetections.length === 1 ? 'detection' : 'detections'}
        </span>
      </h2>

      <div className="space-y-4">
        {displayedDetections.slice(-6).reverse().map((detection) => (
          <div
            key={detection.id}
            className="bg-black/40 rounded-lg border border-gray-700/70 p-4 hover:border-gray-600 transition-colors"
          >
            {/* Detection header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getAudioTypeIcon(detection.audio_type)}</span>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-white">{detection.agent_name}</span>
                    <span className="text-xs text-gray-500">•</span>
                    <span className="text-xs text-gray-400">{getAudioTypeLabel(detection.audio_type)}</span>
                  </div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    {detection.location_label} • {detection.mission_time}
                  </div>
                </div>
              </div>
              <div className={`px-2 py-0.5 rounded text-xs font-semibold border whitespace-nowrap ${getStatusBadgeColor(detection.status)}`}>
                {detection.status.replace(/_/g, ' ').toUpperCase()}
              </div>
            </div>

            {/* Description */}
            <p className="text-sm text-gray-300 mb-3">{detection.description}</p>

            {/* Audio player and spectrogram */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
              {/* Audio waveform placeholder / spectrogram */}
              {detection.spectrogram_url ? (
                <div className="aspect-video bg-black rounded border border-gray-700 overflow-hidden">
                  <img 
                    src={detection.spectrogram_url} 
                    alt="Audio spectrogram"
                    className="w-full h-full object-cover"
                  />
                </div>
              ) : (
                <div className="aspect-video bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 rounded border border-gray-700 flex items-center justify-center">
                  <div className="flex items-center gap-1">
                    {[...Array(20)].map((_, i) => (
                      <div
                        key={i}
                        className="w-1 bg-blue-500/50 rounded-full"
                        style={{
                          height: `${Math.random() * 40 + 20}px`,
                          animation: 'pulse 1s ease-in-out infinite',
                          animationDelay: `${i * 0.05}s`
                        }}
                      ></div>
                    ))}
                  </div>
                </div>
              )}

              {/* Audio playback control */}
              {detection.audio_url && (
                <div className="flex flex-col justify-center items-center gap-3 bg-gray-900/60 rounded border border-gray-700 p-4">
                  <button
                    onClick={() => toggleAudioPlayback(detection.id, detection.audio_url!)}
                    className={`p-4 rounded-full transition-colors ${
                      currentlyPlaying === detection.id
                        ? 'bg-red-600 hover:bg-red-700'
                        : 'bg-blue-600 hover:bg-blue-700'
                    }`}
                    title={currentlyPlaying === detection.id ? 'Stop audio' : 'Play audio'}
                  >
                    {currentlyPlaying === detection.id ? (
                      <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                      </svg>
                    ) : (
                      <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z" />
                      </svg>
                    )}
                  </button>
                  <div className="text-center">
                    <p className="text-xs text-gray-400">
                      {currentlyPlaying === detection.id ? 'Playing...' : 'Click to play'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">Generated audio sample</p>
                  </div>
                </div>
              )}
            </div>

            {/* Signal quality and confidence */}
            <div className="grid grid-cols-2 gap-4 mb-3">
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500 w-20">Signal:</span>
                <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      detection.signal_quality >= 70
                        ? 'bg-green-500'
                        : detection.signal_quality >= 40
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${detection.signal_quality}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-400 w-10 text-right">{detection.signal_quality}%</span>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500 w-20">Confidence:</span>
                <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      detection.confidence >= 75
                        ? 'bg-green-500'
                        : detection.confidence >= 50
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${detection.confidence}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-400 w-10 text-right">{detection.confidence}%</span>
              </div>
            </div>

            {/* Annotations */}
            {detection.annotations && detection.annotations.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {detection.annotations.map((annotation, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-0.5 bg-gray-800/60 text-gray-300 text-xs rounded border border-gray-700"
                  >
                    {annotation}
                  </span>
                ))}
              </div>
            )}

            {/* Critical warning border for human review */}
            {detection.status === 'human_review_required' && (
              <div className="absolute inset-0 border-2 border-red-500 rounded-lg animate-pulse pointer-events-none"></div>
            )}
          </div>
        ))}
      </div>

      {displayedDetections.length > 6 && (
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Showing most recent 6 of {displayedDetections.length} detections
          </p>
        </div>
      )}
    </div>
  );
}
