import pytest
import asyncio
from typing import Dict, Any

from infrastructure.adapters.motor_adapter import MotorAdapter


@pytest.fixture
def motor_adapter():
    """Create a MotorAdapter instance for testing (starts stopped)."""
    return MotorAdapter(motor_id="motor_01", initial_speed=0)


@pytest.fixture
def running_motor_adapter():
    """Create a MotorAdapter instance that starts running at mid speed."""
    return MotorAdapter(motor_id="motor_02", initial_speed=128)


@pytest.mark.asyncio
async def test_motor_adapter_device_id(motor_adapter: MotorAdapter):
    """MotorAdapter should return consistent device ID."""
    assert motor_adapter.device_id == "motor_01"


@pytest.mark.asyncio
async def test_motor_adapter_device_type(motor_adapter: MotorAdapter):
    """MotorAdapter should identify as motor type."""
    assert motor_adapter.device_type == "motor"


@pytest.mark.asyncio
async def test_motor_read_returns_integer_speed(motor_adapter: MotorAdapter):
    """MotorAdapter read() should return integer speed in PWM range."""
    speed = await motor_adapter.read()
    assert isinstance(speed, int)
    assert 0 <= speed <= 255
    # Initial speed should be 0 (stopped)
    assert speed == 0


@pytest.mark.asyncio
async def test_motor_write_changes_speed(motor_adapter: MotorAdapter):
    """MotorAdapter write() should change motor speed and be readable."""
    # Start at 0, set to half speed
    await motor_adapter.write({"speed": 128})
    speed = await motor_adapter.read()
    assert speed == 128
    
    # Set to full speed
    await motor_adapter.write({"speed": 255})
    speed = await motor_adapter.read()
    assert speed == 255
    
    # Stop motor
    await motor_adapter.write({"speed": 0})
    speed = await motor_adapter.read()
    assert speed == 0


@pytest.mark.asyncio
async def test_motor_write_validates_speed_range(motor_adapter: MotorAdapter):
    """MotorAdapter write() should validate PWM range (0-255)."""
    # Test negative speed
    with pytest.raises(ValueError, match="must be in range 0-255"):
        await motor_adapter.write({"speed": -1})
    
    # Test speed too high
    with pytest.raises(ValueError, match="must be in range 0-255"):
        await motor_adapter.write({"speed": 256})


@pytest.mark.asyncio
async def test_motor_write_validates_payload_format(motor_adapter: MotorAdapter):
    """MotorAdapter write() should validate payload format."""
    # Missing speed key
    with pytest.raises(ValueError, match="'speed' key required"):
        await motor_adapter.write({"power": 100})
    
    # Non-integer speed
    with pytest.raises(ValueError, match="'speed' must be integer"):
        await motor_adapter.write({"speed": "fast"})


@pytest.mark.asyncio
async def test_motor_get_status_online_when_working(running_motor_adapter: MotorAdapter):
    """MotorAdapter get_status() should return online status with current speed."""
    status = await running_motor_adapter.get_status()
    
    assert status["device_id"] == "motor_02"
    assert status["device_type"] == "motor"
    assert status["status"] == "online"
    assert "data" in status
    assert status["data"] == 128


@pytest.mark.asyncio
async def test_motor_read_has_realistic_delay():
    """MotorAdapter read() should have random delay to simulate real I/O."""
    motor = MotorAdapter("test_motor", 100)
    
    # Measure multiple read operations
    times = []
    for _ in range(3):
        start = asyncio.get_event_loop().time()
        await motor.read()
        end = asyncio.get_event_loop().time()
        times.append(end - start)
    
    # Should have some delay (> 0.01s) and variability
    assert all(t > 0.01 for t in times), "Read operations should have realistic delay"
    assert max(times) - min(times) > 0.005, "Read delays should be variable"


@pytest.mark.asyncio
async def test_motor_initialization_validates_range():
    """MotorAdapter constructor should validate initial speed range."""
    # Valid ranges
    MotorAdapter("test1", 0)    # min speed
    MotorAdapter("test2", 255)  # max speed
    MotorAdapter("test3", 128)  # mid speed
    
    # Invalid ranges
    with pytest.raises(ValueError, match="Initial speed must be in range 0-255"):
        MotorAdapter("test4", -1)
    
    with pytest.raises(ValueError, match="Initial speed must be in range 0-255"):
        MotorAdapter("test5", 256)
