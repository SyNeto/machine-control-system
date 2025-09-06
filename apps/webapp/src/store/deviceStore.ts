// Zustand store for device state management

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { 
  Device, 
  // HealthStatus, 
  SystemStatus, 
  ConnectionState,
  DeviceControlPayload,
  DeviceUpdateMessage,
  DeviceValue
} from '@/types/devices';
import * as deviceApi from '@/services/api/devices';
import { 
  wsManager, 
  onDeviceUpdate, 
  onConnectionStateChange, 
  subscribeToDevice 
} from '@/services/api/websocket';

// ==================== STORE INTERFACE ====================
interface DeviceStore extends SystemStatus {
  // ==================== ACTIONS ====================
  
  // Health and Connection
  checkHealth: () => Promise<void>;
  setConnectionState: (state: Partial<ConnectionState>) => void;
  
  // Device Management
  loadDevices: () => Promise<void>;
  loadDevice: (deviceId: string) => Promise<void>;
  updateDeviceLocally: (deviceId: string, updates: Partial<Device>) => void;
  
  // Device Control
  controlDevice: (deviceId: string, payload: DeviceControlPayload) => Promise<boolean>;
  controlMotor: (deviceId: string, speed: number) => Promise<boolean>;
  controlServo: (deviceId: string, angle: number) => Promise<boolean>;
  controlValve: (deviceId: string, state: boolean) => Promise<boolean>;
  
  // WebSocket Management
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
  subscribeToDeviceUpdates: (deviceId: string) => void;
  
  // Utility
  reset: () => void;
  getDevice: (deviceId: string) => Device | undefined;
  getDevicesByType: (deviceType: string) => Device[];
  isDeviceLoading: (deviceId: string) => boolean;
}

// ==================== INITIAL STATE ====================
const initialState: SystemStatus = {
  health: null,
  connection: {
    status: 'disconnected'
  },
  devices: {},
  lastUpdate: null
};

// ==================== ZUSTAND STORE ====================
export const useDeviceStore = create<DeviceStore>()(
  subscribeWithSelector((set, get) => ({
    ...initialState,

    // ==================== HEALTH & CONNECTION ====================
    checkHealth: async () => {
      try {
        const health = await deviceApi.checkHealth();
        set(state => ({ 
          ...state, 
          health,
          lastUpdate: new Date() 
        }));
      } catch (error) {
        console.error('Health check failed:', error);
        set(state => ({ 
          ...state, 
          health: {
            status: 'unhealthy' as const,
            service: 'Machine Control Panel API',
            devices_count: 0,
            message: error instanceof Error ? error.message : 'Health check failed'
          },
          lastUpdate: new Date()
        }));
      }
    },

    setConnectionState: (connectionUpdates) => {
      set(state => ({
        ...state,
        connection: { ...state.connection, ...connectionUpdates }
      }));
    },

    // ==================== DEVICE LOADING ====================
    loadDevices: async () => {
      try {
        const deviceResponses = await deviceApi.getDevices();
        
        const devices: Record<string, Device> = {};
        Object.values(deviceResponses).forEach(deviceResponse => {
          devices[deviceResponse.device_id] = {
            device_id: deviceResponse.device_id,
            device_type: deviceResponse.device_type,
            status: deviceResponse.status,
            current_value: deviceResponse.current_value,
            last_updated: deviceResponse.last_updated ? new Date(deviceResponse.last_updated) : new Date(),
            loading: false
          };
        });

        set(state => ({
          ...state,
          devices,
          lastUpdate: new Date()
        }));

        // Subscribe to real-time updates for all devices
        Object.keys(devices).forEach(deviceId => {
          subscribeToDevice(deviceId);
        });

      } catch (error) {
        console.error('Failed to load devices:', error);
        // Mark all devices as error state
        set(state => {
          const errorDevices: Record<string, Device> = {};
          Object.keys(state.devices).forEach(deviceId => {
            errorDevices[deviceId] = {
              ...state.devices[deviceId],
              status: 'error',
              error: error instanceof Error ? error.message : 'Failed to load device',
              loading: false
            };
          });
          return { ...state, devices: errorDevices };
        });
      }
    },

    loadDevice: async (deviceId: string) => {
      // Set loading state
      set(state => ({
        ...state,
        devices: {
          ...state.devices,
          [deviceId]: {
            ...state.devices[deviceId],
            loading: true
          }
        }
      }));

      try {
        const deviceResponse = await deviceApi.getDevice(deviceId);
        
        const device: Device = {
          device_id: deviceResponse.device_id,
          device_type: deviceResponse.device_type,
          status: deviceResponse.status,
          current_value: deviceResponse.current_value,
          last_updated: deviceResponse.last_updated ? new Date(deviceResponse.last_updated) : new Date(),
          loading: false
        };

        set(state => ({
          ...state,
          devices: {
            ...state.devices,
            [deviceId]: device
          },
          lastUpdate: new Date()
        }));

        // Subscribe to real-time updates
        subscribeToDevice(deviceId);

      } catch (error) {
        console.error(`Failed to load device ${deviceId}:`, error);
        set(state => ({
          ...state,
          devices: {
            ...state.devices,
            [deviceId]: {
              ...state.devices[deviceId],
              status: 'error',
              error: error instanceof Error ? error.message : 'Failed to load device',
              loading: false
            }
          }
        }));
      }
    },

    updateDeviceLocally: (deviceId, updates) => {
      set(state => ({
        ...state,
        devices: {
          ...state.devices,
          [deviceId]: {
            ...state.devices[deviceId],
            ...updates,
            last_updated: new Date()
          }
        },
        lastUpdate: new Date()
      }));
    },

    // ==================== DEVICE CONTROL ====================
    controlDevice: async (deviceId, payload) => {
      // Set loading state
      get().updateDeviceLocally(deviceId, { loading: true });

      try {
        const response = await deviceApi.updateDevice(deviceId, payload);
        
        // Update device with new state
        const device = get().devices[deviceId];
        if (device) {
          // Extract the correct value based on device type
          let newValue: DeviceValue;
          if (device.device_type === 'motor' && response.new_state?.speed !== undefined) {
            newValue = response.new_state.speed;
          } else if (device.device_type === 'servo' && response.new_state?.angle !== undefined) {
            newValue = response.new_state.angle;
          } else if (device.device_type === 'valve' && response.new_state?.value !== undefined) {
            newValue = response.new_state.value;
          } else if (device.device_type === 'temperature' && response.new_state?.temperature !== undefined) {
            newValue = response.new_state.temperature;
          } else {
            // Fallback: use the entire object as-is and cast it
            newValue = response.new_state as DeviceValue;
          }

          get().updateDeviceLocally(deviceId, {
            current_value: newValue,
            loading: false,
            error: undefined
          });
        }

        return response.changed;
      } catch (error) {
        console.error(`Failed to control device ${deviceId}:`, error);
        get().updateDeviceLocally(deviceId, {
          loading: false,
          error: error instanceof Error ? error.message : 'Control failed'
        });
        return false;
      }
    },

    controlMotor: async (deviceId, speed) => {
      return get().controlDevice(deviceId, { speed });
    },

    controlServo: async (deviceId, angle) => {
      return get().controlDevice(deviceId, { angle });
    },

    controlValve: async (deviceId, state) => {
      return get().controlDevice(deviceId, { state });
    },

    // ==================== WEBSOCKET MANAGEMENT ====================
    connectWebSocket: () => {
      wsManager.connect('webapp-store');
    },

    disconnectWebSocket: () => {
      wsManager.disconnect();
    },

    subscribeToDeviceUpdates: (deviceId) => {
      subscribeToDevice(deviceId);
    },

    // ==================== UTILITY METHODS ====================
    reset: () => {
      set(initialState);
    },

    getDevice: (deviceId) => {
      return get().devices[deviceId];
    },

    getDevicesByType: (deviceType) => {
      return Object.values(get().devices).filter(device => device.device_type === deviceType);
    },

    isDeviceLoading: (deviceId) => {
      return get().devices[deviceId]?.loading ?? false;
    },
  }))
);

