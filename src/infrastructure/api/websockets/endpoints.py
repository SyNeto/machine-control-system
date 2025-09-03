"""WebSocket endpoints for real-time device monitoring.

This module provides WebSocket endpoints that allow clients to receive
real-time updates about device status changes and system events.
"""

import json
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
import logging

from src.application.machine_service import MachineControlService
from src.infrastructure.api.dependencies import MachineServiceDep
from src.infrastructure.api.websockets.manager import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websockets"])


@router.websocket("/devices")
async def websocket_device_monitor(
    websocket: WebSocket,
    client_id: str = Query(default="anonymous"),
    machine_service: MachineControlService = MachineServiceDep
):
    """WebSocket endpoint for real-time device monitoring.
    
    Provides live updates of device status changes, control actions,
    and system events to connected clients.
    
    Args:
        websocket: WebSocket connection.
        client_id: Optional client identifier for logging.
        machine_service: Injected machine control service.
        
    WebSocket Message Types:
        Incoming:
        - subscribe: {"action": "subscribe", "device_id": "motor_01"}
        - unsubscribe: {"action": "unsubscribe", "device_id": "motor_01"}
        - get_status: {"action": "get_status", "device_id": "motor_01"}
        - get_all_status: {"action": "get_all_status"}
        
        Outgoing:
        - device_update: Real-time device state changes
        - system_status: System-wide status updates
        - error: Error messages
        - connection_established: Welcome message
    """
    await connection_manager.connect(websocket, client_id)
    
    # Send initial device status
    try:
        initial_status = await _get_all_device_status(machine_service)
        await connection_manager._send_to_connection(websocket, {
            "type": "initial_status",
            "data": initial_status,
            "timestamp": asyncio.get_event_loop().time()
        })
    except Exception as e:
        logger.error(f"Failed to send initial status: {e}")
    
    try:
        while True:
            # Wait for incoming messages
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await _handle_websocket_message(websocket, message, machine_service)
                
            except json.JSONDecodeError:
                await connection_manager.send_error(
                    websocket, 
                    "Invalid JSON format", 
                    "json_error"
                )
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await connection_manager.send_error(
                    websocket, 
                    f"Error processing message: {str(e)}", 
                    "processing_error"
                )
                
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        await connection_manager.disconnect(websocket)


async def _handle_websocket_message(
    websocket: WebSocket, 
    message: Dict[str, Any], 
    machine_service: MachineControlService
) -> None:
    """Handle incoming WebSocket messages.
    
    Args:
        websocket: WebSocket connection.
        message: Parsed JSON message.
        machine_service: Machine control service.
    """
    action = message.get("action")
    
    if action == "subscribe":
        device_id = message.get("device_id")
        if device_id:
            await connection_manager.subscribe_to_device(websocket, device_id)
        else:
            await connection_manager.send_error(
                websocket, 
                "device_id required for subscribe action", 
                "validation_error"
            )
    
    elif action == "unsubscribe":
        device_id = message.get("device_id")
        if device_id:
            await connection_manager.unsubscribe_from_device(websocket, device_id)
        else:
            await connection_manager.send_error(
                websocket, 
                "device_id required for unsubscribe action", 
                "validation_error"
            )
    
    elif action == "get_status":
        device_id = message.get("device_id")
        if device_id:
            device_status = await _get_device_status(machine_service, device_id)
            if device_status:
                await connection_manager._send_to_connection(websocket, {
                    "type": "device_status",
                    "device_id": device_id,
                    "data": device_status,
                    "timestamp": asyncio.get_event_loop().time()
                })
            else:
                await connection_manager.send_error(
                    websocket, 
                    f"Device {device_id} not found", 
                    "device_not_found"
                )
        else:
            await connection_manager.send_error(
                websocket, 
                "device_id required for get_status action", 
                "validation_error"
            )
    
    elif action == "get_all_status":
        all_status = await _get_all_device_status(machine_service)
        await connection_manager._send_to_connection(websocket, {
            "type": "all_device_status",
            "data": all_status,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    else:
        await connection_manager.send_error(
            websocket, 
            f"Unknown action: {action}", 
            "unknown_action"
        )


async def _get_device_status(machine_service: MachineControlService, device_id: str) -> Dict[str, Any] | None:
    """Get status of a specific device.
    
    Args:
        machine_service: Machine control service.
        device_id: Device identifier.
        
    Returns:
        Device status data or None if not found.
    """
    device = machine_service.get_device_by_id(device_id)
    if not device:
        return None
    
    try:
        current_data = await device.read()
        status_info = await device.get_status()
        
        return {
            "device_id": device.device_id,
            "device_type": device.device_type,
            "status": status_info["status"],
            "current_value": current_data,
            "last_updated": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Error reading device {device_id}: {e}")
        return {
            "device_id": device_id,
            "device_type": device.device_type,
            "status": "error",
            "current_value": f"Error: {str(e)}",
            "last_updated": asyncio.get_event_loop().time()
        }


async def _get_all_device_status(machine_service: MachineControlService) -> Dict[str, Dict[str, Any]]:
    """Get status of all devices.
    
    Args:
        machine_service: Machine control service.
        
    Returns:
        Dictionary mapping device IDs to their status.
    """
    all_status = {}
    
    for device in machine_service.devices:
        device_status = await _get_device_status(machine_service, device.device_id)
        if device_status:
            all_status[device.device_id] = device_status
    
    return all_status


# Broadcast function to be called from device endpoints
async def broadcast_device_change(
    device_id: str, 
    device_type: str,
    previous_state: Dict[str, Any],
    new_state: Dict[str, Any],
    changed: bool,
    action: str = "device_update"
) -> None:
    """Broadcast device state change to WebSocket clients.
    
    This function should be called from the device control endpoints
    to notify WebSocket clients of real-time changes.
    
    Args:
        device_id: Device that changed.
        device_type: Type of device.
        previous_state: State before change.
        new_state: State after change.
        changed: Whether the state actually changed.
        action: Type of action performed.
    """
    broadcast_data = {
        "device_id": device_id,
        "device_type": device_type,
        "previous_state": previous_state,
        "new_state": new_state,
        "changed": changed,
        "action": action,
        "last_updated": asyncio.get_event_loop().time()
    }
    
    await connection_manager.broadcast_device_update(device_id, broadcast_data)
