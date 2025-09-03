import asyncio
import httpx
from typing import Any, Dict, Optional

from domain.ports.io_device import IODevice


class TemperatureAdapter(IODevice):
    """Infrastructure adapter for ambient temperature sensor using OpenMeteo API.
    
    Fetches real-time temperature data from OpenMeteo weather service.
    Acts as sensor-only device (read-only, write operations not supported).
    """
    
    def __init__(
        self, 
        device_id: str,
        latitude: float, 
        longitude: float,
        timeout: float = 10.0
    ):
        """Initialize temperature sensor adapter.
        
        Args:
            device_id: Unique identifier for this temperature sensor
            latitude: Geographic latitude for temperature reading
            longitude: Geographic longitude for temperature reading  
            timeout: HTTP request timeout in seconds (default: 10.0)
        """
        self._device_id = device_id
        self._latitude = latitude
        self._longitude = longitude
        self._timeout = timeout
        self._base_url = "https://api.open-meteo.com/v1/forecast"
        
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees")
    
    @property
    def device_id(self) -> str:
        """Return the temperature sensor identifier."""
        return self._device_id

    @property
    def device_type(self) -> str:
        """Return the device type."""
        return "temperature_sensor"
    
    async def read(self) -> float:
        """Read current ambient temperature from OpenMeteo API.
        
        Returns:
            float: Current temperature in Celsius
            
        Raises:
            ConnectionError: When API is unreachable or returns error
            TimeoutError: When request exceeds timeout limit
            ValueError: When API returns invalid temperature data
        """
        params = {
            "latitude": self._latitude,
            "longitude": self._longitude,
            "current_weather": "true",
            "temperature_unit": "celsius"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(self._base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract temperature from response
                current_weather = data.get("current_weather", {})
                temperature = current_weather.get("temperature")
                
                if temperature is None:
                    raise ValueError("Invalid API response: missing temperature data")
                
                if not isinstance(temperature, (int, float)):
                    raise ValueError(f"Invalid temperature format: {type(temperature)}")
                
                return float(temperature)
                
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Temperature API request timeout: {e}")
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f"Temperature API HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise ConnectionError(f"Temperature API connection error: {e}")
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid temperature API response: {e}")
    
    async def write(self, data: Dict[str, Any]) -> None:
        """Temperature sensor is read-only device.
        
        Args:
            data: Ignored
            
        Raises:
            ValueError: Always, as temperature sensors don't support write operations
        """
        raise ValueError("Temperature sensor is read-only device; write operations not supported")
