/**
 * TalkbackPanel - Two-Way Survivor Communication Interface
 * 
 * Simulates operator ability to send audio messages through deployed agents
 * and monitor for survivor responses. 
 * 
 * SIMULATION ONLY - Not real survivor contact. Human review required.
 */
import { useState, useEffect } from 'react';

interface TalkbackAgent {
  agent_id: string;
  name: string;
  has_speaker: boolean;
  has_microphone: boolean;
}

interface TalkbackMessage {
  id: string;
  agent_id: string;
  agent_name: string;
  sent_at_seconds: number;
  timestamp: string;
  location: string;
  message: string;
  audio_link_quality: number;
  delivery_status: string;
  response_expected: boolean;
  response_window_seconds: number;
}

interface TalkbackResponse {
  id: string;
  detected_at_seconds: number;
  timestamp: string;
  location: string;
  original_message_at: number;
  response_type: string;
  tap_count?: number;
  confidence: number;
  requires_human_review: boolean;
  transcript: string;
  description: string;
}

interface TalkbackCapability {
  talkback_available: boolean;
  speaker_available: boolean;
  microphone_available: boolean;
  available_agents: TalkbackAgent[];
}

interface TalkbackData {
  capability: TalkbackCapability;
  messages: TalkbackMessage[];
  responses: TalkbackResponse[];
}

interface TalkbackPanelProps {
  talkbackData: TalkbackData | null;
}

const MESSAGE_PRESETS = [
  "If you can hear me, tap three times.",
  "Stay calm. Help is on the way.",
  "Can you move or respond?",
  "We are trying to maintain contact.",
  "Emergency services are approaching your location.",
  "Do not move if you are injured.",
];

