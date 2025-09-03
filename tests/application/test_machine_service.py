"""Tests for MachineControlService."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from application.machine_service import MachineControlService
from domain.ports.io_device import IODevice


@pytest.fixture
def mock_motor():
    """Create a mock motor device."""
    motor = AsyncMock(spec=IODevice)
    motor.device_id = "motor_01"
    motor.device_type = "motor"
    motor.read = AsyncMock(return_value=100)
    motor.write = AsyncMock()
    motor.get_status = AsyncMock(return_value={
        "device_id": "motor_01",
        "device_type": "motor", 
        "status": "online",
        "data": 100
    })
    return motor


@pytest.fixture
def mock_valve():
    """Create a mock valve device."""
    valve = AsyncMock(spec=IODevice)
    valve.device_id = "valve_01"
    valve.device_type = "valve"
    valve.read = AsyncMock(return_value=False)
    valve.write = AsyncMock()
    valve.get_status = AsyncMock(return_value={
        "device_id": "valve_01",
        "device_type": "valve",
        "status": "online", 
        "data": False
    })
    return valve


@pytest.fixture
def mock_temperature_sensor():
    """Create a mock temperature sensor."""
    sensor = AsyncMock(spec=IODevice)
    sensor.device_id = "temp_01"
    sensor.device_type = "temperature_sensor"
    sensor.read = AsyncMock(return_value=23.5)
    sensor.write = AsyncMock(side_effect=ValueError("Temperature sensor is read-only"))
    sensor.get_status = AsyncMock(return_value={
        "device_id": "temp_01",
        "device_type": "temperature_sensor",
        "status": "online",
        "data": 23.5
    })
    return sensor


@pytest.fixture
def mock_servo():
    """Create a mock servo device."""
    servo = AsyncMock(spec=IODevice)
    servo.device_id = "servo_01"
    servo.device_type = "servo"
    servo.read = AsyncMock(return_value=90)
    servo.write = AsyncMock()
    servo.get_status = AsyncMock(return_value={
        "device_id": "servo_01",
        "device_type": "servo",
        "status": "online",
        "data": 90
    })
    return servo


@pytest.fixture
def machine_service(mock_motor, mock_valve, mock_temperature_sensor, mock_servo):
    """Create a MachineControlService with mocked devices."""
    devices = [mock_motor, mock_valve, mock_temperature_sensor, mock_servo]
    return MachineControlService(devices)


class TestMachineControlService:
    """Test suite for MachineControlService."""
    
    def test_service_initialization(self, machine_service, mock_motor, mock_valve):
        """Service should initialize with devices correctly grouped."""
        # Test device count
        assert len(machine_service.devices) == 4
        
        # Test device lookup by ID
        assert machine_service.get_device_by_id("motor_01") == mock_motor
        assert machine_service.get_device_by_id("valve_01") == mock_valve
        assert machine_service.get_device_by_id("nonexistent") is None
        
        # Test device lookup by type
        motors = machine_service.get_devices_by_type("motor")
        assert len(motors) == 1
        assert motors[0] == mock_motor
        
        valves = machine_service.get_devices_by_type("valve")
        assert len(valves) == 1
        assert valves[0] == mock_valve
    
    @pytest.mark.asyncio
    async def test_read_device_success(self, machine_service, mock_motor):
        """Should read data from device by ID."""
        result = await machine_service.read_device("motor_01")
        
        assert result == 100
        mock_motor.read.assert_called_once()
    
    @pytest.mark.asyncio 
    async def test_read_device_not_found(self, machine_service):
        """Should raise ValueError for nonexistent device."""
        with pytest.raises(ValueError, match="Device nonexistent not found"):
            await machine_service.read_device("nonexistent")
    
    @pytest.mark.asyncio
    async def test_write_device_success(self, machine_service, mock_valve):
        """Should write data to device by ID."""
        await machine_service.write_device("valve_01", {"value": True})
        
        mock_valve.write.assert_called_once_with({"value": True})
    
    @pytest.mark.asyncio
    async def test_write_device_not_found(self, machine_service):
        """Should raise ValueError for nonexistent device."""
        with pytest.raises(ValueError, match="Device nonexistent not found"):
            await machine_service.write_device("nonexistent", {"value": 123})
    
    @pytest.mark.asyncio
    async def test_get_device_status(self, machine_service, mock_temperature_sensor):
        """Should get status from device by ID."""
        status = await machine_service.get_device_status("temp_01")
        
        assert status["device_id"] == "temp_01"
        assert status["status"] == "online"
        assert status["data"] == 23.5
        mock_temperature_sensor.get_status.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_statuses(self, machine_service):
        """Should get status from all devices."""
        statuses = await machine_service.get_all_statuses()
        
        assert len(statuses) == 4
        assert "motor_01" in statuses
        assert "valve_01" in statuses
        assert "temp_01" in statuses
        assert "servo_01" in statuses
        
        # Check that all devices were called
        for device in machine_service.devices:
            device.get_status.assert_called_once()
    
    def test_list_devices(self, machine_service):
        """Should list all devices with basic info."""
        devices_info = machine_service.list_devices()
        
        assert len(devices_info) == 4
        
        device_ids = [info["device_id"] for info in devices_info]
        device_types = [info["device_type"] for info in devices_info]
        
        assert "motor_01" in device_ids
        assert "valve_01" in device_ids
        assert "temp_01" in device_ids
        assert "servo_01" in device_ids
        
        assert "motor" in device_types
        assert "valve" in device_types
        assert "temperature_sensor" in device_types
        assert "servo" in device_types


class TestMachineControlServiceConvenienceMethods:
    """Test suite for convenience methods in MachineControlService."""
    
    @pytest.mark.asyncio
    async def test_get_motor_speed(self, machine_service, mock_motor):
        """Should get motor speed using convenience method."""
        speed = await machine_service.get_motor_speed()
        
        assert speed == 100
        mock_motor.read.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_motor_speed(self, machine_service, mock_motor):
        """Should set motor speed using convenience method."""
        await machine_service.set_motor_speed(150)
        
        mock_motor.write.assert_called_once_with({"value": 150})
    
    @pytest.mark.asyncio
    async def test_get_valve_state(self, machine_service, mock_valve):
        """Should get valve state using convenience method."""
        state = await machine_service.get_valve_state()
        
        assert state is False
        mock_valve.read.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_set_valve_state(self, machine_service, mock_valve):
        """Should set valve state using convenience method."""
        await machine_service.set_valve_state(True)
        
        mock_valve.write.assert_called_once_with({"value": True})
    
    @pytest.mark.asyncio
    async def test_get_temperature(self, machine_service, mock_temperature_sensor):
        """Should get temperature using convenience method."""
        temp = await machine_service.get_temperature()
        
        assert temp == 23.5
        mock_temperature_sensor.read.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_motor_not_found(self, mock_valve, mock_temperature_sensor):
        """Should return None when no motor device exists."""
        # Service without motor
        service = MachineControlService([mock_valve, mock_temperature_sensor])
        
        speed = await service.get_motor_speed()
        assert speed is None
    
    @pytest.mark.asyncio
    async def test_set_motor_speed_no_motor(self, mock_valve, mock_temperature_sensor):
        """Should raise ValueError when trying to set speed with no motor."""
        # Service without motor
        service = MachineControlService([mock_valve, mock_temperature_sensor])
        
        with pytest.raises(ValueError, match="No motor device found"):
            await service.set_motor_speed(100)
    
    @pytest.mark.asyncio
    async def test_valve_not_found(self, mock_motor, mock_temperature_sensor):
        """Should return None when no valve device exists."""
        # Service without valve
        service = MachineControlService([mock_motor, mock_temperature_sensor])
        
        state = await service.get_valve_state()
        assert state is None
    
    @pytest.mark.asyncio
    async def test_set_valve_state_no_valve(self, mock_motor, mock_temperature_sensor):
        """Should raise ValueError when trying to set valve with no valve."""
        # Service without valve
        service = MachineControlService([mock_motor, mock_temperature_sensor])
        
        with pytest.raises(ValueError, match="No valve device found"):
            await service.set_valve_state(True)
    
    @pytest.mark.asyncio
    async def test_temperature_not_found(self, mock_motor, mock_valve):
        """Should return None when no temperature sensor exists."""
        # Service without temperature sensor
        service = MachineControlService([mock_motor, mock_valve])
        
        temp = await service.get_temperature()
        assert temp is None
