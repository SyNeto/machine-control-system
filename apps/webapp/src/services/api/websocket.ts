// WebSocket service for real-time device data

import { 
  WebSocketMessage, 
  DeviceUpdateMessage, 
  ConnectionState 
} from '@/types/devices';
import { API_ENDPOINTS, getWebSocketUrl, API_CONFIG } from '@/config/api';

// ==================== WEBSOCKET MANAGER CLASS ====================
class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private listeners: Map<string, Set<Function>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = API_CONFIG.wsMaxReconnectAttempts;
  private reconnectInterval = API_CONFIG.wsReconnectInterval;

  public connectionState: ConnectionState = {
    status: 'disconnected'
  };

  // ==================== CONNECTION MANAGEMENT ====================
  connect(clientId: string = 'webapp-client'): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    // Check if we've already exceeded max attempts
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.warn('WebSocket disabled after max connection attempts. Backend may need WebSocket dependencies.');
      this.setConnectionState({ 
        status: 'error', 
        error: 'WebSocket unavailable - backend needs WebSocket dependencies installed' 
      });
      return;
    }

    this.setConnectionState({ status: 'connecting' });

    try {
      const wsUrl = getWebSocketUrl(API_ENDPOINTS.WS_DEVICES, { client_id: clientId });
      console.log('Attempting WebSocket connection to:', wsUrl);
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      this.setConnectionState({ 
        status: 'error', 
        error: error instanceof Error ? error.message : 'Connection failed' 
      });
    }
  }

  disconnect(): void {
    this.clearTimers();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    this.setConnectionState({ status: 'disconnected' });
    this.reconnectAttempts = 0;
  }

  // ==================== EVENT HANDLERS ====================
  private handleOpen(): void {
    console.log('WebSocket connected');
    this.reconnectAttempts = 0;
    this.setConnectionState({ 
      status: 'connected', 
      lastConnected: new Date(),
      reconnectAttempts: 0
    });
    
    this.startHeartbeat();
    this.emit('connection', { connected: true });
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      // Emit message to specific listeners
      this.emit(message.type, message.data);
      
      // Also emit to general message listeners
      this.emit('message', message);
      
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
      this.emit('error', { error: 'Invalid message format' });
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log('WebSocket closed:', event.code, event.reason);
    this.clearTimers();
    
    if (event.code !== 1000) { // Not a normal closure
      this.attemptReconnect();
    } else {
      this.setConnectionState({ status: 'disconnected' });
    }
    
    this.emit('connection', { connected: false });
  }

  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    
    // More specific error handling
    let errorMessage = 'WebSocket connection error';
    if (this.ws?.readyState === WebSocket.CLOSED) {
      errorMessage = 'WebSocket server unavailable - check backend WebSocket dependencies';
    }
    
    this.setConnectionState({ 
      status: 'error', 
      error: errorMessage 
    });
    this.emit('error', { error: errorMessage });
  }

  // ==================== RECONNECTION LOGIC ====================
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.setConnectionState({ 
        status: 'error', 
        error: 'Max reconnection attempts reached' 
      });
      return;
    }

    this.reconnectAttempts++;
    this.setConnectionState({ 
      status: 'connecting', 
      reconnectAttempts: this.reconnectAttempts 
    });

    const delay = Math.min(
      this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1),
      30000 // Max 30 seconds
    );

    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  // ==================== HEARTBEAT ====================
  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.sendMessage({ action: 'ping' });
      }
    }, API_CONFIG.wsHeartbeatInterval);
  }

  // ==================== MESSAGE SENDING ====================
  sendMessage(message: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, message not sent:', message);
    }
  }

  // Subscribe to device updates
  subscribeToDevice(deviceId: string): void {
    this.sendMessage({ 
      action: 'subscribe', 
      device_id: deviceId 
    });
  }

  // Unsubscribe from device updates
  unsubscribeFromDevice(deviceId: string): void {
    this.sendMessage({ 
      action: 'unsubscribe', 
      device_id: deviceId 
    });
  }

  // Get current status of all devices
  requestAllStatus(): void {
    this.sendMessage({ action: 'get_all_status' });
  }

  // Get status of specific device
  requestDeviceStatus(deviceId: string): void {
    this.sendMessage({ 
      action: 'get_status', 
      device_id: deviceId 
    });
  }

  // ==================== EVENT SYSTEM ====================
  on(event: string, callback: Function): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    
    this.listeners.get(event)!.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  private emit(event: string, data: any): void {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in WebSocket event handler for ${event}:`, error);
        }
      });
    }
  }

  // ==================== UTILITY METHODS ====================
  private setConnectionState(newState: Partial<ConnectionState>): void {
    this.connectionState = { ...this.connectionState, ...newState };
    this.emit('connectionStateChanged', this.connectionState);
  }

  private clearTimers(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  // ==================== PUBLIC GETTERS ====================
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  get readyState(): number | null {
    return this.ws?.readyState ?? null;
  }
}

// ==================== SINGLETON INSTANCE ====================
export const wsManager = new WebSocketManager();

// ==================== CONVENIENCE FUNCTIONS ====================
export const connectWebSocket = (clientId?: string): void => {
  wsManager.connect(clientId);
};

export const disconnectWebSocket = (): void => {
  wsManager.disconnect();
};

export const onDeviceUpdate = (callback: (data: DeviceUpdateMessage) => void): (() => void) => {
  return wsManager.on('device_update', callback);
};

export const onConnectionChange = (callback: (data: { connected: boolean }) => void): (() => void) => {
  return wsManager.on('connection', callback);
};

export const onConnectionStateChange = (callback: (state: ConnectionState) => void): (() => void) => {
  return wsManager.on('connectionStateChanged', callback);
};

export const subscribeToDevice = (deviceId: string): void => {
  wsManager.subscribeToDevice(deviceId);
};

export const unsubscribeFromDevice = (deviceId: string): void => {
  wsManager.unsubscribeFromDevice(deviceId);
};

// ==================== AUTO-CONNECTION ====================
// Automatically connect when the module is imported
if (typeof window !== 'undefined') {
  // Only connect in browser environment
  connectWebSocket('webapp-auto');
}