import { useEffect, useState, useRef } from 'react';
import { API_BASE_URL } from '../../config/api';

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

export default function DetectionDetailModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [detection, setDetection] = useState<DetectionDetail | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Listen for detection modal show events
    const handleDetectionClick = (event: CustomEvent) => {
      console.log('show-detection-modal event received:', event.detail);
      if (event.detail && event.detail.detection) {
        setDetection(event.detail.detection);
        setIsOpen(true);
        setIsPlaying(false);
      }
    };

    window.addEventListener('show-detection-modal', handleDetectionClick as EventListener);

    return () => {
      window.removeEventListener('show-detection-modal', handleDetectionClick as EventListener);
      // Clean up audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = '';
      }
    };
  }, []);

  const closeModal = () => {
    setIsOpen(false);
    setIsPlaying(false);
    if (audioRef.current) {
      audioRef.current.pause();
    }
  };

  const toggleAudio = () => {
    if (!detection?.audio_url) return;

    const fullAudioUrl = detection.audio_url.startsWith('http') 
      ? detection.audio_url 
      : `${API_BASE_URL}${detection.audio_url}`;

    if (isPlaying) {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      setIsPlaying(false);
    } else {
      if (!audioRef.current) {
        const audio = new Audio(fullAudioUrl);
        audioRef.current = audio;
        audio.onended = () => setIsPlaying(false);
        audio.play();
      } else {
        audioRef.current.currentTime = 0;
        audioRef.current.play();
      }
      setIsPlaying(true);
    }
  };

  const getTypeColor = (type: string): string => {
    switch (type) {
      case 'thermal': return 'text-red-400 border-red-600/50 bg-red-900/40';
      case 'audio': return 'text-purple-400 border-purple-600/50 bg-purple-900/40';
      case 'gas': return 'text-yellow-400 border-yellow-600/50 bg-yellow-900/40';
      case 'electrical': return 'text-blue-400 border-blue-600/50 bg-blue-900/40';
      case 'pressure': return 'text-cyan-400 border-cyan-600/50 bg-cyan-900/40';
      default: return 'text-gray-400 border-gray-600/50 bg-gray-900/40';
    }
  };

  const getTypeIcon = (type: string): JSX.Element => {
    switch (type) {
      case 'thermal':
        return (
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
          </svg>
        );
      case 'audio':
        return (
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
          </svg>
        );
      case 'gas':
        return (
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
          </svg>
        );
      default:
        return (
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        );
    }
  };

  if (!isOpen || !detection) return null;

  const fullSpectrogramUrl = detection.spectrogram_url?.startsWith('http')
    ? detection.spectrogram_url
    : detection.spectrogram_url ? `${API_BASE_URL}${detection.spectrogram_url}` : undefined;

  const fullPreviewUrl = detection.preview_url?.startsWith('http')
    ? detection.preview_url
    : detection.preview_url ? `${API_BASE_URL}${detection.preview_url}` : undefined;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/70 z-40 backdrop-blur-sm"
        onClick={closeModal}
      />

      {/* Modal */}
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="bg-slate-800 rounded-lg border border-slate-700 max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
          {/* Header */}
          <div className="flex items-start justify-between p-6 border-b border-slate-700">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-lg border ${getTypeColor(detection.type)}`}>
                {getTypeIcon(detection.type)}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{detection.label}</h2>
                <p className="text-slate-400 text-sm mt-1">
                  {detection.type.charAt(0).toUpperCase() + detection.type.slice(1)} Detection
                </p>
              </div>
            </div>
            <button
              onClick={closeModal}
              className="text-slate-400 hover:text-white transition-colors p-2 hover:bg-slate-700 rounded"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Metadata */}
            {(detection.agent_name || detection.location_label || detection.mission_time) && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                {detection.agent_name && (
                  <div>
                    <div className="text-slate-500 mb-1">Agent</div>
                    <div className="text-white font-semibold">{detection.agent_name}</div>
                  </div>
                )}
                {detection.location_label && (
                  <div>
                    <div className="text-slate-500 mb-1">Location</div>
                    <div className="text-white font-semibold">{detection.location_label}</div>
                  </div>
                )}
                {detection.mission_time && (
                  <div>
                    <div className="text-slate-500 mb-1">Mission Time</div>
                    <div className="text-white font-semibold">{detection.mission_time}</div>
                  </div>
                )}
              </div>
            )}

            {/* Quality metrics */}
            {(detection.confidence !== undefined || detection.signal_quality !== undefined) && (
              <div className="grid grid-cols-2 gap-4">
                {detection.confidence !== undefined && (
                  <div>
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-slate-400">Confidence</span>
                      <span className="text-white font-semibold">{detection.confidence}%</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-500 rounded-full transition-all"
                        style={{ width: `${detection.confidence}%` }}
                      />
                    </div>
                  </div>
                )}
                {detection.signal_quality !== undefined && (
                  <div>
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-slate-400">Signal Quality</span>
                      <span className="text-white font-semibold">{detection.signal_quality}%</span>
                    </div>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-green-500 rounded-full transition-all"
                        style={{ width: `${detection.signal_quality}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Description */}
            {detection.description && (
              <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                <p className="text-slate-200">{detection.description}</p>
              </div>
            )}

            {/* Audio playback for audio detections */}
            {detection.type === 'audio' && detection.audio_url && (
              <div className="space-y-4">
                {fullSpectrogramUrl && (
                  <div className="aspect-video bg-black rounded-lg border border-slate-700 overflow-hidden">
                    <img 
                      src={fullSpectrogramUrl} 
                      alt="Audio spectrogram"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
                <div className="flex items-center justify-center gap-4 bg-slate-900/50 rounded-lg p-6 border border-slate-700">
                  <button
                    onClick={toggleAudio}
                    className={`p-4 rounded-full transition-colors ${
                      isPlaying
                        ? 'bg-red-600 hover:bg-red-700'
                        : 'bg-purple-600 hover:bg-purple-700'
                    }`}
                    title={isPlaying ? 'Stop audio' : 'Play audio'}
                  >
                    {isPlaying ? (
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
                    <p className="text-white font-semibold">
                      {isPlaying ? 'Playing audio...' : 'Click to play audio'}
                    </p>
                    <p className="text-slate-400 text-sm mt-1">Field-captured audio sample</p>
                  </div>
                </div>
              </div>
            )}

            {/* Image preview for visual detections */}
            {detection.type === 'thermal' && fullPreviewUrl && (
              <div className="aspect-video bg-black rounded-lg border border-slate-700 overflow-hidden">
                <img 
                  src={fullPreviewUrl} 
                  alt="Detection preview"
                  className="w-full h-full object-cover"
                />
              </div>
            )}

            {/* Annotations */}
            {detection.annotations && detection.annotations.length > 0 && (
              <div>
                <div className="text-slate-400 text-sm mb-2">Annotations</div>
                <div className="flex flex-wrap gap-2">
                  {detection.annotations.map((annotation, index) => (
                    <span 
                      key={index}
                      className="px-3 py-1 bg-slate-700 text-slate-300 rounded-full text-sm border border-slate-600"
                    >
                      {annotation}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 bg-slate-900/50 border-t border-slate-700 flex justify-end">
            <button
              onClick={closeModal}
              className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors font-semibold"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
