"""Configuration loader and DI container factory."""

import os
from pathlib import Path
from src.infrastructure.di.containers import DeviceContainer, ApplicationContainer


def create_device_container(config_path: str = None) -> DeviceContainer:
    """Create and configure the device container with YAML config.
    
    Args:
        config_path: Path to YAML configuration file. 
                    Defaults to config/devices.yaml
    
    Returns:
        DeviceContainer: Configured container with all devices
    """
    if config_path is None:
        # Default config path relative to project root
        project_root = Path(__file__).parent.parent.parent.parent
        config_path = project_root / "config" / "devices.yaml"
    
    container = DeviceContainer()
    container.config.from_yaml(str(config_path))
    
    return container


def create_application_container(config_path: str = None) -> ApplicationContainer:
    """Create the main application container.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        ApplicationContainer: Main application container
    """
    device_container = create_device_container(config_path)
    
    app_container = ApplicationContainer()
    app_container.devices.override(device_container)
    
    return app_container


# Global container instance (lazy-loaded)
_container = None


def get_container() -> ApplicationContainer:
    """Get the global application container (singleton pattern).
    
    Returns:
        ApplicationContainer: The global container instance
    """
    global _container
    if _container is None:
        _container = create_application_container()
    return _container


def reset_container():
    """Reset the global container (useful for testing)."""
    global _container
    _container = None
