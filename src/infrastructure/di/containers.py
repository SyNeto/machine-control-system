"""Dependency injection containers for IoT device management."""

from dependency_injector import containers, providers
from infrastructure.adapters.temperature_adapter import TemperatureAdapter
from infrastructure.adapters.valve_adapter import ValveAdapter
from infrastructure.adapters.motor_adapter import MotorAdapter
from infrastructure.adapters.servo_adapter import ServoAdapter
from application.machine_service import MachineControlService


class DeviceContainer(containers.DeclarativeContainer):
    """Simple container for IoT device dependency injection.
    
    Uses Singleton providers to ensure each device maintains its state
    throughout the application lifecycle.
    """
    
    # Configuration provider - loads from YAML
    config = providers.Configuration()
    
    # One device of each type (Singletons to maintain state)
    temperature_sensor = providers.Singleton(
        TemperatureAdapter,
        sensor_id=config.devices.temperature_sensor.id,
        latitude=config.devices.temperature_sensor.latitude,
        longitude=config.devices.temperature_sensor.longitude,
        timeout=config.devices.temperature_sensor.timeout
    )
    
    valve = providers.Singleton(
        ValveAdapter,
        device_id=config.devices.valve.id,
        initial_state=config.devices.valve.initial_state
    )
    
    motor = providers.Singleton(
        MotorAdapter,
        device_id=config.devices.motor.id,
        initial_speed=config.devices.motor.initial_speed
    )
    
    servo = providers.Singleton(
        ServoAdapter,
        device_id=config.devices.servo.id,
        initial_angle=config.devices.servo.initial_angle
    )


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container that wires all components together."""
    
    # Include device container
    devices = providers.DependenciesContainer()
    
    # Application services
    machine_control_service = providers.Singleton(
        MachineControlService,
        devices=providers.List(
            devices.temperature_sensor,
            devices.valve,
            devices.motor,
            devices.servo
        )
    )