// ==================== WEBSOCKET INTEGRATION ====================
// Subscribe to WebSocket events and update store accordingly
onDeviceUpdate((updateMessage: DeviceUpdateMessage) => {
  const store = useDeviceStore.getState();
  const device = store.devices[updateMessage.device_id];
  
  if (device && updateMessage.changed) {
    // Extract the correct value based on device type
    let newValue: DeviceValue;
    if (device.device_type === 'motor' && updateMessage.new_state?.speed !== undefined) {
      newValue = updateMessage.new_state.speed;
    } else if (device.device_type === 'servo' && updateMessage.new_state?.angle !== undefined) {
      newValue = updateMessage.new_state.angle;
    } else if (device.device_type === 'valve' && updateMessage.new_state?.value !== undefined) {
      newValue = updateMessage.new_state.value;
    } else if (device.device_type === 'temperature' && updateMessage.new_state?.temperature !== undefined) {
      newValue = updateMessage.new_state.temperature;
    } else {
      // Fallback: use the entire object as-is and cast it
      newValue = updateMessage.new_state as DeviceValue;
    }

    store.updateDeviceLocally(updateMessage.device_id, {
      current_value: newValue,
      status: 'online',
      error: undefined
    });
  }
});

onConnectionStateChange((connectionState: ConnectionState) => {
  const store = useDeviceStore.getState();
  store.setConnectionState(connectionState);
});

// ==================== SELECTORS ====================
// Convenience selectors for common queries
export const useHealthStatus = () => useDeviceStore(state => state.health);
export const useConnectionState = () => useDeviceStore(state => state.connection);
export const useDevices = () => useDeviceStore(state => state.devices);
export const useDevice = (deviceId: string) => useDeviceStore(state => state.devices[deviceId]);
export const useDevicesByType = (deviceType: string) => 
  useDeviceStore(state => Object.values(state.devices).filter(device => device.device_type === deviceType));

// ==================== ACTIONS ====================
// Export actions for easy access
export const deviceActions = {
  checkHealth: () => useDeviceStore.getState().checkHealth(),
  loadDevices: () => useDeviceStore.getState().loadDevices(),
  loadDevice: (id: string) => useDeviceStore.getState().loadDevice(id),
  controlMotor: (id: string, speed: number) => useDeviceStore.getState().controlMotor(id, speed),
  controlServo: (id: string, angle: number) => useDeviceStore.getState().controlServo(id, angle),
  controlValve: (id: string, state: boolean) => useDeviceStore.getState().controlValve(id, state),
  connectWebSocket: () => useDeviceStore.getState().connectWebSocket(),
};