import { useHealthStatus } from '@/store/deviceStore';
import { useConnectionStatus } from '@/hooks/useWebSocket';

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export default function Header({ 
  title = "Machine Control Panel", 
  subtitle = "IoT Device Dashboard" 
}: HeaderProps) {
  const health = useHealthStatus();
  const { status, reconnectAttempts } = useConnectionStatus();

  // Determine connection status and styling
  const getConnectionStatus = () => {
    switch (status) {
      case 'connected':
        return {
          color: 'bg-green-400',
          text: 'Connected',
          textColor: 'text-green-600'
        };
      case 'connecting':
        return {
          color: 'bg-yellow-400',
          text: reconnectAttempts ? `Reconnecting... (${reconnectAttempts})` : 'Connecting...',
          textColor: 'text-yellow-600'
        };
      case 'error':
        return {
          color: 'bg-red-400',
          text: 'Connection Error',
          textColor: 'text-red-600'
        };
      default:
        return {
          color: 'bg-gray-400',
          text: 'Disconnected',
          textColor: 'text-gray-600'
        };
    }
  };

  const connectionStatus = getConnectionStatus();
  const deviceCount = health?.devices_count ?? 0;

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Title */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg 
                  className="w-5 h-5 text-white" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" 
                  />
                </svg>
              </div>
            </div>
            <div className="ml-3">
              <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
              <p className="text-sm text-gray-500">
                {subtitle} {deviceCount > 0 && `• ${deviceCount} devices`}
              </p>
            </div>
          </div>

          {/* Status Indicators */}
          <div className="flex items-center space-x-6">
            {/* API Health Status */}
            {health && (
              <div className="flex items-center">
                <div className={`w-2 h-2 ${
                  health.status === 'healthy' ? 'bg-green-400' : 'bg-red-400'
                } rounded-full mr-2`}></div>
                <span className="text-sm text-gray-600">
                  API {health.status === 'healthy' ? 'Healthy' : 'Unhealthy'}
                </span>
              </div>
            )}

            {/* WebSocket Connection Status */}
            <div className="flex items-center">
              <div className={`w-2 h-2 ${connectionStatus.color} rounded-full mr-2 ${
                status === 'connecting' ? 'animate-pulse' : ''
              }`}></div>
              <span className={`text-sm ${connectionStatus.textColor}`}>
                {connectionStatus.text}
              </span>
            </div>
            
            {/* Settings/Menu Button */}
            <button 
              className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              aria-label="Settings"
              title="System Settings"
            >
              <svg 
                className="w-5 h-5" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" 
                />
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" 
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}