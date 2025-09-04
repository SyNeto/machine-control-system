import { Header } from '@/components/layout'
import { HealthIndicator, DisplayValue, SliderControl, Toggle } from '@/components/ui'
import { useDevices, useMotors, useValves, useServos, useTemperatureSensors } from '@/hooks/useDevice'
import { deviceActions } from '@/store/deviceStore'
import './App.css'

function App() {
  // Load all devices and system status
  const { health, connection, getDevicesArray, getOnlineDeviceCount } = useDevices();
  
  // Get devices by type
  const motors = useMotors();
  const valves = useValves(); 
  const servos = useServos();
  const temperatureSensors = useTemperatureSensors();

  // Get first device of each type for the demo
  const firstMotor = motors[0];
  const firstValve = valves[0];
  const firstServo = servos[0];
  const firstTempSensor = temperatureSensors[0];

  // Helper functions for device control
  const handleMotorSpeedChange = async (speed: number) => {
    if (firstMotor) {
      await deviceActions.controlMotor(firstMotor.device_id, speed);
    }
  };

  const handleValveToggle = async (state: boolean) => {
    if (firstValve) {
      await deviceActions.controlValve(firstValve.device_id, state);
    }
  };

  const handleServoAngleChange = async (angle: number) => {
    if (firstServo) {
      // Ensure integer value for servo
      const intAngle = Math.round(angle);
      await deviceActions.controlServo(firstServo.device_id, intAngle);
    }
  };

  // Get current values safely
  const getCurrentMotorPWM = () => {
    if (!firstMotor) return 0;
    const value = firstMotor.current_value;
    if (typeof value === 'number') return value;
    if (typeof value === 'object' && value && 'speed' in value) {
      return (value as any).speed;
    }
    return 0;
  };

  const getCurrentMotorRPM = () => {
    const pwmValue = getCurrentMotorPWM();
    // Map PWM (0-255) to RPM (0-40000)
    return Math.round((pwmValue / 255) * 40000);
  };

  const getCurrentValveState = () => {
    if (!firstValve) return false;
    const value = firstValve.current_value;
    if (typeof value === 'boolean') return value;
    if (typeof value === 'object' && value && 'value' in value) {
      return (value as any).value;
    }
    return false;
  };

  const getCurrentServoAngle = () => {
    if (!firstServo) return 0;
    const value = firstServo.current_value;
    if (typeof value === 'number') return Math.round(value); // Ensure integer
    if (typeof value === 'object' && value && 'angle' in value) {
      return Math.round((value as any).angle); // Ensure integer
    }
    return 0;
  };

  const getCurrentTemperature = () => {
    if (!firstTempSensor) return 0;
    const value = firstTempSensor.current_value;
    if (typeof value === 'number') return value;
    if (typeof value === 'object' && value && 'temperature' in value) {
      return (value as any).temperature;
    }
    return 0;
  };

  const devicesArray = getDevicesArray();
  const onlineDevices = getOnlineDeviceCount();

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* System Status Overview */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Machine Control Dashboard
          </h2>
          <p className="text-gray-600">
            Real-time monitoring and control of industrial devices
          </p>
          
          {/* Connection Status Bar */}
          {connection && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <HealthIndicator 
                    status={connection.status === 'connected' ? 'online' : 'error'} 
                    label={connection.status === 'connected' ? 'WebSocket Connected' : 'Connection Error'}
                  />
                  {health && (
                    <HealthIndicator 
                      status={health.status === 'healthy' ? 'online' : 'error'} 
                      label={health.status === 'healthy' ? 'API Healthy' : 'API Error'}
                    />
                  )}
                </div>
                <div className="text-sm text-gray-600">
                  {onlineDevices} of {devicesArray.length} devices online
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Real Device Controls */}
        {devicesArray.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Motor Control */}
            {firstMotor && (
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Motor Control</h3>
                  <HealthIndicator status={firstMotor.status} size="sm" />
                </div>
                <div className="space-y-4">
                  <SliderControl
                    label="Speed Control"
                    value={getCurrentMotorPWM()}
                    min={0}
                    max={255}
                    unit="PWM"
                    onChange={handleMotorSpeedChange}
                    disabled={firstMotor.loading || firstMotor.status !== 'online'}
                    size="sm"
                  />
                  <DisplayValue 
                    label="Current Speed"
                    value={getCurrentMotorRPM()}
                    unit="RPM"
                    loading={firstMotor.loading}
                    variant={firstMotor.status === 'online' ? 'default' : 'muted'}
                    size="sm"
                  />
                </div>
              </div>
            )}

            {/* Valve Control */}
            {firstValve && (
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Valve Control</h3>
                  <HealthIndicator status={firstValve.status} size="sm" />
                </div>
                <div className="space-y-4">
                  <Toggle
                    label="Valve State"
                    checked={getCurrentValveState()}
                    onChange={handleValveToggle}
                    variant="success"
                    showLabels={true}
                    labels={{ on: 'Open', off: 'Closed' }}
                    disabled={firstValve.loading || firstValve.status !== 'online'}
                    size="sm"
                  />
                  <DisplayValue 
                    label="Current State"
                    value={getCurrentValveState() ? 'OPEN' : 'CLOSED'}
                    loading={firstValve.loading}
                    variant={getCurrentValveState() ? 'highlighted' : 'muted'}
                    size="sm"
                  />
                </div>
              </div>
            )}

            {/* Servo Control */}
            {firstServo && (
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Servo Control</h3>
                  <HealthIndicator status={firstServo.status} size="sm" />
                </div>
                <div className="space-y-4">
                  <SliderControl
                    label="Position Control"
                    value={getCurrentServoAngle()}
                    min={0}
                    max={180}
                    step={1}
                    unit="°"
                    onChange={handleServoAngleChange}
                    disabled={firstServo.loading || firstServo.status !== 'online'}
                    size="sm"
                  />
                  <DisplayValue 
                    label="Current Position"
                    value={getCurrentServoAngle()}
                    unit="°"
                    loading={firstServo.loading}
                    variant={firstServo.status === 'online' ? 'default' : 'muted'}
                    size="sm"
                  />
                </div>
              </div>
            )}

            {/* Temperature Sensor */}
            {firstTempSensor && (
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Temperature Sensor</h3>
                  <HealthIndicator status={firstTempSensor.status} size="sm" />
                </div>
                <div className="space-y-4">
                  <DisplayValue 
                    label="Temperature"
                    value={getCurrentTemperature()}
                    unit="°C"
                    loading={firstTempSensor.loading}
                    variant="highlighted"
                    icon={
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    }
                  />
                  <p className="text-xs text-gray-500">
                    Read-only sensor • Updates automatically
                  </p>
                </div>
              </div>
            )}
          </div>
        ) : (
          // Loading state
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Loading Devices...</h3>
            <p className="text-gray-500">
              Connecting to the machine control system
            </p>
          </div>
        )}

        {/* All Devices Overview */}
        {devicesArray.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">All Devices</h3>
              <span className="text-sm text-gray-500">
                Last updated: {new Date().toLocaleTimeString()}
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {devicesArray.map(device => (
                <div key={device.device_id} className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{device.device_id}</h4>
                    <HealthIndicator status={device.status} size="sm" showLabel={false} />
                  </div>
                  <p className="text-sm text-gray-500 capitalize mb-2">{device.device_type}</p>
                  {device.status === 'online' ? (
                    <DisplayValue
                      label="Value"
                      value={typeof device.current_value === 'object' 
                        ? JSON.stringify(device.current_value) 
                        : String(device.current_value)}
                      loading={device.loading}
                      size="sm"
                    />
                  ) : (
                    <p className="text-xs text-red-600">
                      {device.error || 'Device offline'}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
