"""Tests for WebSocket device monitoring endpoints.

This module tests the real-time WebSocket functionality for device monitoring
and control notifications.
"""

import json
import pytest
from fastapi.testclient import TestClient

from src.infrastructure.api.main import create_app


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