export default function TalkbackPanel({ talkbackData: initialData }: TalkbackPanelProps) {
  const [talkbackData, setTalkbackData] = useState<TalkbackData | null>(initialData);
  const [selectedAgentId, setSelectedAgentId] = useState<string>('');
  const [selectedMessage, setSelectedMessage] = useState<string>(MESSAGE_PRESETS[0]);
  const [isCustomMessage, setIsCustomMessage] = useState(false);
  const [customMessage, setCustomMessage] = useState('');

  // Listen for talkback updates
  useEffect(() => {
    const handleUpdate = (event: CustomEvent) => {
      if (event.detail?.talkbackData) {
        setTalkbackData(event.detail.talkbackData);
      }
    };
    
    window.addEventListener('talkback-update', handleUpdate as EventListener);
    return () => window.removeEventListener('talkback-update', handleUpdate as EventListener);
  }, []);

  // Auto-select first available agent
  useEffect(() => {
    if (talkbackData?.capability.available_agents.length > 0 && !selectedAgentId) {
      setSelectedAgentId(talkbackData.capability.available_agents[0].agent_id);
    }
  }, [talkbackData, selectedAgentId]);

  if (!talkbackData || !talkbackData.capability.talkback_available) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <span className="text-yellow-500">⚠</span>
          Talkback Communication Unavailable
        </h3>
        <p className="text-gray-400 text-sm">
          No agents with speaker/microphone capability deployed.
        </p>
      </div>
    );
  }

  const selectedAgent = talkbackData.capability.available_agents.find(
    a => a.agent_id === selectedAgentId
  );

  const lastMessage = talkbackData.messages.length > 0 
    ? talkbackData.messages[talkbackData.messages.length - 1]
    : null;

  const recentResponses = talkbackData.responses.filter(
    r => lastMessage && r.original_message_at === lastMessage.sent_at_seconds
  );

  const handleSendMessage = () => {
    // Simulation only - no real action taken
    console.log('[TalkbackPanel] Simulating message send:', {
      agent: selectedAgentId,
      message: isCustomMessage ? customMessage : selectedMessage,
    });
    alert('Simulation only: Message would be sent to agent speaker system. Human authorization required for real deployment.');
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
        <span className="text-blue-400">📢</span>
        Talkback Communication
      </h3>

      {/* Agent Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Available Agents
        </label>
        <select
          value={selectedAgentId}
          onChange={(e) => setSelectedAgentId(e.target.value)}
          className="w-full bg-gray-700 text-white border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {talkbackData.capability.available_agents.map(agent => (
            <option key={agent.agent_id} value={agent.agent_id}>
              {agent.name} {agent.has_speaker ? '🔊' : ''} {agent.has_microphone ? '🎤' : ''}
            </option>
          ))}
        </select>
        {selectedAgent && (
          <p className="text-xs text-gray-400 mt-1">
            Capability: 
            {selectedAgent.has_speaker && ' Speaker'}
            {selectedAgent.has_microphone && ' Microphone'}
          </p>
        )}
      </div>

      {/* Message Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Message
        </label>
        {!isCustomMessage ? (
          <div className="space-y-2">
            <select
              value={selectedMessage}
              onChange={(e) => setSelectedMessage(e.target.value)}
              className="w-full bg-gray-700 text-white border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {MESSAGE_PRESETS.map((preset, index) => (
                <option key={index} value={preset}>
                  {preset}
                </option>
              ))}
            </select>
            <button
              onClick={() => setIsCustomMessage(true)}
              className="text-sm text-blue-400 hover:text-blue-300"
            >
              Custom Message...
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <textarea
              value={customMessage}
              onChange={(e) => setCustomMessage(e.target.value)}
              placeholder="Enter custom message..."
              rows={3}
              className="w-full bg-gray-700 text-white border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => setIsCustomMessage(false)}
              className="text-sm text-blue-400 hover:text-blue-300"
            >
              Use Preset
            </button>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={handleSendMessage}
          disabled={!selectedAgentId || (!selectedAgent?.has_speaker)}
          className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded transition-colors"
        >
          ● Push to Talk
        </button>
        <button
          disabled={!selectedAgentId || (!selectedAgent?.has_microphone)}
          className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded transition-colors"
        >
          Listen for Response
        </button>
      </div>

      {/* Last Message Status */}
      {lastMessage && (
        <div className="bg-gray-700 rounded p-3 mb-3">
          <p className="text-sm text-gray-300 mb-1">
            <span className="font-medium">Status:</span> Message sent at {lastMessage.timestamp}
          </p>
          <p className="text-sm text-gray-300 mb-1">
            <span className="font-medium">Location:</span> {lastMessage.location}
          </p>
          <p className="text-sm text-gray-300 mb-1">
            <span className="font-medium">Audio Link Quality:</span> 
            <span className="ml-2 inline-flex items-center">
              <span className="inline-block w-32 bg-gray-600 rounded-full h-2 mr-2">
                <span 
                  className="block bg-green-500 h-2 rounded-full" 
                  style={{ width: `${lastMessage.audio_link_quality * 100}%` }}
                />
              </span>
              {Math.round(lastMessage.audio_link_quality * 100)}%
            </span>
          </p>
          <p className="text-sm text-gray-300">
            <span className="font-medium">Delivery:</span> 
            <span className={`ml-2 ${
              lastMessage.delivery_status === 'delivered' ? 'text-green-400' : 
              lastMessage.delivery_status === 'degraded' ? 'text-yellow-400' : 
              'text-red-400'
            }`}>
              {lastMessage.delivery_status === 'delivered' && '✓ '}
              {lastMessage.delivery_status.charAt(0).toUpperCase() + lastMessage.delivery_status.slice(1)}
            </span>
          </p>
        </div>
      )}

      {/* Responses */}
      {recentResponses.length > 0 && (
        <div className="bg-green-900 bg-opacity-30 border border-green-700 rounded p-3 mb-3">
          <h4 className="text-sm font-semibold text-green-400 mb-2">
            ✓ Response Detected
          </h4>
          {recentResponses.map(response => (
            <div key={response.id} className="text-sm mb-2">
              <p className="text-gray-200">
                <span className="font-medium">Time:</span> {response.timestamp}
              </p>
              <p className="text-gray-200">
                <span className="font-medium">Type:</span> {response.response_type}
                {response.tap_count && ` (${response.tap_count} taps)`}
              </p>
              <p className="text-gray-200">
                <span className="font-medium">Confidence:</span> {Math.round(response.confidence * 100)}%
              </p>
              <p className="text-gray-300 italic mt-1">
                {response.transcript}
              </p>
              {response.requires_human_review && (
                <p className="text-yellow-400 mt-1 text-xs font-medium">
                  ⚠ Human review required
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Safety Warning */}
      <div className="bg-yellow-900 bg-opacity-20 border border-yellow-700 rounded p-3">
        <p className="text-xs text-yellow-200">
          ⚠ <strong>Simulation only.</strong> Not real survivor contact. 
          All detections require human review and authorized rescue communications protocols.
        </p>
      </div>
    </div>
  );
}
