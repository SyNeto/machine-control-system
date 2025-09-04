"""Response models for API endpoints.

This module defines Pydantic models for API responses,
providing consistent structure for device control results.
"""

from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime


class DeviceStatusResponse(BaseModel):
    """Response model for device status information.
    
    Attributes:
        device_id: Unique identifier for the device.
        device_type: Type of device (motor, servo, valve, temperature).
        status: Current operational status.
        current_value: Current device value/state.
        last_updated: Timestamp of last update.
    """
    device_id: str
    device_type: str
    status: str
    current_value: Any
    last_updated: Optional[datetime] = None


class DeviceUpdateResponse(BaseModel):
    """Generic response model for device update operations.
    
    Attributes:
        device_id: Device identifier.
        device_type: Type of device.
        previous_state: Device state before the operation.
        new_state: Device state after the operation.
        status: Operation result status.
        message: Human-readable result message.
        changed: Whether the state actually changed.
    """
    device_id: str
    device_type: str
    previous_state: Dict[str, Any]
    new_state: Dict[str, Any]
    status: str
    message: str
    changed: bool


class MotorControlResponse(BaseModel):
    """Response model for motor control operations (backward compatibility).
    
    Attributes:
        device_id: Motor device identifier.
        previous_speed: Speed before the operation.
        new_speed: Speed after the operation.
        status: Operation result status.
        message: Human-readable result message.
        changed: Whether the speed actually changed.
    """
    device_id: str
    previous_speed: int
    new_speed: int
    status: str
    message: str
    changed: bool


class ServoControlResponse(BaseModel):
    """Response model for servo control operations (backward compatibility).
    
    Attributes:
        device_id: Servo device identifier.
        previous_angle: Angle before the operation.
        new_angle: Angle after the operation.
        status: Operation result status.
        message: Human-readable result message.
        changed: Whether the angle actually changed.
    """
    device_id: str
    previous_angle: float
    new_angle: float
    status: str
    message: str
    changed: bool


class ErrorResponse(BaseModel):
    """Response model for error cases.
    
    Attributes:
        error: Error type or code.
        message: Human-readable error message.
        device_id: Device that caused the error (if applicable).
    """
    error: str
    message: str
    device_id: Optional[str] = None
