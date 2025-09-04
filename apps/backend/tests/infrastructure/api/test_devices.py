"""Tests for device control REST API endpoints.

This module tests the RESTful device control API with proper
validation, error handling, and state verification.
"""

import pytest
from fastapi.testclient import TestClient

from src.infrastructure.api.main import create_app


class TestDeviceAPI:
    """Test cases for device control endpoints."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for FastAPI app.
        
        Returns:
            TestClient: Configured test client instance.
        """
        app = create_app()
        return TestClient(app)
    
    def test_update_motor_device_success(self, client: TestClient) -> None:
        """Test successful motor speed update."""
        # Test speed update
        response = client.post(
            "/api/v1/devices/motor_01",
            json={"speed": 150}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["device_id"] == "motor_01"
        assert data["device_type"] == "motor"
        assert "previous_state" in data
        assert "new_state" in data
        assert data["status"] in ["success", "no_change"]
        assert isinstance(data["changed"], bool)
        assert "message" in data
    
    def test_update_servo_device_success(self, client: TestClient) -> None:
        """Test successful servo position update."""
        # Test position update
        response = client.post(
            "/api/v1/devices/servo_01",
            json={"angle": 90}  # Use integer for servo
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["device_id"] == "servo_01"
        assert data["device_type"] == "servo"
        assert "previous_state" in data
        assert "new_state" in data
        assert data["status"] in ["success", "no_change"]
        assert isinstance(data["changed"], bool)
        assert "message" in data
    
    def test_update_valve_device_success(self, client: TestClient) -> None:
        """Test successful valve state update."""
        # Test state update
        response = client.post(
            "/api/v1/devices/valve_01",
            json={"state": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["device_id"] == "valve_01"
        assert data["device_type"] == "valve"
        assert "previous_state" in data
        assert "new_state" in data
        assert data["status"] in ["success", "no_change"]
        assert isinstance(data["changed"], bool)
        assert "message" in data
    
    def test_motor_speed_validation(self, client: TestClient) -> None:
        """Test motor speed validation limits."""
        # Test below minimum
        response = client.post(
            "/api/v1/devices/motor_01",
            json={"speed": -10}
        )
        assert response.status_code == 422
        error_data = response.json()
        assert "greater than or equal to 0" in error_data["detail"][0]["msg"]
        
        # Test above maximum
        response = client.post(
            "/api/v1/devices/motor_01", 
            json={"speed": 300}
        )
        assert response.status_code == 422
        error_data = response.json()
        assert "less than or equal to 255" in error_data["detail"][0]["msg"]
        
        # Test valid range
        response = client.post(
            "/api/v1/devices/motor_01",
            json={"speed": 128}
        )
        assert response.status_code == 200
    
    def test_servo_angle_validation(self, client: TestClient) -> None:
        """Test servo angle validation limits."""
        # Test below minimum
        response = client.post(
            "/api/v1/devices/servo_01",
            json={"angle": -10.0}
        )
        assert response.status_code == 422
        error_data = response.json()
        assert "greater than or equal to 0" in error_data["detail"][0]["msg"]
        
        # Test above maximum  
        response = client.post(
            "/api/v1/devices/servo_01",
            json={"angle": 200.0}
        )
        assert response.status_code == 422
        error_data = response.json()
        assert "less than or equal to 180" in error_data["detail"][0]["msg"]
        
        # Test valid range
        response = client.post(
            "/api/v1/devices/servo_01", 
            json={"angle": 90}  # Use integer for servo
        )
        assert response.status_code == 200
    
    def test_update_device_not_found(self, client: TestClient) -> None:
        """Test update on non-existent device."""
        response = client.post(
            "/api/v1/devices/nonexistent",
            json={"speed": 100}
        )
        
        assert response.status_code == 404
        error_data = response.json()
        assert "not found" in error_data["detail"].lower()
    
    def test_update_wrong_field_for_device_type(self, client: TestClient) -> None:
        """Test using wrong field for device type."""
        # Try to set angle on motor (should fail)
        response = client.post(
            "/api/v1/devices/motor_01",
            json={"angle": 90.0}
        )
        
        assert response.status_code == 400
        error_data = response.json()
        assert "motor" in error_data["detail"].lower() and "speed" in error_data["detail"].lower()
        
        # Try to set speed on servo (should fail)
        response = client.post(
            "/api/v1/devices/servo_01",
            json={"speed": 100}
        )
        
        assert response.status_code == 400
        error_data = response.json()
        assert "servo" in error_data["detail"].lower() and "angle" in error_data["detail"].lower()
    
    def test_update_temperature_sensor_readonly(self, client: TestClient) -> None:
        """Test that temperature sensors are read-only."""
        response = client.post(
            "/api/v1/devices/temp_01",
            json={"state": True}
        )
        
        assert response.status_code == 400
        error_data = response.json()
        assert "read-only" in error_data["detail"].lower() or "temperature" in error_data["detail"].lower()
    
    def test_update_empty_request(self, client: TestClient) -> None:
        """Test update with no fields provided."""
        response = client.post(
            "/api/v1/devices/motor_01",
            json={}
        )
        
        # The validation now happens in our custom init, returning 400 instead of 422
        assert response.status_code in [400, 422]
        error_data = response.json()
        
        # Handle both list and string error formats
        if isinstance(error_data["detail"], list):
            error_msg = error_data["detail"][0]["msg"].lower()
        else:
            error_msg = error_data["detail"].lower()
            
        assert "at least one field" in error_msg or "motor" in error_msg
    
    def test_list_devices_success(self, client: TestClient) -> None:
        """Test listing all devices."""
        response = client.get("/api/v1/devices/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that all devices are returned
        expected_devices = {"motor_01", "servo_01", "valve_01", "temp_01"}
        assert set(data.keys()) == expected_devices
        
        # Check device details
        assert data["motor_01"]["device_type"] == "motor"
        assert "status" in data["motor_01"]
        assert "current_value" in data["motor_01"]
        
        assert data["servo_01"]["device_type"] == "servo"
        assert "current_value" in data["servo_01"]
    
    def test_get_device_status_success(self, client: TestClient) -> None:
        """Test getting status of specific device."""
        response = client.get("/api/v1/devices/motor_01")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["device_id"] == "motor_01"
        assert data["device_type"] == "motor"
        assert "status" in data
        assert "current_value" in data
    
    def test_get_device_status_not_found(self, client: TestClient) -> None:
        """Test getting status of non-existent device."""
        response = client.get("/api/v1/devices/nonexistent")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "not found" in error_data["detail"].lower()
