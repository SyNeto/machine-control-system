"""FastAPI application setup and configuration.

This module provides the main FastAPI application instance with basic
configuration, health check endpoints, and dependency injection wiring.
"""

from fastapi import FastAPI

from src.application.machine_service import MachineControlService
from src.infrastructure.api.dependencies import MachineServiceDep


def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured application instance.
    """
    app = FastAPI(
        title="Machine Control Panel API",
        description="Device control system with real-time monitoring",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    @app.get("/")
    async def root(
        machine_service: MachineControlService = MachineServiceDep
    ) -> dict[str, str | dict[str, str]]:
        """API root endpoint with service information and device status.
        
        Args:
            machine_service: Injected MachineControlService instance.
            
        Returns:
            dict: Comprehensive service information and device status.
        """
        # Get device status information
        device_status = {}
        for device in machine_service.devices:
            try:
                # Check if device is responsive
                status = await device.get_status()
                device_status[device.device_id] = "connected"
            except Exception:
                device_status[device.device_id] = "disconnected"
        
        return {
            "service": "Machine Control Panel API",
            "version": "0.1.0", 
            "status": "operational",
            "architecture": "Hexagonal Architecture with FastAPI",
            "devices": device_status,
            "endpoints": {
                "health": "/health",
                "docs": "/docs", 
                "redoc": "/redoc",
                "devices": "/devices (coming soon)",
                "websocket": "/ws (coming soon)"
            }
        }
    
    @app.get("/health")
    async def health_check(
        machine_service: MachineControlService = MachineServiceDep
    ) -> dict[str, str | int]:
        """Enhanced health check with service status.
        
        Args:
            machine_service: Injected MachineControlService instance.
            
        Returns:
            dict: Health status with service information.
        """
        # Basic check that service is available
        devices_count = len(machine_service.devices)
        
        return {
            "status": "healthy",
            "service": "Machine Control Panel API",
            "devices_count": devices_count,
            "message": "Service is running with dependency injection"
        }
    
    return app


# Application instance for uvicorn
app = create_app()
