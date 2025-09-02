import asyncio
import pytest

from domain.ports.io_device import IODevice
from .fixtures.io_device_fixtures import DummyDevice, failing_device, make_dummy_device, dummy_device


@pytest.mark.asyncio
async def test_get_status_happy_path(dummy_device: DummyDevice):
    """Returns 'online' status and correct metadata when read() succeeds."""
    # Given a working device with an initial value
    dev = dummy_device
    # When
    status = await dev.get_status()
    # Then
    assert status["device_id"] == dev.device_id
    assert status["device_type"] == dev.device_type
    assert status["status"] == "online"
    assert status["data"] == 0


@pytest.mark.asyncio
async def test_get_status_error_path(failing_device: DummyDevice):
    """Returns 'error' status and exception message when read() fails."""
    dev = failing_device
    status = await dev.get_status()
    assert status["device_id"] == dev.device_id
    assert status["device_type"] == dev.device_type
    assert status["status"] == "error"
    assert "read failed" in status["message"]


@pytest.mark.asyncio
async def test_write_then_read_updates_value(make_dummy_device):
    """write() updates the value and then read() returns it."""
    dev: IODevice = make_dummy_device("d3", "sensor", 10)
    await dev.write({"value": 99})
    out = await dev.read()
    assert out == 99


@pytest.mark.asyncio
async def test_concurrent_get_status_calls_share_result(dummy_device: DummyDevice):
    """Concurrent get_status() calls are consistent and increment read counter."""
    dev = dummy_device

    async def call():
        return await dev.get_status()

    results = await asyncio.gather(*[call() for _ in range(5)])
    assert all(r["status"] == "online" for r in results)
    # read() should have been called once per get_status invocation
    assert dev.read_count == 5
