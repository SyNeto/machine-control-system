from typing import List, Dict, Any, Optional
from domain.ports.io_device import IODevice


class MachineControlService:
    """Simple service for managing devices.
    
    Manages a list of devices and provides methods to read/write data.
    No complex business logic - just device coordination.
    """
    
    def __init__(self, devices: List[IODevice]):
        """Initialize with a list of devices.
        
        Args:
            devices: List of IoT devices to manage
        """
        self.devices = devices
        self._devices_by_id = {device.device_id: device for device in devices}
        self._devices_by_type = {}
        
        # Group devices by type for easy access
        for device in devices:
            device_type = device.device_type
            if device_type not in self._devices_by_type:
                self._devices_by_type[device_type] = []
            self._devices_by_type[device_type].append(device)
    
    def get_device_by_id(self, device_id: str) -> Optional[IODevice]:
        """Get device by ID."""
        return self._devices_by_id.get(device_id)
    
    def get_devices_by_type(self, device_type: str) -> List[IODevice]:
        """Get all devices of a specific type."""
        return self._devices_by_type.get(device_type, [])
    
    async def read_device(self, device_id: str) -> Any:
        """Read data from a specific device."""
        device = self.get_device_by_id(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        
        return await device.read()
    
    async def write_device(self, device_id: str, data: Dict[str, Any]) -> None:
        """Write data to a specific device."""
        device = self.get_device_by_id(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        
        await device.write(data)
    
    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get status of a specific device."""
        device = self.get_device_by_id(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")
        
        return await device.get_status()
    
    async def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all devices."""
        statuses = {}
        for device in self.devices:
            statuses[device.device_id] = await device.get_status()
        return statuses
    
    # Convenience methods for specific device types
    async def get_motor_speed(self) -> Optional[int]:
        """Get current motor speed (convenience method)."""
        motors = self.get_devices_by_type("motor")
        if not motors:
            return None
        return await motors[0].read()
    
    async def set_motor_speed(self, speed: int) -> None:
        """Set motor speed (convenience method)."""
        motors = self.get_devices_by_type("motor")
        if not motors:
            raise ValueError("No motor device found")
        await motors[0].write({"value": speed})
    
    async def get_valve_state(self) -> Optional[bool]:
        """Get current valve state (convenience method)."""
        valves = self.get_devices_by_type("valve")
        if not valves:
            return None
        return await valves[0].read()
    
    async def set_valve_state(self, open_valve: bool) -> None:
        """Set valve state (convenience method)."""
        valves = self.get_devices_by_type("valve")
        if not valves:
            raise ValueError("No valve device found")
        await valves[0].write({"value": open_valve})
    
    async def get_temperature(self) -> Optional[float]:
        """Get current temperature (convenience method)."""
        temp_sensors = self.get_devices_by_type("temperature_sensor")
        if not temp_sensors:
            return None
        return await temp_sensors[0].read()
    
    def list_devices(self) -> List[Dict[str, str]]:
        """List all devices with their basic info."""
        return [
            {
                "device_id": device.device_id,
                "device_type": device.device_type
            }
            for device in self.devices
        ]
