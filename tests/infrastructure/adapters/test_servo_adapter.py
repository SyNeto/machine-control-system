import pytest
import asyncio
from typing import Dict, Any

from infrastructure.adapters.servo_adapter import ServoAdapter


@pytest.fixture
def servo_adapter():
    """Create a ServoAdapter instance for testing (starts at center position)."""
    return ServoAdapter(servo_id="servo_01", initial_angle=90)


@pytest.fixture
def servo_at_zero():
    """Create a ServoAdapter instance that starts at 0 degrees."""
    return ServoAdapter(servo_id="servo_02", initial_angle=0)


@pytest.fixture
def servo_at_max():
    """Create a ServoAdapter instance that starts at 180 degrees."""
    return ServoAdapter(servo_id="servo_03", initial_angle=180)


@pytest.mark.asyncio
async def test_servo_adapter_device_id(servo_adapter: ServoAdapter):
    """ServoAdapter should return consistent device ID."""
    assert servo_adapter.device_id == "servo_01"


@pytest.mark.asyncio
async def test_servo_adapter_device_type(servo_adapter: ServoAdapter):
    """ServoAdapter should identify as servo type."""
    assert servo_adapter.device_type == "servo"


@pytest.mark.asyncio
async def test_servo_read_returns_integer_angle(servo_adapter: ServoAdapter):
    """ServoAdapter read() should return integer angle in valid range."""
    angle = await servo_adapter.read()
    assert isinstance(angle, int)
    assert 0 <= angle <= 180
    # Initial angle should be 90 (center)
    assert angle == 90


@pytest.mark.asyncio
async def test_servo_write_changes_angle(servo_adapter: ServoAdapter):
    """ServoAdapter write() should change servo angle and be readable."""
    # Start at center (90), move to 0
    await servo_adapter.write({"angle": 0})
    angle = await servo_adapter.read()
    assert angle == 0
    
    # Move to max position
    await servo_adapter.write({"angle": 180})
    angle = await servo_adapter.read()
    assert angle == 180
    
    # Move to 45 degrees
    await servo_adapter.write({"angle": 45})
    angle = await servo_adapter.read()
    assert angle == 45


@pytest.mark.asyncio
async def test_servo_write_validates_angle_range(servo_adapter: ServoAdapter):
    """ServoAdapter write() should validate angle range (0-180)."""
    # Test negative angle
    with pytest.raises(ValueError, match="must be in range 0-180"):
        await servo_adapter.write({"angle": -1})
    
    # Test angle too high
    with pytest.raises(ValueError, match="must be in range 0-180"):
        await servo_adapter.write({"angle": 181})


@pytest.mark.asyncio
async def test_servo_write_validates_payload_format(servo_adapter: ServoAdapter):
    """ServoAdapter write() should validate payload format."""
    # Missing angle key
    with pytest.raises(ValueError, match="'angle' key required"):
        await servo_adapter.write({"position": 90})
    
    # Non-integer angle
    with pytest.raises(ValueError, match="'angle' must be integer"):
        await servo_adapter.write({"angle": 90.5})


@pytest.mark.asyncio
async def test_servo_get_status_online_when_working(servo_at_zero: ServoAdapter):
    """ServoAdapter get_status() should return online status with current angle."""
    status = await servo_at_zero.get_status()
    
    assert status["device_id"] == "servo_02"
    assert status["device_type"] == "servo"
    assert status["status"] == "online"
    assert "data" in status
    assert status["data"] == 0


@pytest.mark.asyncio
async def test_servo_read_has_realistic_delay():
    """ServoAdapter read() should have random delay to simulate real I/O."""
    servo = ServoAdapter("test_servo", 90)
    
    # Measure multiple read operations
    times = []
    for _ in range(3):
        start = asyncio.get_event_loop().time()
        await servo.read()
        end = asyncio.get_event_loop().time()
        times.append(end - start)
    
    # Should have some delay (> 0.015s) and variability
    assert all(t > 0.015 for t in times), "Read operations should have realistic delay"
    assert max(times) - min(times) > 0.005, "Read delays should be variable"


@pytest.mark.asyncio
async def test_servo_movement_delay_proportional_to_distance():
    """ServoAdapter write() delay should be proportional to movement distance."""
    servo = ServoAdapter("test_servo", 90)
    
    # Small movement (90 -> 95)
    start = asyncio.get_event_loop().time()
    await servo.write({"angle": 95})
    small_move_time = asyncio.get_event_loop().time() - start
    
    # Large movement (95 -> 0)
    start = asyncio.get_event_loop().time()
    await servo.write({"angle": 0})
    large_move_time = asyncio.get_event_loop().time() - start
    
    # Large movement should take longer than small movement
    assert large_move_time > small_move_time, "Large movements should take longer"


@pytest.mark.asyncio
async def test_servo_initialization_validates_range():
    """ServoAdapter constructor should validate initial angle range."""
    # Valid ranges
    ServoAdapter("test1", 0)    # min angle
    ServoAdapter("test2", 180)  # max angle
    ServoAdapter("test3", 90)   # center angle
    
    # Invalid ranges
    with pytest.raises(ValueError, match="Initial angle must be in range 0-180"):
        ServoAdapter("test4", -1)
    
    with pytest.raises(ValueError, match="Initial angle must be in range 0-180"):
        ServoAdapter("test5", 181)


@pytest.mark.asyncio
async def test_servo_concurrent_operations_are_safe(servo_adapter: ServoAdapter):
    """ServoAdapter should handle concurrent read/write operations safely."""
    async def read_operation():
        return await servo_adapter.read()
    
    async def write_operation():
        await servo_adapter.write({"angle": 45})
        return True
    
    # Run concurrent operations
    results = await asyncio.gather(
        read_operation(),
        write_operation(),
        read_operation(),
        return_exceptions=True
    )
    
    # No exceptions should be raised
    assert all(not isinstance(r, Exception) for r in results)
