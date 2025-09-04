// TypeScript types for device data structures and API responses

// ==================== HEALTH STATUS ====================
export interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  service: string;
  devices_count: number;
  message: string;
}

// ==================== DEVICE TYPES ====================
export type DeviceType = 'motor' | 'valve' | 'servo' | 'temperature';

export type DeviceStatus = 'online' | 'offline' | 'error' | 'warning';

// ==================== DEVICE RESPONSES ====================
export interface DeviceStatusResponse {
  device_id: string;
  device_type: DeviceType;
  status: DeviceStatus;
  current_value: any;
  last_updated?: string;
}

export interface DeviceUpdateResponse {
  device_id: string;
  device_type: DeviceType;
  previous_state: Record<string, any>;
  new_state: Record<string, any>;
  status: string;
  message: string;
  changed: boolean;
}

// ==================== DEVICE CONTROL PAYLOADS ====================
export interface MotorControlPayload {
  speed: number; // 0-255
}

export interface ServoControlPayload {
  angle: number; // 0-180
}

export interface ValveControlPayload {
  state: boolean; // true = open, false = closed
}

export type DeviceControlPayload = 
  | MotorControlPayload 
  | ServoControlPayload 
  | ValveControlPayload;

// ==================== DEVICE VALUES ====================
export interface MotorValue {
  speed: number;
}

export interface ServoValue {
  angle: number;
}

export interface ValveValue {
  value: boolean;
}

export interface TemperatureValue {
  temperature: number;
}

export type DeviceValue = 
  | MotorValue 
  | ServoValue 
  | ValveValue 
  | TemperatureValue 
  | number 
  | boolean;

// ==================== DEVICE STATE ====================
export interface Device {
  device_id: string;
  device_type: DeviceType;
  status: DeviceStatus;
  current_value: DeviceValue;
  last_updated?: Date;
  loading?: boolean;
  error?: string;
}

// ==================== API RESPONSES ====================
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  loading?: boolean;
}

export interface DeviceListResponse {
  [device_id: string]: DeviceStatusResponse;
}

// ==================== WEBSOCKET MESSAGES ====================
export interface WebSocketMessage {
  type: 'device_update' | 'system_status' | 'error' | 'connection_established';
  data: any;
  timestamp?: string;
}

export interface DeviceUpdateMessage {
  device_id: string;
  device_type: DeviceType;
  previous_state: Record<string, any>;
  new_state: Record<string, any>;
  changed: boolean;
  action: string;
}

// ==================== ERROR TYPES ====================
export interface ApiError {
  error: string;
  message: string;
  device_id?: string;
  status_code?: number;
}

// ==================== CONNECTION STATE ====================
export interface ConnectionState {
  status: 'connected' | 'disconnected' | 'connecting' | 'error';
  error?: string;
  lastConnected?: Date;
  reconnectAttempts?: number;
}

// ==================== SYSTEM STATE ====================
export interface SystemStatus {
  health: HealthStatus | null;
  connection: ConnectionState;
  devices: Record<string, Device>;
  lastUpdate: Date | null;
}