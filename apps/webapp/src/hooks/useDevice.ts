// Custom hook for device state management

import { useCallback, useEffect } from 'react';
import { 
  useDevice as useDeviceFromStore, 
  useDeviceStore 
} from '@/store/deviceStore';
// import type { Device } from '@/types/devices';

// ==================== INDIVIDUAL DEVICE HOOK ====================
export const useDevice = (deviceId: string) => {
  const device = useDeviceFromStore(deviceId);
  const { loadDevice, controlDevice, isDeviceLoading } = useDeviceStore();

  // Load device on mount if not already loaded
  useEffect(() => {
    if (!device && deviceId) {
      loadDevice(deviceId);
    }
  }, [deviceId, device, loadDevice]);

  // Control functions
  const control = useCallback(async (payload: any) => {
    if (!deviceId) return false;
    return await controlDevice(deviceId, payload);
  }, [deviceId, controlDevice]);

  return {
    device,
    loading: isDeviceLoading(deviceId),
    control,
    reload: () => loadDevice(deviceId),
    exists: !!device
  };
};

// ==================== MOTOR DEVICE HOOK ====================
export const useMotor = (deviceId: string) => {
  const { device, loading, reload, exists } = useDevice(deviceId);
  const { controlMotor } = useDeviceStore();

  const setSpeed = useCallback(async (speed: number) => {
    if (!deviceId || !exists) return false;
    return await controlMotor(deviceId, speed);
  }, [deviceId, controlMotor, exists]);

  const getCurrentSpeed = useCallback(() => {
    if (!device || device.device_type !== 'motor') return 0;
    
    const value = device.current_value;
    if (typeof value === 'number') return value;
    if (typeof value === 'object' && value !== null && 'speed' in value) {
      return (value as any).speed;
    }
    return 0;
  }, [device]);

  return {
    device,
    loading,
    exists,
    currentSpeed: getCurrentSpeed(),
    setSpeed,
    reload,
    isMotor: device?.device_type === 'motor'
  };
};

// ==================== VALVE DEVICE HOOK ====================
export const useValve = (deviceId: string) => {
  const { device, loading, reload, exists } = useDevice(deviceId);
  const { controlValve } = useDeviceStore();

  const setState = useCallback(async (state: boolean) => {
    if (!deviceId || !exists) return false;
    return await controlValve(deviceId, state);
  }, [deviceId, controlValve, exists]);

  const getCurrentState = useCallback(() => {
    if (!device || device.device_type !== 'valve') return false;
    
    const value = device.current_value;
    if (typeof value === 'boolean') return value;
    if (typeof value === 'object' && value !== null && 'value' in value) {
      return (value as any).value;
    }
    return false;
  }, [device]);

  const toggle = useCallback(async () => {
    const currentState = getCurrentState();
    return await setState(!currentState);
  }, [getCurrentState, setState]);

  return {
    device,
    loading,
    exists,
    isOpen: getCurrentState(),
    setState,
    toggle,
    reload,
    isValve: device?.device_type === 'valve'
  };
};

// ==================== SERVO DEVICE HOOK ====================
export const useServo = (deviceId: string) => {
  const { device, loading, reload, exists } = useDevice(deviceId);
  const { controlServo } = useDeviceStore();

  const setAngle = useCallback(async (angle: number) => {
    if (!deviceId || !exists) return false;
    return await controlServo(deviceId, angle);
  }, [deviceId, controlServo, exists]);

  const getCurrentAngle = useCallback(() => {
    if (!device || device.device_type !== 'servo') return 0;
    
    const value = device.current_value;
    if (typeof value === 'number') return value;
    if (typeof value === 'object' && value !== null && 'angle' in value) {
      return (value as any).angle;
    }
    return 0;
  }, [device]);

  return {
    device,
    loading,
    exists,
    currentAngle: getCurrentAngle(),
    setAngle,
    reload,
    isServo: device?.device_type === 'servo'
  };
};

// ==================== TEMPERATURE SENSOR HOOK ====================
export const useTemperatureSensor = (deviceId: string) => {
  const { device, loading, reload, exists } = useDevice(deviceId);

  const getCurrentTemperature = useCallback(() => {
    if (!device || device.device_type !== 'temperature') return 0;
    
    const value = device.current_value;
    if (typeof value === 'number') return value;
    if (typeof value === 'object' && value !== null && 'temperature' in value) {
      return (value as any).temperature;
    }
    return 0;
  }, [device]);

  return {
    device,
    loading,
    exists,
    currentTemperature: getCurrentTemperature(),
    reload,
    isTemperatureSensor: device?.device_type === 'temperature'
  };
};

// ==================== ALL DEVICES HOOK ====================
export const useDevices = () => {
  const { 
    devices, 
    health, 
    connection, 
    loadDevices, 
    checkHealth, 
    connectWebSocket 
  } = useDeviceStore();

  // Load all devices on mount
  useEffect(() => {
    const initializeSystem = async () => {
      await checkHealth();
      await loadDevices();
      connectWebSocket();
    };

    initializeSystem();
  }, [checkHealth, loadDevices, connectWebSocket]);

  const getDevicesByType = useCallback((deviceType: string) => {
    return Object.values(devices).filter(device => device.device_type === deviceType);
  }, [devices]);

  const getDevicesArray = useCallback(() => {
    return Object.values(devices);
  }, [devices]);

  const getDeviceCount = useCallback(() => {
    return Object.keys(devices).length;
  }, [devices]);

  const getOnlineDeviceCount = useCallback(() => {
    return Object.values(devices).filter(device => device.status === 'online').length;
  }, [devices]);

  return {
    devices,
    health,
    connection,
    // Utility functions
    getDevicesByType,
    getDevicesArray,
    getDeviceCount,
    getOnlineDeviceCount,
    // Actions
    reload: loadDevices,
    checkHealth
  };
};

// ==================== TYPED DEVICE HOOKS ====================
// Convenience hooks for specific device types
export const useMotors = () => {
  const { devices } = useDeviceStore();
  return Object.values(devices).filter(device => device.device_type === 'motor');
};

export const useValves = () => {
  const { devices } = useDeviceStore();
  return Object.values(devices).filter(device => device.device_type === 'valve');
};

export const useServos = () => {
  const { devices } = useDeviceStore();
  return Object.values(devices).filter(device => device.device_type === 'servo');
};

export const useTemperatureSensors = () => {
  const { devices } = useDeviceStore();
  return Object.values(devices).filter(device => device.device_type === 'temperature');
};