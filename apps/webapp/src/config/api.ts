// API configuration constants

// ==================== BASE CONFIGURATION ====================
const isDevelopment = import.meta.env.DEV;
const API_BASE_URL = isDevelopment 
  ? 'http://localhost:8000'  // Development backend
  : '/api';                  // Production (assuming same origin)

const WS_BASE_URL = isDevelopment
  ? 'ws://localhost:8000'    // Development WebSocket
  : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`;

// ==================== API ENDPOINTS ====================
export const API_ENDPOINTS = {
  // Health and system
  HEALTH: '/health/',
  ROOT: '/',
  
  // Device endpoints  
  DEVICES: '/api/v1/devices/',
  DEVICE: (deviceId: string) => `/api/v1/devices/${deviceId}`,
  
  // WebSocket endpoints
  WS_DEVICES: '/ws/devices',
} as const;

// ==================== FULL URLS ====================
export const API_CONFIG = {
  baseURL: API_BASE_URL,
  wsBaseURL: WS_BASE_URL,
  
  // HTTP Configuration
  timeout: 10000, // 10 seconds
  retries: 3,
  retryDelay: 1000, // 1 second
  
  // WebSocket Configuration
  wsReconnectInterval: 10000, // 10 seconds (longer delay)
  wsMaxReconnectAttempts: 3,   // Only 3 attempts before giving up
  wsHeartbeatInterval: 30000, // 30 seconds
} as const;

// ==================== HELPER FUNCTIONS ====================
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.baseURL}${endpoint}`;
};

export const getWebSocketUrl = (endpoint: string, params?: Record<string, string>): string => {
  const url = new URL(`${API_CONFIG.wsBaseURL}${endpoint}`);
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
  }
  
  return url.toString();
};

// ==================== REQUEST HEADERS ====================
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
} as const;

// ==================== ENVIRONMENT INFO ====================
export const ENV_INFO = {
  isDevelopment,
  apiBaseUrl: API_BASE_URL,
  wsBaseUrl: WS_BASE_URL,
  version: '1.0.0',
} as const;