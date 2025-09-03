"""Tests for FastAPI application.

This module contains basic tests for the FastAPI application setup
and health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.infrastructure.api.main import create_app


class TestFastAPIApp:
    """Test suite for FastAPI application."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client for FastAPI app.
        
        Returns:
            TestClient: Configured test client instance.
        """
        app = create_app()
        return TestClient(app)
    
    def test_root_endpoint_returns_service_information(self, client: TestClient) -> None:
        """Test that root endpoint returns comprehensive service information.
        
        Args:
            client: FastAPI test client fixture.
        """
        # Act
        response = client.get("/")
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "Machine Control Panel API"
        assert data["version"] == "0.1.0"
        assert data["status"] == "operational"
        assert data["architecture"] == "Hexagonal Architecture with FastAPI"
        
        # Check devices section
        assert "devices" in data
        assert isinstance(data["devices"], dict)
        
        # Check endpoints section
        assert "endpoints" in data
        endpoints = data["endpoints"]
        assert endpoints["health"] == "/health"
        assert endpoints["docs"] == "/docs"
        assert endpoints["redoc"] == "/redoc"
        assert "devices" in endpoints
        assert "websocket" in endpoints
    
    def test_root_endpoint_shows_device_status(self, client: TestClient) -> None:
        """Test that root endpoint shows status of all configured devices.
        
        Args:
            client: FastAPI test client fixture.
        """
        # Act
        response = client.get("/")
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        devices = data["devices"]
        
        # Should have all 4 device types configured with their actual IDs
        expected_devices = ["temp_01", "valve_01", "motor_01", "servo_01"]
        for device_id in expected_devices:
            assert device_id in devices
            # Device status should be either "connected" or "disconnected"
            assert devices[device_id] in ["connected", "disconnected"]
    
    def test_health_check_endpoint_with_dependency_injection(self, client: TestClient) -> None:
        """Test that health endpoint works with injected service.
        
        Args:
            client: FastAPI test client fixture.
        """
        # Act
        response = client.get("/health")
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Machine Control Panel API"
        assert "devices_count" in data
        assert isinstance(data["devices_count"], int)
        assert "message" in data
    
    def test_app_has_correct_metadata(self, client: TestClient) -> None:
        """Test that app has correct title and description.
        
        Args:
            client: FastAPI test client fixture.
        """
        # Act
        app = client.app
        
        # Assert
        assert app.title == "Machine Control Panel API"
        assert app.description == "Device control system with real-time monitoring"
        assert app.version == "0.1.0"
    
    def test_docs_endpoints_are_available(self, client: TestClient) -> None:
        """Test that documentation endpoints are accessible.
        
        Args:
            client: FastAPI test client fixture.
        """
        # Act
        docs_response = client.get("/docs")
        redoc_response = client.get("/redoc")
        
        # Assert
        assert docs_response.status_code == 200
        assert redoc_response.status_code == 200
