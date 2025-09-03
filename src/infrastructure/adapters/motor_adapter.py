import asyncio
import random
from typing import Any, Dict

from domain.ports.io_device import IODevice


class MotorAdapter(IODevice):
    """Infrastructure adapter for motor device implementation.
    
    Simulates a realistic motor with PWM speed control and random I/O delays.
    Acts as both sensor (read current speed) and actuator (control speed).
    Speed range: 0-255 (8-bit PWM resolution).
    """
    
    def __init__(self, device_id: str, initial_speed: int = 0):
        """Initialize motor adapter.
        
        Args:
            device_id: Unique identifier for this motor
            initial_speed: Initial motor speed (0-255, default 0=stopped)
        """
        self._device_id = device_id
        if not (0 <= initial_speed <= 255):
            raise ValueError("Initial speed must be in range 0-255")
        self._current_speed = initial_speed
        self._lock = asyncio.Lock()
    
    @property
    def device_id(self) -> str:
        """Return the motor identifier."""
        return self._device_id

    @property
    def device_type(self) -> str:
        """Return the device type."""
        return "motor"
    
    async def read(self) -> int:
        """Read current motor speed with realistic delay.
        
        Returns:
            int: Current motor speed (0-255, 8-bit PWM)
        """
        # Simulate realistic I/O delay (15-45ms for speed reading)
        delay = random.uniform(0.015, 0.045)
        await asyncio.sleep(delay)
        
        async with self._lock:
            return self._current_speed
    
    async def write(self, data: Dict[str, Any]) -> None:
        """Write new motor speed with realistic delay.
        
        Args:
            data: Must contain {"speed": int} with value 0-255
            
        Raises:
            ValueError: If payload is invalid or speed out of range
        """
        if "speed" not in data:
            raise ValueError("Invalid payload: 'speed' key required")
        
        new_speed = data["speed"]
        if not isinstance(new_speed, int):
            raise ValueError("Invalid payload: 'speed' must be integer")
        
        if not (0 <= new_speed <= 255):
            raise ValueError("Invalid speed: must be in range 0-255 (8-bit PWM)")
        
        # Simulate motor control delay (25-75ms for speed changes)
        delay = random.uniform(0.025, 0.075)
        await asyncio.sleep(delay)
        
        async with self._lock:
            self._current_speed = new_speed
