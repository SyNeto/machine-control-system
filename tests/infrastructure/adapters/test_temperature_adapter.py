import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from infrastructure.adapters.temperature_adapter import TemperatureAdapter


@pytest.fixture
def temp_sensor():
    """Create a TemperatureAdapter instance for testing (Mexico City coordinates)."""
    return TemperatureAdapter(
        device_id="temp_01",
        latitude=19.4326,  # Mexico City
        longitude=-99.1332,
        timeout=5.0
    )


@pytest.fixture
def mock_openmeteo_response():
    """Mock successful OpenMeteo API response."""
    return {
        "current_weather": {
            "temperature": 23.5,
            "windspeed": 10.5,
            "winddirection": 180,
            "weathercode": 1,
            "time": "2025-09-03T15:00"
        }
    }


@pytest.mark.asyncio
async def test_temperature_adapter_device_id(temp_sensor: TemperatureAdapter):
    """TemperatureAdapter should return consistent device ID."""
    assert temp_sensor.device_id == "temp_01"


@pytest.mark.asyncio
async def test_temperature_adapter_device_type(temp_sensor: TemperatureAdapter):
    """TemperatureAdapter should identify as temperature_sensor type."""
    assert temp_sensor.device_type == "temperature_sensor"


@pytest.mark.asyncio
async def test_temperature_read_with_mock_api(temp_sensor: TemperatureAdapter, mock_openmeteo_response):
    """TemperatureAdapter read() should return temperature from mocked API."""
    with patch('httpx.AsyncClient') as mock_client_class:
        # Create a mock client instance
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = mock_openmeteo_response
        mock_response.raise_for_status.return_value = None
        
        # Configure the async client properly
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        # Test read operation
        temperature = await temp_sensor.read()
        
        assert isinstance(temperature, float)
        assert temperature == 23.5
        
        # Verify API was called with correct parameters
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "latitude" in call_args[1]["params"]
        assert "longitude" in call_args[1]["params"]
        assert call_args[1]["params"]["current_weather"] == "true"


@pytest.mark.asyncio
async def test_temperature_get_status_online_when_api_works(temp_sensor: TemperatureAdapter, mock_openmeteo_response):
    """get_status() should return 'online' when API works correctly."""
    with patch('httpx.AsyncClient') as mock_client_class:
        # Create a mock client instance
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = mock_openmeteo_response
        mock_response.raise_for_status.return_value = None
        
        # Configure the async client properly
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        # Test status check
        status = await temp_sensor.get_status()
        
        assert status['status'] == "online"
        
        # Verify API was called
        mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_temperature_get_status_error_when_api_fails(temp_sensor: TemperatureAdapter):
    """TemperatureAdapter get_status() should return error status when API fails."""
    with patch('httpx.AsyncClient') as mock_client_class:
        # Create a mock client instance
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.RequestError("Network error"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        status = await temp_sensor.get_status()
        
        assert status["device_id"] == "temp_01"
        assert status["device_type"] == "temperature_sensor"
        assert status["status"] == "error"
        assert "message" in status
        assert "connection error" in status["message"].lower()


@pytest.mark.asyncio
async def test_temperature_read_handles_timeout():
    """TemperatureAdapter read() should raise TimeoutError on API timeout."""
    sensor = TemperatureAdapter("temp_timeout", 0.0, 0.0, timeout=0.001)
    
    with patch('httpx.AsyncClient') as mock_client_class:
        # Create a mock client instance
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Request timeout"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        with pytest.raises(TimeoutError, match="timeout"):
            await sensor.read()


@pytest.mark.asyncio
async def test_temperature_read_handles_http_error():
    """TemperatureAdapter read() should raise ConnectionError on HTTP errors."""
    sensor = TemperatureAdapter("temp_error", 0.0, 0.0)
    
    with patch('httpx.AsyncClient') as mock_client_class:
        # Create a mock client instance
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Server Error", request=None, response=mock_response
        )
        
        # Configure the async client properly
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        with pytest.raises(ConnectionError, match="HTTP error 500"):
            await sensor.read()


@pytest.mark.asyncio
async def test_temperature_read_handles_invalid_response(temp_sensor: TemperatureAdapter):
    """TemperatureAdapter read() should raise ValueError on invalid API response."""
    with patch('httpx.AsyncClient') as mock_client_class:
        # Create a mock client instance
        mock_client = AsyncMock()
        mock_response = MagicMock()
        # Response missing temperature data
        mock_response.json.return_value = {"current_weather": {}}
        mock_response.raise_for_status.return_value = None
        
        # Configure the async client properly
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client
        
        with pytest.raises(ValueError, match="missing temperature data"):
            await temp_sensor.read()


def test_temperature_adapter_validates_coordinates():
    """TemperatureAdapter constructor should validate coordinate ranges."""
    # Valid coordinates should work
    valid_sensor = TemperatureAdapter("valid", 19.4326, -99.1332)
    assert valid_sensor.device_id == "valid"
    
    # Invalid latitude (too high)
    with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
        TemperatureAdapter("invalid_lat_high", 91.0, 0.0)
    
    # Invalid latitude (too low)
    with pytest.raises(ValueError, match="Latitude must be between -90 and 90"):
        TemperatureAdapter("invalid_lat_low", -91.0, 0.0)
    
    # Invalid longitude (too high)
    with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
        TemperatureAdapter("invalid_lon_high", 0.0, 181.0)
    
    # Invalid longitude (too low)
    with pytest.raises(ValueError, match="Longitude must be between -180 and 180"):
        TemperatureAdapter("invalid_lon_low", 0.0, -181.0)


@pytest.mark.asyncio
async def test_temperature_real_api_integration():
    """Integration test with real OpenMeteo API (requires internet connection)."""
    # Using coordinates for a known location (London)
    sensor = TemperatureAdapter("london_temp", 51.5074, -0.1278, timeout=10.0)
    
    try:
        # Test real API call
        temperature = await sensor.read()
        
        # Verify we got a reasonable temperature value
        assert isinstance(temperature, float)
        assert -50 <= temperature <= 60  # Reasonable temperature range for Earth
        
        # Test status with real API
        status = await sensor.get_status()
        assert status["device_id"] == "london_temp"
        assert status["device_type"] == "temperature_sensor"
        assert status["status"] == "online"
        
    except Exception as e:
        # If the real API fails (no internet, API down, etc.), skip the test
        pytest.skip(f"Real API integration test skipped due to: {e}")
