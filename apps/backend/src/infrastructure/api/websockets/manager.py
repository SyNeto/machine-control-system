"""WebSocket connection manager for real-time device monitoring.

This module provides a centralized WebSocket connection manager that handles
multiple client connections and broadcasts device status updates in real-time.
"""

import json
import asyncio
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts for real-time updates."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Set[WebSocket] = set()
        self.device_subscriptions: Dict[str, Set[WebSocket]] = {}
        self._broadcast_lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> None:
        """Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection to accept.
            client_id: Optional client identifier for logging.
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        
        logger.info(f"WebSocket client connected. Client ID: {client_id}. "
                   f"Total connections: {len(self.active_connections)}")
        
        # Send initial welcome message
        await self._send_to_connection(websocket, {
            "type": "connection_established",
            "message": "Connected to Machine Control Panel",
            "timestamp": asyncio.get_event_loop().time(),
            "total_connections": len(self.active_connections)
        })
    
    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection to remove.
        """
        self.active_connections.discard(websocket)
        
        # Remove from device subscriptions
        for device_id in list(self.device_subscriptions.keys()):
            self.device_subscriptions[device_id].discard(websocket)
            if not self.device_subscriptions[device_id]:
                del self.device_subscriptions[device_id]
        
        logger.info(f"WebSocket client disconnected. "
                   f"Remaining connections: {len(self.active_connections)}")
    
    async def subscribe_to_device(self, websocket: WebSocket, device_id: str) -> None:
        """Subscribe a connection to specific device updates.
        
        Args:
            websocket: WebSocket connection.
            device_id: Device ID to subscribe to.
        """
        if device_id not in self.device_subscriptions:
            self.device_subscriptions[device_id] = set()
        
        self.device_subscriptions[device_id].add(websocket)
        
        await self._send_to_connection(websocket, {
            "type": "subscription_confirmed",
            "device_id": device_id,
            "message": f"Subscribed to device {device_id}",
            "timestamp": asyncio.get_event_loop().time()
        })
        
        logger.info(f"Client subscribed to device {device_id}")
    
    async def unsubscribe_from_device(self, websocket: WebSocket, device_id: str) -> None:
        """Unsubscribe a connection from device updates.
        
        Args:
            websocket: WebSocket connection.
            device_id: Device ID to unsubscribe from.
        """
        if device_id in self.device_subscriptions:
            self.device_subscriptions[device_id].discard(websocket)
            if not self.device_subscriptions[device_id]:
                del self.device_subscriptions[device_id]
        
        await self._send_to_connection(websocket, {
            "type": "subscription_removed",
            "device_id": device_id,
            "message": f"Unsubscribed from device {device_id}",
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_device_update(self, device_id: str, device_data: Dict[str, Any]) -> None:
        """Broadcast device status update to all relevant subscribers.
        
        Args:
            device_id: Device that was updated.
            device_data: Current device state and metadata.
        """
        if not self.active_connections:
            return
        
        message = {
            "type": "device_update",
            "device_id": device_id,
            "data": device_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Send to device-specific subscribers
        device_subscribers = self.device_subscriptions.get(device_id, set())
        
        # Send to all connections (global updates)
        async with self._broadcast_lock:
            await self._broadcast_to_connections(self.active_connections, message)
        
        logger.debug(f"Broadcasted update for device {device_id} to "
                    f"{len(self.active_connections)} connections")
    
    async def broadcast_system_status(self, status_data: Dict[str, Any]) -> None:
        """Broadcast system-wide status update.
        
        Args:
            status_data: System status information.
        """
        if not self.active_connections:
            return
        
        message = {
            "type": "system_status",
            "data": status_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        async with self._broadcast_lock:
            await self._broadcast_to_connections(self.active_connections, message)
    
    async def send_error(self, websocket: WebSocket, error_message: str, 
                        error_code: str = "general_error") -> None:
        """Send error message to specific connection.
        
        Args:
            websocket: Target WebSocket connection.
            error_message: Error description.
            error_code: Error type identifier.
        """
        message = {
            "type": "error",
            "error_code": error_code,
            "message": error_message,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self._send_to_connection(websocket, message)
    
    async def _send_to_connection(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
        """Send message to a single WebSocket connection.
        
        Args:
            websocket: Target connection.
            message: Message to send.
        """
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.warning(f"Failed to send message to connection: {e}")
            # Remove failed connection
            await self.disconnect(websocket)
    
    async def _broadcast_to_connections(self, connections: Set[WebSocket], 
                                      message: Dict[str, Any]) -> None:
        """Broadcast message to multiple connections.
        
        Args:
            connections: Set of WebSocket connections.
            message: Message to broadcast.
        """
        if not connections:
            return
        
        message_text = json.dumps(message)
        failed_connections = set()
        
        # Send to all connections concurrently
        tasks = []
        for connection in connections:
            tasks.append(self._safe_send(connection, message_text, failed_connections))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Clean up failed connections
        for failed_connection in failed_connections:
            await self.disconnect(failed_connection)
    
    async def _safe_send(self, websocket: WebSocket, message_text: str, 
                        failed_connections: Set[WebSocket]) -> None:
        """Safely send message and track failures.
        
        Args:
            websocket: Target connection.
            message_text: JSON message string.
            failed_connections: Set to add failed connections to.
        """
        try:
            await websocket.send_text(message_text)
        except Exception as e:
            logger.warning(f"Failed to send to connection: {e}")
            failed_connections.add(websocket)
    
    def get_connection_count(self) -> int:
        """Get current number of active connections.
        
        Returns:
            int: Number of active WebSocket connections.
        """
        return len(self.active_connections)
    
    def get_device_subscriber_count(self, device_id: str) -> int:
        """Get number of subscribers for a specific device.
        
        Args:
            device_id: Device identifier.
            
        Returns:
            int: Number of subscribers for the device.
        """
        return len(self.device_subscriptions.get(device_id, set()))


# Global connection manager instance
connection_manager = ConnectionManager()
