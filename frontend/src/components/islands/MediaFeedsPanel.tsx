import { useEffect, useState } from 'react';
import type { MediaFrame } from '../../types/simulation';

interface MediaFeedsPanelProps {
  mediaFeeds?: MediaFrame[];
}

export default function MediaFeedsPanel({ mediaFeeds: initialMediaFeeds = [] }: MediaFeedsPanelProps) {
  const [displayedFeeds, setDisplayedFeeds] = useState<MediaFrame[]>(initialMediaFeeds);

  useEffect(() => {
    console.log('[MediaFeedsPanel] Component mounted, listening for media-feeds-update events');
    
    // Listen for media feeds updates from simulation
    const handleMediaFeedsUpdate = (event: CustomEvent) => {
      console.log('[MediaFeedsPanel] Received media-feeds-update event:', event.detail);
      if (event.detail && event.detail.mediaFeeds) {
        console.log(`[MediaFeedsPanel] Updating with ${event.detail.mediaFeeds.length} feeds`);
        setDisplayedFeeds(event.detail.mediaFeeds);
      }
    };

    window.addEventListener('media-feeds-update', handleMediaFeedsUpdate as EventListener);

    return () => {
      console.log('[MediaFeedsPanel] Component unmounting, removing event listener');
      window.removeEventListener('media-feeds-update', handleMediaFeedsUpdate as EventListener);
    };
  }, []);

  // Helper function to get status badge color
  const getStatusBadgeColor = (status: MediaFrame['status']): string => {
    switch (status) {
      case 'live':
        return 'bg-green-900/40 text-green-400 border-green-600/50';
      case 'degraded':
        return 'bg-yellow-900/40 text-yellow-400 border-yellow-600/50';
      case 'delayed':
        return 'bg-orange-900/40 text-orange-400 border-orange-600/50';
      case 'lost':
        return 'bg-red-900/40 text-red-400 border-red-600/50';
      case 'last_good_frame':
        return 'bg-gray-900/40 text-gray-400 border-gray-600/50';
      case 'thermal_detection':
        return 'bg-purple-900/40 text-purple-400 border-purple-600/50';
      case 'ai_flagged':
        return 'bg-blue-900/40 text-blue-400 border-blue-600/50';
      case 'human_review_required':
        return 'bg-red-900/50 text-red-300 border-red-500/70 animate-pulse';
      default:
        return 'bg-gray-900/40 text-gray-400 border-gray-600/50';
    }
  };

  // Helper function to get sensor type icon/label
  const getSensorTypeLabel = (sensorType: MediaFrame['sensor_type']): string => {
    switch (sensorType) {
      case 'rgb_camera':
        return 'RGB';
      case 'low_light_camera':
        return 'Low-Light';
      case 'thermal_camera':
        return 'Thermal';
      case 'inspection_camera':
        return 'Inspection';
      case 'underwater_camera':
        return 'Underwater';
      case 'hazard_camera':
        return 'Hazard';
      default:
        return 'Camera';
    }
  };

  // Helper function to render frame (actual image or simulated placeholder)
  const renderFrame = (frame: MediaFrame) => {
    const isDegraded = frame.status === 'degraded' || frame.status === 'delayed' || frame.signal_quality < 60;
    const isThermal = frame.sensor_type === 'thermal_camera' || frame.frame_type === 'thermal';
    const isUnderwater = frame.sensor_type === 'underwater_camera';
    const isLastGoodFrame = frame.status === 'last_good_frame';

    // If we have a real image URL, display it
    if (frame.media_url || frame.thumbnail_url) {
      const imageUrl = frame.thumbnail_url || frame.media_url;
      return (
        <div className="relative aspect-video w-full bg-black rounded-md overflow-hidden border border-gray-700">
          <img 
            src={imageUrl} 
            alt={frame.description}
            className={`w-full h-full object-cover ${isDegraded ? 'opacity-70' : ''}`}
            loading="lazy"
          />
          
          {/* Degradation effects overlay */}
          {isDegraded && (
            <div className="absolute inset-0">
              {/* Scanlines */}
              <div className="absolute inset-0 opacity-20"
                   style={{
                     backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.1) 2px, rgba(255,255,255,0.1) 4px)'
                   }}>
              </div>
            </div>
          )}

          {/* Last good frame timestamp overlay */}
          {isLastGoodFrame && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="bg-black/70 px-4 py-2 rounded border border-gray-600">
                <p className="text-gray-300 text-sm font-mono">LAST GOOD FRAME</p>
                <p className="text-gray-500 text-xs font-mono">{frame.mission_time}</p>
              </div>
            </div>
          )}

          {/* Frame metadata overlay */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
            <div className="flex items-center justify-between text-xs text-gray-300 font-mono">
              <span>{frame.location_label}</span>
              <span>{frame.mission_time}</span>
            </div>
          </div>

          {/* Confidence indicator */}
          <div className="absolute top-2 right-2 bg-black/70 px-2 py-1 rounded text-xs font-mono">
            <span className={frame.confidence >= 75 ? 'text-green-400' : frame.confidence >= 50 ? 'text-yellow-400' : 'text-red-400'}>
              {Math.round(frame.confidence * 100)}% conf
            </span>
          </div>
        </div>
      );
    }

    // Otherwise render simulated placeholder
    // Base gradient for different frame types
    let gradientClass = 'from-gray-800 via-gray-700 to-gray-800';
    if (isThermal) {
      gradientClass = 'from-red-900/30 via-orange-800/30 to-yellow-700/30';
    } else if (isUnderwater) {
      gradientClass = 'from-blue-900/40 via-cyan-800/40 to-teal-800/40';
    } else if (isLastGoodFrame) {
      gradientClass = 'from-gray-900/60 via-gray-800/60 to-gray-900/60';
    }

    return (
      <div className="relative aspect-video w-full bg-black rounded-md overflow-hidden border border-gray-700">
        {/* Simulated image background */}
        <div className={`absolute inset-0 bg-gradient-to-br ${gradientClass}`}>
          {/* Simulated geometric patterns */}
          <svg className="absolute inset-0 w-full h-full opacity-20" viewBox="0 0 400 300">
            <rect x="50" y="50" width="100" height="80" fill="currentColor" className="text-white/10" />
            <circle cx="300" cy="200" r="60" fill="currentColor" className="text-white/10" />
            <polygon points="200,100 250,180 150,180" fill="currentColor" className="text-white/10" />
          </svg>

          {/* Thermal color overlay for thermal frames */}
          {isThermal && (
            <div className="absolute inset-0 opacity-40">
              <div className="absolute top-1/3 left-1/2 w-20 h-20 bg-red-500 rounded-full blur-xl"></div>
              <div className="absolute top-2/3 left-1/4 w-16 h-16 bg-orange-400 rounded-full blur-lg"></div>
              <div className="absolute top-1/2 right-1/3 w-12 h-12 bg-yellow-300 rounded-full blur-md"></div>
            </div>
          )}

          {/* Underwater turbidity effect */}
          {isUnderwater && (
            <div className="absolute inset-0 bg-blue-600/20 backdrop-blur-[1px]">
              <div className="absolute top-1/4 left-1/3 w-24 h-24 bg-cyan-300/10 rounded-full blur-2xl"></div>
            </div>
          )}

          {/* Degradation effects */}
          {isDegraded && (
            <div className="absolute inset-0">
              {/* Noise/static pattern */}
              <div className="absolute inset-0 opacity-30 mix-blend-overlay">
                <svg className="w-full h-full">
                  <filter id="noise">
                    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" />
                  </filter>
                  <rect width="100%" height="100%" filter="url(#noise)" />
                </svg>
              </div>
              {/* Scanlines */}
              <div className="absolute inset-0 opacity-20"
                   style={{
                     backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.1) 2px, rgba(255,255,255,0.1) 4px)'
                   }}>
              </div>
            </div>
          )}

          {/* Last good frame timestamp overlay */}
          {isLastGoodFrame && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="bg-black/70 px-4 py-2 rounded border border-gray-600">
                <p className="text-gray-300 text-sm font-mono">LAST GOOD FRAME</p>
                <p className="text-gray-500 text-xs font-mono">{frame.mission_time}</p>
              </div>
            </div>
          )}

          {/* Frame metadata overlay */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
            <div className="flex items-center justify-between text-xs text-gray-300 font-mono">
              <span>{frame.location_label}</span>
              <span>{frame.mission_time}</span>
            </div>
          </div>

          {/* Confidence indicator */}
          <div className="absolute top-2 right-2 bg-black/70 px-2 py-1 rounded text-xs font-mono">
            <span className={frame.confidence >= 75 ? 'text-green-400' : frame.confidence >= 50 ? 'text-yellow-400' : 'text-red-400'}>
              {frame.confidence}% conf
            </span>
          </div>
        </div>

        {/* Critical warning border for human review */}
        {frame.status === 'human_review_required' && (
          <div className="absolute inset-0 border-4 border-red-500 animate-pulse pointer-events-none"></div>
        )}
      </div>
    );
  };

  if (!displayedFeeds || displayedFeeds.length === 0) {
    return (
      <div className="bg-gray-900/50 rounded-lg border border-gray-700/50 p-6">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          Visual Media Feeds
        </h2>
        <div className="text-gray-400 text-center py-8">
          <p className="text-sm">Awaiting first media return from active agents...</p>
          <p className="text-xs text-gray-500 mt-2">Camera feeds will appear as agents begin imaging</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900/50 rounded-lg border border-gray-700/50 p-6">
      <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        Visual Media Feeds
        <span className="ml-auto text-sm font-normal text-gray-400">
          {displayedFeeds.length} {displayedFeeds.length === 1 ? 'frame' : 'frames'}
        </span>
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {displayedFeeds.slice(-6).reverse().map((frame) => (
          <div
            key={frame.frame_id}
            className="bg-black/40 rounded-lg border border-gray-700/70 p-4 hover:border-gray-600 transition-colors"
          >
            {/* Frame header */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-white">{frame.agent_name}</span>
                <span className="text-xs text-gray-500">•</span>
                <span className="text-xs text-gray-400">{getSensorTypeLabel(frame.sensor_type)}</span>
              </div>
              <div className={`px-2 py-0.5 rounded text-xs font-semibold border ${getStatusBadgeColor(frame.status)}`}>
                {frame.status.replace(/_/g, ' ').toUpperCase()}
              </div>
            </div>

            {/* Frame image or placeholder */}
            {renderFrame(frame)}

            {/* Frame details */}
            <div className="mt-3 space-y-2">
              <p className="text-sm text-gray-300">{frame.description}</p>

              {/* Signal quality bar */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500 w-16">Signal:</span>
                <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      frame.signal_quality >= 70
                        ? 'bg-green-500'
                        : frame.signal_quality >= 40
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${frame.signal_quality}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-400 w-10 text-right">{frame.signal_quality}%</span>
              </div>

              {/* Annotations */}
              {frame.annotations && frame.annotations.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {frame.annotations.map((annotation, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 bg-gray-800/60 text-gray-300 text-xs rounded border border-gray-700"
                    >
                      {annotation}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {displayedFeeds.length > 6 && (
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Showing most recent 6 of {displayedFeeds.length} frames
          </p>
        </div>
      )}
    </div>
  );
}
