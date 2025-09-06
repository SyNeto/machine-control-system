"""Tests for WebSocket device monitoring endpoints and connection management.

This module tests the real-time WebSocket functionality for device monitoring,
control notifications, and comprehensive ConnectionManager coverage.
"""

import json
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect

from src.infrastructure.api.main import create_app
from src.infrastructure.api.websockets.manager import ConnectionManager


class TestWebSocketEndpoints:
    """Test cases for WebSocket device monitoring."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for FastAPI app.
        
        Returns:
            TestClient: Configured test client instance.
        """
        app = create_app()
        return TestClient(app)
    
    def test_websocket_connection(self, client: TestClient) -> None:
        """Test basic WebSocket connection establishment."""
        with client.websocket_connect("/ws/devices?client_id=test_client") as websocket:
            # Should receive welcome message
            data = websocket.receive_json()
            assert data["type"] == "connection_established"
            assert data["message"] == "Connected to Machine Control Panel"
            assert "timestamp" in data
            
            # Should receive initial status
            initial_data = websocket.receive_json()
            assert initial_data["type"] == "initial_status"
            assert "data" in initial_data
            assert isinstance(initial_data["data"], dict)
    
    def test_websocket_get_all_status(self, client: TestClient) -> None:
        """Test getting all device status via WebSocket."""
        with client.websocket_connect("/ws/devices") as websocket:
            # Skip welcome and initial messages
            websocket.receive_json()  # connection_established
            websocket.receive_json()  # initial_status
            
            # Request all status
            websocket.send_json({"action": "get_all_status"})
            
            response = websocket.receive_json()
            assert response["type"] == "all_device_status"
            assert "data" in response
            assert isinstance(response["data"], dict)
            
            # Should have all expected devices
            expected_devices = {"motor_01", "servo_01", "valve_01", "temp_01"}
            assert set(response["data"].keys()) == expected_devices
    
    def test_websocket_get_specific_device_status(self, client: TestClient) -> None:
        """Test getting specific device status via WebSocket."""
        with client.websocket_connect("/ws/devices") as websocket:
            # Skip welcome and initial messages
            websocket.receive_json()  # connection_established
            websocket.receive_json()  # initial_status
            
            # Request specific device status
            websocket.send_json({
                "action": "get_status",
                "device_id": "motor_01"
            })
            
            response = websocket.receive_json()
            assert response["type"] == "device_status"
            assert response["device_id"] == "motor_01"
            assert "data" in response
            
            device_data = response["data"]
            assert device_data["device_id"] == "motor_01"
            assert device_data["device_type"] == "motor"
            assert "status" in device_data
            assert "current_value" in device_data
    
    def test_websocket_subscribe_unsubscribe(self, client: TestClient) -> None:
        """Test device subscription and unsubscription."""
        with client.websocket_connect("/ws/devices") as websocket:
            # Skip welcome and initial messages
            websocket.receive_json()  # connection_established
            websocket.receive_json()  # initial_status
            
            # Subscribe to motor_01
            websocket.send_json({
                "action": "subscribe",
                "device_id": "motor_01"
            })
            
            response = websocket.receive_json()
            assert response["type"] == "subscription_confirmed"
            assert response["device_id"] == "motor_01"
            assert "Subscribed to device motor_01" in response["message"]
            
            # Unsubscribe from motor_01
            websocket.send_json({
                "action": "unsubscribe",
                "device_id": "motor_01"
            })
            
            response = websocket.receive_json()
            assert response["type"] == "subscription_removed"
            assert response["device_id"] == "motor_01"
            assert "Unsubscribed from device motor_01" in response["message"]
    
    def test_websocket_invalid_action(self, client: TestClient) -> None:
        """Test WebSocket error handling for invalid actions."""
        with client.websocket_connect("/ws/devices") as websocket:
            # Skip welcome and initial messages
            websocket.receive_json()  # connection_established
            websocket.receive_json()  # initial_status
            
            # Send invalid action
            websocket.send_json({"action": "invalid_action"})
            
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert response["error_code"] == "unknown_action"
            assert "Unknown action: invalid_action" in response["message"]
    
    def test_websocket_missing_device_id(self, client: TestClient) -> None:
        """Test WebSocket error handling for missing device_id."""
        with client.websocket_connect("/ws/devices") as websocket:
            # Skip welcome and initial messages
            websocket.receive_json()  # connection_established
            websocket.receive_json()  # initial_status
            
            # Send subscribe without device_id
            websocket.send_json({"action": "subscribe"})
            
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert response["error_code"] == "validation_error"
            assert "device_id required for subscribe action" in response["message"]
    
    def test_websocket_nonexistent_device(self, client: TestClient) -> None:
        """Test WebSocket handling of nonexistent device requests."""
        with client.websocket_connect("/ws/devices") as websocket:
            # Skip welcome and initial messages
            websocket.receive_json()  # connection_established
            websocket.receive_json()  # initial_status
            
            # Request status for nonexistent device
            websocket.send_json({
                "action": "get_status",
                "device_id": "nonexistent_device"
            })
            
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert response["error_code"] == "device_not_found"
            assert "Device nonexistent_device not found" in response["message"]
    
    def test_websocket_invalid_json(self, client: TestClient) -> None:
        """Test WebSocket handling of invalid JSON."""
        with client.websocket_connect("/ws/devices") as websocket:
            # Skip welcome and initial messages
            websocket.receive_json()  # connection_established
            websocket.receive_json()  # initial_status
            
            # Send invalid JSON
            websocket.send_text("invalid json")
            
            response = websocket.receive_json()
            assert response["type"] == "error"
            assert response["error_code"] == "json_error"
            assert "Invalid JSON format" in response["message"]


