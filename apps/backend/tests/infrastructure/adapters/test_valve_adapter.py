import pytest
import asyncio
from typing import Dict, Any

from infrastructure.adapters.valve_adapter import ValveAdapter
from .fixtures.valve_fixtures import valve_adapter, open_valve_adapter


@pytest.mark.asyncio
async def test_valve_adapter_device_id(valve_adapter: ValveAdapter):
    """ValveAdapter should return consistent device ID."""
    assert valve_adapter.device_id == "valve_01"


@pytest.mark.asyncio
async def test_valve_adapter_device_type(valve_adapter: ValveAdapter):
    """ValveAdapter should identify as valve type."""
    assert valve_adapter.device_type == "valve"


@pytest.mark.asyncio
async def test_valve_read_returns_boolean_state(valve_adapter: ValveAdapter):
    """ValveAdapter read() should return boolean valve state (open/closed)."""
    state = await valve_adapter.read()
    assert isinstance(state, bool)
    # Initial state should be False (closed)
    assert state is False


@pytest.mark.asyncio
async def test_valve_write_changes_state(valve_adapter: ValveAdapter):
    """ValveAdapter write() should change valve state and be readable."""
    # Start closed, open it
    await valve_adapter.write({"value": True})
    state = await valve_adapter.read()
    assert state is True
    
    # Close it again
    await valve_adapter.write({"value": False})
    state = await valve_adapter.read()
    assert state is False


@pytest.mark.asyncio
async def test_valve_write_with_invalid_payload_raises_error(valve_adapter: ValveAdapter):
    """ValveAdapter write() should raise ValueError for invalid payload."""
    with pytest.raises(ValueError, match="Invalid payload"):
        await valve_adapter.write({"invalid_key": "some_value"})


@pytest.mark.asyncio
async def test_valve_get_status_online_when_working(valve_adapter: ValveAdapter):
    """ValveAdapter get_status() should return online status with current state."""
    status = await valve_adapter.get_status()
    
    assert status["device_id"] == "valve_01"
    assert status["device_type"] == "valve"
    assert status["status"] == "online"
    assert "data" in status
    assert isinstance(status["data"], bool)


@pytest.mark.asyncio
async def test_valve_read_has_realistic_delay():
    """ValveAdapter read() should have random delay to simulate real I/O."""
    valve = ValveAdapter("test_valve", False)
    
    # Measure multiple read operations
    times = []
    for _ in range(3):
        start = asyncio.get_event_loop().time()
        await valve.read()
        end = asyncio.get_event_loop().time()
        times.append(end - start)
    
    # Should have some delay (> 0.01s) and variability
    assert all(t > 0.01 for t in times), "Read operations should have realistic delay"
    assert max(times) - min(times) > 0.005, "Read delays should be variable"


@pytest.mark.asyncio
async def test_valve_concurrent_operations_are_safe(valve_adapter: ValveAdapter):
    """ValveAdapter should handle concurrent read/write operations safely."""
    async def read_operation():
        return await valve_adapter.read()
    
    async def write_operation():
        await valve_adapter.write({"value": True})
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
