import asyncio
import random
from typing import Any, Dict

from domain.ports.io_device import IODevice


class ValveAdapter(IODevice):
    """Infrastructure adapter for valve device implementation.
    
    Simulates a realistic valve with random I/O delays and state management.
    Acts as both sensor (read current state) and actuator (control open/closed).
    """
    
    def __init__(self, device_id: str, initial_state: bool = False):
        """Initialize valve adapter.
        
        Args:
            valve_id: Unique identifier for this valve
            initial_state: Initial valve state (False=closed, True=open)
        """
        self._device_id = device_id
        self._is_open = initial_state
        self._lock = asyncio.Lock()
    
    @property
    def device_id(self) -> str:
        """Return the valve identifier."""
        return self._device_id

    @property
    def device_type(self) -> str:
        """Return the device type."""
        return "valve"
    
    async def read(self) -> bool:
        """Read current valve state with realistic delay.
        
        Returns:
            bool: True if valve is open, False if closed
        """
        # Simulate realistic I/O delay (10-50ms)
        delay = random.uniform(0.01, 0.05)
        await asyncio.sleep(delay)
        
        async with self._lock:
            return self._is_open
    
    async def write(self, data: Dict[str, Any]) -> None:
        """Write new valve state with realistic delay.
        
        Args:
            data: Must contain {"value": bool} to set valve state
            
        Raises:
            ValueError: If payload is invalid
        """
        if "value" not in data:
            raise ValueError("Invalid payload: 'value' key required")
        
        new_state = data["value"]
        if not isinstance(new_state, bool):
            raise ValueError("Invalid payload: 'value' must be boolean")
        
        # Simulate valve actuation delay (20-80ms)
        delay = random.uniform(0.02, 0.08)
        await asyncio.sleep(delay)
        
        async with self._lock:
            self._is_open = new_state
