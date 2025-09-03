import pytest
from infrastructure.adapters.valve_adapter import ValveAdapter


@pytest.fixture
def valve_adapter():
    """Create a ValveAdapter instance for testing."""
    return ValveAdapter(valve_id="valve_01", initial_state=False)


@pytest.fixture
def open_valve_adapter():
    """Create a ValveAdapter instance that starts open."""
    return ValveAdapter(valve_id="valve_02", initial_state=True)
