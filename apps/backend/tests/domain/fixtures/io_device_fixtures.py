import asyncio
from typing import Any, Dict, Callable

import pytest

from domain.ports.io_device import IODevice


class DummyDevice(IODevice):
    """A simple IODevice test double that stores a single value in memory."""

    def __init__(self, device_id: str, device_type: str, value: Any = None):
        self._id = device_id
        self._type = device_type
        self._value = value
        self.read_count = 0

    @property
    def device_id(self) -> str:
        return self._id

    @property
    def device_type(self) -> str:
        return self._type

    async def read(self) -> Any:
        self.read_count += 1
        await asyncio.sleep(0)
        return self._value

    async def write(self, data: Dict[str, Any]) -> None:
        await asyncio.sleep(0)
        if "value" in data:
            self._value = data["value"]


class FailingReadDevice(DummyDevice):
    """IODevice that raises on read to exercise error path in get_status."""

    def __init__(self, device_id: str, device_type: str, exc: Exception):
        super().__init__(device_id, device_type)
        self._exc = exc

    async def read(self) -> Any:
        await asyncio.sleep(0)
        raise self._exc


@pytest.fixture
def make_dummy_device() -> Callable[..., DummyDevice]:
    def _factory(device_id: str = "dev-1", device_type: str = "sensor", value: Any = 0) -> DummyDevice:
        return DummyDevice(device_id, device_type, value)

    return _factory


@pytest.fixture
def dummy_device(make_dummy_device: Callable[..., DummyDevice]) -> DummyDevice:
    return make_dummy_device("dev-1", "sensor", 0)


@pytest.fixture
def failing_device() -> FailingReadDevice:
    return FailingReadDevice("dev-err", "sensor", RuntimeError("read failed"))
