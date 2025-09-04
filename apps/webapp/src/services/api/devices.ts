// API service for device HTTP requests

import { 
  HealthStatus, 
  DeviceStatusResponse, 
  DeviceListResponse, 
  DeviceUpdateResponse,
  DeviceControlPayload,
  // ApiError
} from '@/types/devices';
import { API_ENDPOINTS, getApiUrl, DEFAULT_HEADERS, API_CONFIG } from '@/config/api';

// ==================== ERROR HANDLING ====================
class DeviceApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public deviceId?: string
  ) {
    super(message);
    this.name = 'DeviceApiError';
  }
}

const handleApiResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new DeviceApiError(
      errorData.message || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      errorData.device_id
    );
  }
  return response.json();
};

// ==================== HTTP CLIENT ====================
const makeRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const url = getApiUrl(endpoint);
  
  const config: RequestInit = {
    ...options,
    headers: {
      ...DEFAULT_HEADERS,
      ...options.headers,
    },
    // Add timeout using AbortController
    signal: AbortSignal.timeout(API_CONFIG.timeout),
  };

  try {
    const response = await fetch(url, config);
    return handleApiResponse<T>(response);
  } catch (error) {
    if (error instanceof DeviceApiError) {
      throw error;
    }
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new DeviceApiError('Request timeout');
      }
      throw new DeviceApiError(`Network error: ${error.message}`);
    }
    
    throw new DeviceApiError('Unknown error occurred');
  }
};

// ==================== HEALTH ENDPOINTS ====================
export const getHealthStatus = async (): Promise<HealthStatus> => {
  return makeRequest<HealthStatus>(API_ENDPOINTS.HEALTH);
};

export const getSystemInfo = async (): Promise<any> => {
  return makeRequest<any>(API_ENDPOINTS.ROOT);
};

// ==================== DEVICE ENDPOINTS ====================
export const getDevices = async (): Promise<DeviceListResponse> => {
  return makeRequest<DeviceListResponse>(API_ENDPOINTS.DEVICES);
};

export const getDevice = async (deviceId: string): Promise<DeviceStatusResponse> => {
  return makeRequest<DeviceStatusResponse>(API_ENDPOINTS.DEVICE(deviceId));
};

export const updateDevice = async (
  deviceId: string, 
  payload: DeviceControlPayload
): Promise<DeviceUpdateResponse> => {
  return makeRequest<DeviceUpdateResponse>(API_ENDPOINTS.DEVICE(deviceId), {
    method: 'POST',
    body: JSON.stringify(payload),
  });
};

// ==================== DEVICE-SPECIFIC CONTROL FUNCTIONS ====================
export const controlMotor = async (deviceId: string, speed: number): Promise<DeviceUpdateResponse> => {
  if (speed < 0 || speed > 255) {
    throw new DeviceApiError('Motor speed must be between 0 and 255', 400, deviceId);
  }
  return updateDevice(deviceId, { speed });
};

export const controlServo = async (deviceId: string, angle: number): Promise<DeviceUpdateResponse> => {
  if (angle < 0 || angle > 180) {
    throw new DeviceApiError('Servo angle must be between 0 and 180', 400, deviceId);
  }
  return updateDevice(deviceId, { angle });
};

export const controlValve = async (deviceId: string, state: boolean): Promise<DeviceUpdateResponse> => {
  return updateDevice(deviceId, { state });
};

// ==================== BATCH OPERATIONS ====================
export const getMultipleDevices = async (deviceIds: string[]): Promise<DeviceStatusResponse[]> => {
  const requests = deviceIds.map(id => getDevice(id));
  const results = await Promise.allSettled(requests);
  
  return results.map((result, index) => {
    if (result.status === 'fulfilled') {
      return result.value;
    } else {
      // Return error device status for failed requests
      return {
        device_id: deviceIds[index],
        device_type: 'motor' as const, // Default type, will be corrected when device comes online
        status: 'error' as const,
        current_value: `Error: ${result.reason?.message || 'Unknown error'}`,
      };
    }
  });
};

// ==================== RETRY MECHANISM ====================
export const retryRequest = async <T>(
  requestFn: () => Promise<T>,
  maxRetries: number = API_CONFIG.retries,
  delay: number = API_CONFIG.retryDelay
): Promise<T> => {
  let lastError: Error;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error as Error;
      
      // Don't retry on client errors (4xx) except timeout
      if (error instanceof DeviceApiError && error.statusCode && error.statusCode >= 400 && error.statusCode < 500) {
        if (error.statusCode !== 408) { // 408 Request Timeout
          throw error;
        }
      }
      
      if (attempt < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, attempt)));
      }
    }
  }
  
  throw lastError!;
};

// ==================== HEALTH CHECK WITH RETRY ====================
export const checkHealth = async (): Promise<HealthStatus> => {
  return retryRequest(() => getHealthStatus(), 2, 1000);
};

// ==================== EXPORTS ====================
export { DeviceApiError };