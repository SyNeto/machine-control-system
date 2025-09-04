// Custom hook for WebSocket connection management

import { useEffect, useCallback } from 'react';
import { useConnectionState } from '@/store/deviceStore';
import { 
  wsManager,
  connectWebSocket,
  disconnectWebSocket,
  onDeviceUpdate,
  subscribeToDevice,
  unsubscribeFromDevice
} from '@/services/api/websocket';
import { DeviceUpdateMessage } from '@/types/devices';

// ==================== WEBSOCKET CONNECTION HOOK ====================
export const useWebSocket = () => {
  const connectionState = useConnectionState();

  const connect = useCallback((clientId?: string) => {
    connectWebSocket(clientId);
  }, []);

  const disconnect = useCallback(() => {
    disconnectWebSocket();
  }, []);

  const isConnected = wsManager.isConnected;
  const readyState = wsManager.readyState;

  return {
    connectionState,
    isConnected,
    readyState,
    connect,
    disconnect
  };
};

// ==================== DEVICE UPDATE LISTENER HOOK ====================
export const useDeviceUpdates = (
  onUpdate?: (message: DeviceUpdateMessage) => void,
  deviceIds?: string[]
) => {
  useEffect(() => {
    if (!onUpdate) return;

    const unsubscribe = onDeviceUpdate((message: DeviceUpdateMessage) => {
      // Filter by device IDs if specified
      if (deviceIds && !deviceIds.includes(message.device_id)) {
        return;
      }
      onUpdate(message);
    });

    return unsubscribe;
  }, [onUpdate, deviceIds]);
};

// ==================== CONNECTION LISTENER HOOK ====================
export const useConnectionStatus = (
  onConnectionChange?: (connected: boolean) => void
) => {
  const connectionState = useConnectionState();

  useEffect(() => {
    // Connection state management is handled by the store
    if (onConnectionChange && connectionState.status) {
      onConnectionChange(connectionState.status === 'connected');
    }
  }, [onConnectionChange, connectionState.status]);

  return {
    isConnected: connectionState.status === 'connected',
    status: connectionState.status,
    error: connectionState.error,
    lastConnected: connectionState.lastConnected,
    reconnectAttempts: connectionState.reconnectAttempts
  };
};

// ==================== DEVICE SUBSCRIPTION HOOK ====================
export const useDeviceSubscription = (deviceId: string, autoSubscribe = true) => {
  const subscribe = useCallback(() => {
    if (deviceId) {
      subscribeToDevice(deviceId);
    }
  }, [deviceId]);

  const unsubscribe = useCallback(() => {
    if (deviceId) {
      unsubscribeFromDevice(deviceId);
    }
  }, [deviceId]);

  useEffect(() => {
    if (autoSubscribe && deviceId) {
      subscribe();
      return unsubscribe;
    }
  }, [deviceId, autoSubscribe, subscribe, unsubscribe]);

  return {
    subscribe,
    unsubscribe
  };
};