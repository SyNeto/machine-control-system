"""Request models for API endpoints.

This module defines Pydantic models for incoming API requests,
providing validation and documentation for device control operations.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Union, Optional, Any, Dict


class DeviceUpdateRequest(BaseModel):
    """Generic request model for updating device state.
    
    Supports different device types with appropriate validation:
    - Motor: speed (0-255)
    - Servo: angle (0-180)  
    - Valve: state (true/false)
    - Temperature: read-only (no updates)
    """
    
    # Motor control
    speed: Optional[int] = Field(
        None,
        ge=0,
        le=255,
        description="Motor speed (0-255, integer)"
    )
    
    # Servo control
    angle: Optional[float] = Field(
        None,
        ge=0.0,
        le=180.0,
        description="Servo angle in degrees (0-180)"
    )
    
    # Valve control
    state: Optional[bool] = Field(
        None,
        description="Valve state (true=open, false=closed)"
    )
    
    @field_validator('speed', 'angle', 'state', mode='before')
    @classmethod
    def validate_at_least_one_field(cls, v, info):
        """Ensure at least one field is provided."""
        # For Pydantic V2, we'll handle this validation differently
        return v
    
    def __init__(self, **data):
        """Custom initialization to ensure at least one field."""
        super().__init__(**data)
        if all(v is None for v in [self.speed, self.angle, self.state]):
            raise ValueError('At least one field must be provided')


class MotorSpeedRequest(BaseModel):
    """Specific request model for motor speed (backward compatibility).
    
    Attributes:
        speed: Motor speed (0-255).
    """
    speed: int = Field(
        ...,
        ge=0,
        le=255,
        description="Motor speed (0-255, integer)"
    )


class ServoPositionRequest(BaseModel):
    """Specific request model for servo position (backward compatibility).
    
    Attributes:
        angle: Servo angle in degrees (0-180).
    """
    angle: float = Field(
        ...,
        ge=0.0,
        le=180.0,
        description="Servo angle in degrees (0-180)"
    )