# ==================== CONNECTION MANAGER COVERAGE TESTS ====================

class MockWebSocket:
    """Mock WebSocket for testing ConnectionManager edge cases."""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.send_text = AsyncMock()
        self.accept = AsyncMock()
        
        if should_fail:
            self.send_text.side_effect = ConnectionError("Connection failed")


class TestConnectionManagerCoverage:
    """Tests to improve ConnectionManager coverage from 58% to 95%+."""
    
    @pytest.fixture
    def manager(self):
        """Fresh ConnectionManager instance."""
        return ConnectionManager()
    
    @pytest.fixture
    def mock_websocket(self):
        """Working mock WebSocket."""
        return MockWebSocket()
    
    @pytest.fixture
    def failing_websocket(self):
        """Failing mock WebSocket."""
        return MockWebSocket(should_fail=True)
    
    # ==================== BROADCAST WITH NO CONNECTIONS ====================
    
    @pytest.mark.asyncio
    async def test_broadcast_device_update_no_connections(self, manager):
        """Test broadcasting when no connections are active (lines 113-127)."""
        await manager.broadcast_device_update("motor_01", {"speed": 100})
        assert len(manager.active_connections) == 0
    
    @pytest.mark.asyncio
    async def test_broadcast_system_status_no_connections(self, manager):
        """Test system status broadcast with no connections (lines 136-146)."""
        status_data = {"status": "healthy", "devices": 4}
        await manager.broadcast_system_status(status_data)
        assert len(manager.active_connections) == 0
    
    # ==================== SYSTEM STATUS BROADCASTING ====================
    
    @pytest.mark.asyncio
    async def test_broadcast_system_status_with_connections(self, manager, mock_websocket):
        """Test system status broadcast to active connections."""
        await manager.connect(mock_websocket, "test_client")
        
        status_data = {"status": "healthy", "devices": 4}
        await manager.broadcast_system_status(status_data)
        
        assert mock_websocket.send_text.call_count >= 2
        
        # Check system status message format
        calls = [json.loads(call[0][0]) for call in mock_websocket.send_text.call_args_list]
        system_msgs = [msg for msg in calls if msg.get("type") == "system_status"]
        
        assert len(system_msgs) == 1
        assert system_msgs[0]["data"] == status_data
    
    # ==================== CONNECTION FAILURE HANDLING ====================
    
    @pytest.mark.asyncio
    async def test_send_to_connection_failure_removes_connection(self, manager, failing_websocket):
        """Test failed connections are removed (lines 175-178)."""
        # Manually add to connections to avoid welcome message failure
        manager.active_connections.add(failing_websocket)
        assert len(manager.active_connections) == 1
        
        # Trigger failure through _send_to_connection
        await manager._send_to_connection(failing_websocket, {"type": "test"})
        
        # Should be removed after failure
        assert len(manager.active_connections) == 0
    
    @pytest.mark.asyncio
    async def test_send_error_message(self, manager, mock_websocket):
        """Test error message sending."""
        await manager.connect(mock_websocket, "test_client")
        
        await manager.send_error(mock_websocket, "Test error", "test_code")
        
        calls = [json.loads(call[0][0]) for call in mock_websocket.send_text.call_args_list]
        error_msgs = [msg for msg in calls if msg.get("type") == "error"]
        
        assert len(error_msgs) == 1
        assert error_msgs[0]["error_code"] == "test_code"
        assert error_msgs[0]["message"] == "Test error"
    
    # ==================== BROADCAST WITH MIXED CONNECTIONS ====================
    
    @pytest.mark.asyncio
    async def test_broadcast_with_failed_connections(self, manager, mock_websocket, failing_websocket):
        """Test broadcasting to mix of good/bad connections (lines 188-203)."""
        # Connect good websocket normally
        await manager.connect(mock_websocket, "good_client")
        
        # Manually add failing websocket to avoid initial failure
        manager.active_connections.add(failing_websocket)
        
        assert len(manager.active_connections) == 2
        
        device_data = {"speed": 150}
        await manager.broadcast_device_update("motor_01", device_data)
        
        # Good connection remains, bad one removed
        assert len(manager.active_connections) == 1
        assert mock_websocket in manager.active_connections
        assert failing_websocket not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_broadcast_to_empty_connections(self, manager):
        """Test broadcasting to empty connection set."""
        empty_connections = set()
        message = {"type": "test"}
        
        # Should not raise error
        await manager._broadcast_to_connections(empty_connections, message)
    
    # ==================== SAFE SEND ERROR TRACKING ====================
    
    @pytest.mark.asyncio
    async def test_safe_send_tracks_failures(self, manager):
        """Test _safe_send tracks failed connections (lines 214-218)."""
        failing_ws = MockWebSocket(should_fail=True)
        failed_connections = set()
        
        await manager._safe_send(failing_ws, '{"test": "data"}', failed_connections)
        
        assert failing_ws in failed_connections
    
    @pytest.mark.asyncio
    async def test_safe_send_successful(self, manager, mock_websocket):
        """Test _safe_send with successful connection."""
        failed_connections = set()
        message_text = '{"type": "test"}'
        
        await manager._safe_send(mock_websocket, message_text, failed_connections)
        
        mock_websocket.send_text.assert_called_once_with(message_text)
        assert mock_websocket not in failed_connections
    
    # ==================== CONNECTION COUNT METHODS ====================
    
    @pytest.mark.asyncio
    async def test_get_connection_count(self, manager, mock_websocket):
        """Test connection count tracking (line 226)."""
        assert manager.get_connection_count() == 0
        
        await manager.connect(mock_websocket, "test_client")
        assert manager.get_connection_count() == 1
        
        await manager.disconnect(mock_websocket)
        assert manager.get_connection_count() == 0
    
    @pytest.mark.asyncio
    async def test_get_device_subscriber_count(self, manager, mock_websocket):
        """Test device subscriber counting (line 237)."""
        # No subscribers initially
        assert manager.get_device_subscriber_count("motor_01") == 0
        assert manager.get_device_subscriber_count("nonexistent") == 0
        
        # Connect and subscribe
        await manager.connect(mock_websocket, "test_client")
        await manager.subscribe_to_device(mock_websocket, "motor_01")
        
        assert manager.get_device_subscriber_count("motor_01") == 1
        assert manager.get_device_subscriber_count("valve_01") == 0
        
        # Unsubscribe
        await manager.unsubscribe_from_device(mock_websocket, "motor_01")
        assert manager.get_device_subscriber_count("motor_01") == 0
    
    # ==================== SUBSCRIPTION EDGE CASES ====================
    
    @pytest.mark.asyncio
    async def test_unsubscribe_nonexistent_device(self, manager, mock_websocket):
        """Test unsubscribing from nonexistent device."""
        await manager.connect(mock_websocket, "test_client")
        
        # Should not raise error
        await manager.unsubscribe_from_device(mock_websocket, "nonexistent")
        
        calls = [json.loads(call[0][0]) for call in mock_websocket.send_text.call_args_list]
        unsub_msgs = [msg for msg in calls if msg.get("type") == "subscription_removed"]
        
        assert len(unsub_msgs) == 1
        assert unsub_msgs[0]["device_id"] == "nonexistent"
    
    @pytest.mark.asyncio
    async def test_disconnect_removes_all_subscriptions(self, manager):
        """Test disconnect removes from all device subscriptions."""
        ws1 = MockWebSocket()
        ws2 = MockWebSocket()
        
        await manager.connect(ws1, "client1")
        await manager.connect(ws2, "client2")
        
        # Subscribe both to motor_01
        await manager.subscribe_to_device(ws1, "motor_01")
        await manager.subscribe_to_device(ws2, "motor_01")
        
        # Subscribe ws1 to valve_01
        await manager.subscribe_to_device(ws1, "valve_01")
        
        assert manager.get_device_subscriber_count("motor_01") == 2
        assert manager.get_device_subscriber_count("valve_01") == 1
        
        # Disconnect ws1 - should remove from all subscriptions
        await manager.disconnect(ws1)
        
        assert manager.get_device_subscriber_count("motor_01") == 1
        assert manager.get_device_subscriber_count("valve_01") == 0
    
    # ==================== WEBSOCKET DISCONNECT EXCEPTION ====================
    
    @pytest.mark.asyncio
    async def test_websocket_disconnect_exception(self, manager):
        """Test handling WebSocketDisconnect exception."""
        class DisconnectWebSocket(MockWebSocket):
            def __init__(self):
                super().__init__()
                self.send_text.side_effect = WebSocketDisconnect()
        
        disconnect_ws = DisconnectWebSocket()
        failed_connections = set()
        
        await manager._safe_send(disconnect_ws, '{"test": "data"}', failed_connections)
        
        assert disconnect_ws in failed_connections
