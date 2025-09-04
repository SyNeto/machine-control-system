"""FastAPI application setup and configuration.

This module provides the main FastAPI application instance with basic
configuration, health check endpoints, dependency injection wiring,
and device control routers.
"""

from fastapi import FastAPI

from src.application.machine_service import MachineControlService
from src.infrastructure.api.dependencies import MachineServiceDep
from src.infrastructure.api.routers import devices


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
    
    # Include API routers
    app.include_router(devices.router, prefix="/api/v1")
    
    # Include WebSocket router
    try:
        from src.infrastructure.api.websockets import endpoints as ws_endpoints
        app.include_router(ws_endpoints.router)
    except ImportError:
        # WebSockets not available, skip
        pass
    
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
                status_info = await device.get_status()
                device_status[device.device_id] = "connected" if status_info["status"] == "online" else "disconnected"
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
                "devices": "/api/v1/devices",  # Add this back for compatibility
                "devices_list": "/api/v1/devices",
                "device_status": "/api/v1/devices/{device_id}",
                "device_control": "/api/v1/devices/{device_id}",  # New generic endpoint
                "websocket_devices": "/ws/devices",  # WebSocket endpoint
                "websocket": "/ws/devices"  # Keep both for compatibility
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
