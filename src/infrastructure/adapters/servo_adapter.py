import asyncio
import random
from typing import Any, Dict

from domain.ports.io_device import IODevice


class ServoAdapter(IODevice):
    """Infrastructure adapter for servo motor device implementation.
    
    Simulates a realistic servo motor with angle control and random I/O delays.
    Acts as both sensor (read current angle) and actuator (control position).
    Angle range: 0-180 degrees (standard servo range).
    """
    
    def __init__(self, servo_id: str, initial_angle: int = 90):
        """Initialize servo adapter.
        
        Args:
            servo_id: Unique identifier for this servo
            initial_angle: Initial servo angle (0-180 degrees, default 90=center)
        """
        self._servo_id = servo_id
        if not (0 <= initial_angle <= 180):
            raise ValueError("Initial angle must be in range 0-180 degrees")
        self._current_angle = initial_angle
        self._lock = asyncio.Lock()
    
    @property
    def device_id(self) -> str:
        """Return the servo identifier."""
        return self._servo_id
    
    @property
    def device_type(self) -> str:
        """Return the device type."""
        return "servo"
    
    async def read(self) -> int:
        """Read current servo angle with realistic delay.
        
        Returns:
            int: Current servo angle (0-180 degrees)
        """
        # Simulate realistic position feedback delay (20-60ms)
        delay = random.uniform(0.020, 0.060)
        await asyncio.sleep(delay)
        
        async with self._lock:
            return self._current_angle
    
    async def write(self, data: Dict[str, Any]) -> None:
        """Write new servo angle with realistic delay.
        
        Args:
            data: Must contain {"angle": int} with value 0-180
            
        Raises:
            ValueError: If payload is invalid or angle out of range
        """
        if "angle" not in data:
            raise ValueError("Invalid payload: 'angle' key required")
        
        new_angle = data["angle"]
        if not isinstance(new_angle, int):
            raise ValueError("Invalid payload: 'angle' must be integer")
        
        if not (0 <= new_angle <= 180):
            raise ValueError("Invalid angle: must be in range 0-180 degrees")
        
        # Simulate servo movement delay - longer for larger movements
        current_angle = self._current_angle
        angle_diff = abs(new_angle - current_angle)
        # Base delay + proportional to movement (1-2ms per degree)
        base_delay = random.uniform(0.030, 0.070)
        movement_delay = angle_diff * random.uniform(0.001, 0.002)
        total_delay = base_delay + movement_delay
        
        await asyncio.sleep(total_delay)
        
        async with self._lock:
            self._current_angle = new_angle
