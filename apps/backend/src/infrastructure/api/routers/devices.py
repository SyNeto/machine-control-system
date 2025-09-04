"""Device control REST API endpoints.

This module provides RESTful endpoints for controlling and monitoring
devices with a generic approach that works for all device types.
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from src.application.machine_service import MachineControlService
from src.infrastructure.api.dependencies import MachineServiceDep
from src.infrastructure.api.models.requests import DeviceUpdateRequest
from src.infrastructure.api.models.responses import (
    DeviceUpdateResponse,
    DeviceStatusResponse,
    ErrorResponse
)

# Import WebSocket broadcast function
try:
    from src.infrastructure.api.websockets.endpoints import broadcast_device_change
except ImportError:
    # Fallback if WebSocket module not available
    async def broadcast_device_change(*args, **kwargs):
        pass

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/{device_id}", response_model=DeviceUpdateResponse)
async def update_device(
    device_id: str,
    request: DeviceUpdateRequest,
    machine_service: MachineControlService = MachineServiceDep
) -> DeviceUpdateResponse:
    """Update device state (motor speed, servo angle, valve state).
    
    This is the main RESTful endpoint for controlling all device types:
    - Motor: {"speed": 128} (0-255)
    - Servo: {"angle": 90.5} (0-180)
    - Valve: {"state": true} (true/false)
    
    Args:
        device_id: Device identifier.
        request: Device update request with appropriate fields.
        machine_service: Injected machine control service.
        
    Returns:
        DeviceUpdateResponse: Result with previous/new state and change status.
        
    Raises:
        HTTPException: If device not found, invalid request, or operation fails.
    """
    try:
        # Get device
        device = machine_service.get_device_by_id(device_id)
        if not device:
            raise HTTPException(
                status_code=404,
                detail=f"Device '{device_id}' not found"
            )
        
        # Get current state before change
        current_data = await device.read()
        
        # Handle different device return types
        if device.device_type == "valve":
            # Valve returns boolean directly
            previous_state = {"value": current_data}
        elif device.device_type == "motor":
            # Motor returns number directly
            previous_state = {"speed": current_data} if isinstance(current_data, (int, float)) else current_data.copy()
        elif device.device_type == "servo":
            # Servo returns number directly
            previous_state = {"angle": current_data} if isinstance(current_data, (int, float)) else current_data.copy()
        else:
            # Generic handling for other device types
            previous_state = current_data.copy() if isinstance(current_data, dict) else {"value": current_data}
        
        # Build update payload based on device type and request
        update_payload = {}
        field_name = None
        new_value = None
        
        if device.device_type == "motor":
            if request.speed is not None:
                update_payload = {"speed": request.speed}
                field_name = "speed"
                new_value = request.speed
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Motor devices require 'speed' field (0-255)"
                )
                
        elif device.device_type == "servo":
            if request.angle is not None:
                # Convert float to int for servo adapter compatibility
                angle_int = int(round(request.angle))
                update_payload = {"angle": angle_int}
                field_name = "angle"
                new_value = angle_int
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Servo devices require 'angle' field (0-180)"
                )
                
        elif device.device_type == "valve":
            if request.state is not None:
                # Valve adapter expects "value" key, not "state"
                update_payload = {"value": request.state}
                field_name = "value"  # For consistency with adapter
                new_value = request.state
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Valve devices require 'state' field (true/false)"
                )
                
        elif device.device_type == "temperature":
            raise HTTPException(
                status_code=400,
                detail="Temperature sensors are read-only devices"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown device type: {device.device_type}"
            )
        
        # Apply the update
        await device.write(update_payload)
        
        # Verify the change
        updated_data = await device.read()
        
        # Handle different device return types
        if device.device_type == "valve":
            # Valve returns boolean directly
            new_state = {"value": updated_data}
            previous_value = previous_state["value"]
            current_value = updated_data
        elif device.device_type == "motor":
            # Motor returns number directly, but we need to structure it correctly
            new_state = {"speed": updated_data} if isinstance(updated_data, (int, float)) else updated_data.copy()
            previous_value = previous_state.get("speed", previous_state.get("value", 0))
            current_value = new_state.get("speed", new_state.get("value", 0))
        elif device.device_type == "servo":
            # Servo returns number directly, but we need to structure it correctly
            new_state = {"angle": updated_data} if isinstance(updated_data, (int, float)) else updated_data.copy()
            previous_value = previous_state.get("angle", previous_state.get("value", 0))
            current_value = new_state.get("angle", new_state.get("value", 0))
        else:
            # Generic handling for other device types
            new_state = updated_data.copy() if isinstance(updated_data, dict) else {"value": updated_data}
            previous_value = previous_state.get(field_name, 0)
            current_value = new_state.get(field_name, 0)
        
        # Check if state actually changed
        # For numeric values, allow small float precision differences
        if isinstance(previous_value, (int, float)) and isinstance(current_value, (int, float)):
            changed = abs(current_value - previous_value) > 0.01
        else:
            changed = previous_value != current_value
        
        # Generate descriptive message
        if device.device_type == "motor":
            message = f"Motor speed {'changed' if changed else 'unchanged'}: {previous_value} → {current_value}"
        elif device.device_type == "servo":
            message = f"Servo position {'changed' if changed else 'unchanged'}: {previous_value}° → {current_value}°"
        elif device.device_type == "valve":
            state_text = lambda s: "open" if s else "closed"
            message = f"Valve state {'changed' if changed else 'unchanged'}: {state_text(previous_value)} → {state_text(current_value)}"
        else:
            message = f"Device {'updated' if changed else 'unchanged'}"
        
        # Generate response
        response = DeviceUpdateResponse(
            device_id=device_id,
            device_type=device.device_type,
            previous_state=previous_state,
            new_state=new_state,
            status="success" if changed else "no_change",
            message=message,
            changed=changed
        )
        
        # Broadcast the change to WebSocket clients (fire and forget)
        try:
            asyncio.create_task(broadcast_device_change(
                device_id=device_id,
                device_type=device.device_type,
                previous_state=previous_state,
                new_state=new_state,
                changed=changed,
                action="device_control"
            ))
        except Exception as broadcast_error:
            # Don't fail the main request if broadcast fails
            logger.warning(f"WebSocket broadcast failed: {broadcast_error}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update device: {str(e)}"
        )


@router.get("/", response_model=Dict[str, DeviceStatusResponse])
async def list_devices(
    machine_service: MachineControlService = MachineServiceDep
) -> Dict[str, DeviceStatusResponse]:
    """List all devices with their current status.
    
    Args:
        machine_service: Injected machine control service.
        
    Returns:
        Dict mapping device IDs to their status information.
    """
    devices_status = {}
    
    for device in machine_service.devices:
        try:
            current_data = await device.read()
            status_info = await device.get_status()
            
            devices_status[device.device_id] = DeviceStatusResponse(
                device_id=device.device_id,
                device_type=device.device_type,
                status=status_info["status"],  # Extract string from status dict
                current_value=current_data
            )
        except Exception as e:
            devices_status[device.device_id] = DeviceStatusResponse(
                device_id=device.device_id,
                device_type=device.device_type,
                status="error",
                current_value=f"Error: {str(e)}"
            )
    
    return devices_status


@router.get("/{device_id}", response_model=DeviceStatusResponse)
async def get_device_status(
    device_id: str,
    machine_service: MachineControlService = MachineServiceDep
) -> DeviceStatusResponse:
    """Get status of a specific device.
    
    Args:
        device_id: Device identifier.
        machine_service: Injected machine control service.
        
    Returns:
        DeviceStatusResponse: Current device status and value.
        
    Raises:
        HTTPException: If device not found.
    """
    device = machine_service.get_device_by_id(device_id)
    if not device:
        raise HTTPException(
            status_code=404,
            detail=f"Device '{device_id}' not found"
        )
    
    try:
        current_data = await device.read()
        status_info = await device.get_status()
        
        return DeviceStatusResponse(
            device_id=device.device_id,
            device_type=device.device_type,
            status=status_info["status"],  # Extract string from status dict
            current_value=current_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get device status: {str(e)}"
        )
