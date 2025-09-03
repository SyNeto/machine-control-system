"""Dependency injection integration for FastAPI.

This module provides FastAPI dependencies that integrate with the
dependency injection container to provide services to API endpoints.
"""

from typing import Iterator

from fastapi import Depends

from src.application.machine_service import MachineControlService
from src.infrastructure.di.factory import get_container


def get_machine_service() -> Iterator[MachineControlService]:
    """FastAPI dependency to get MachineControlService.
    
    This function acts as a FastAPI dependency that retrieves the
    MachineControlService from the DI container. It uses a generator
    pattern to ensure proper lifecycle management.
    
    Yields:
        MachineControlService: Configured service instance.
    """
    container = get_container()
    service = container.machine_control_service()
    try:
        yield service
    finally:
        # Any cleanup if needed
        pass


# Type alias for dependency injection
MachineServiceDep = Depends(get_machine_service)
