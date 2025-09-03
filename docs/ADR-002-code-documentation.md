# ADR-002: Documentation Standards

## Status
**ACCEPTED** - 2025-09-02

## Context
The Machine Control Panel application requires comprehensive documentation to:
- **Support technical assessment**: Clear code documentation for reviewers
- **Enable future maintenance**: Well-documented architecture and business rules
- **Facilitate AI-assisted development**: Structured docstrings for AI agents to understand context
- **Ensure code quality**: Consistent documentation patterns across the codebase

Modern Python development emphasizes machine-readable documentation that serves both humans and tools (IDEs, static analyzers, AI assistants).

## Decision

### Documentation Strategy
We will implement a **multi-layered documentation approach**:

1. **Architectural Documentation** - ADRs for major decisions
2. **API Documentation** - Auto-generated from code
3. **Code Documentation** - Modern Python docstring standards
4. **User Documentation** - README and setup guides

### Docstring Standard: Modern Python with Type Hints

#### **Choice: Google Style with Type Annotations**
We will use **Google-style docstrings** combined with modern Python type hints:

```python
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod

class IODevice(ABC):
    """Abstract base class for I/O devices in industrial automation.
    
    This interface provides a unified abstraction for sensors, actuators, and hybrid
    devices, following industrial PLC patterns where all devices are treated as
    I/O points with read/write capabilities.
    
    Examples:
        Basic device implementation:
        
        >>> class TemperatureSensor(IODevice):
        ...     @property
        ...     def device_id(self) -> str:
        ...         return "temp_01"
        ...     
        ...     async def read(self) -> float:
        ...         return 23.5
        
        Usage in machine context:
        
        >>> device = TemperatureSensor()
        >>> status = await device.get_status()
        >>> print(status["status"])  # "online"
    
    Note:
        All I/O operations are async to support real network calls and
        maintain consistent interface regardless of device type.
    """
    
    @property
    @abstractmethod
    def device_id(self) -> str:
        """Unique identifier for this device.
        
        Returns:
            Unique string identifier used for device registration and logging.
            Should be immutable throughout device lifecycle.
            
        Note:
            Format convention: {type}_{sequence} (e.g., "temp_01", "valve_main")
        """
        
    @abstractmethod
    async def read(self) -> Any:
        """Read current value from the device.
        
        Returns:
            Current device value. Type depends on device implementation:
            - Sensors: measurement value (float, int, bool)
            - Actuators: current state/position
            - Hybrid devices: primary feedback value
            
        Raises:
            ConnectionError: When device is unreachable
            ValueError: When device returns invalid data
            TimeoutError: When read operation times out
            
        Examples:
            >>> temp_value = await temperature_sensor.read()  # 23.5
            >>> valve_state = await valve.read()              # True (open)
            >>> motor_speed = await motor.read()              # 75 (rpm %)
        """
        
    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive device status and diagnostics.
        
        Provides device health information by attempting a read operation
        and returning structured status data.
        
        Returns:
            Status dictionary containing:
            - device_id: Device identifier
            - device_type: Device type string  
            - status: "online" | "error" | "offline"
            - data: Current device value (if online)
            - message: Error description (if error)
            
        Note:
            This method should never raise exceptions. Errors are captured
            in the status response for graceful degradation.
            
        Examples:
            Successful status:
            >>> status = await device.get_status()
            >>> print(status)
            {
                "device_id": "temp_01",
                "device_type": "temperature_sensor", 
                "status": "online",
                "data": 23.5
            }
            
            Error status:
            >>> status = await failing_device.get_status()
            >>> print(status["status"])  # "error"
        """
```

### Documentation Levels

#### **1. Interface/Port Documentation (Comprehensive)**
- **Purpose**: Contract definition and usage examples
- **Audience**: Other developers, AI assistants, API consumers
- **Include**: Examples, error cases, type information, usage patterns

#### **2. Domain Entity Documentation (Business-Focused)**
```python
class Machine:
    """Industrial machine aggregate managing I/O devices.
    
    Represents a complete industrial machine with sensors and actuators.
    Enforces business rules around device registration, initialization,
    and operational state management.
    
    Business Rules:
        - Devices can only be added before initialization
        - Machine must be initialized before I/O operations
        - Device IDs must be unique within a machine
        - All I/O operations are tracked for diagnostics
    """
```

#### **3. Application Service Documentation (Use-Case Focused)**
```python
class MachineControlService:
    """Application service for machine control use cases.
    
    Orchestrates machine operations for specific business scenarios.
    Provides error handling and response formatting for external interfaces.
    """
    
    async def control_actuator(self, actuator_id: str, value: Any) -> Dict[str, Any]:
        """Execute actuator control use case.
        
        Args:
            actuator_id: Target actuator identifier
            value: Control value to apply
            
        Returns:
            Control operation result with success status and current value
        """
```

#### **4. Infrastructure Adapter Documentation (Implementation-Focused)**
```python
class WeatherApiAdapter(IODevice):
    """Weather API adapter for ambient temperature sensing.
    
    Implements IODevice interface by fetching real-time temperature
    data from OpenWeatherMap API.
    
    Configuration:
        - API_KEY: Required OpenWeatherMap API key
        - CITY: Target city for temperature readings
        - TIMEOUT: Request timeout in seconds (default: 10)
    """
```

### Documentation Tools

#### **Auto-Documentation Generation**
- **Sphinx** with autodoc for API documentation
- **Type hints** for parameter and return documentation
- **docstring-parser** for structured docstring validation

#### **Documentation Validation**
- **pydocstyle** for docstring quality checking
- **mypy** for type annotation validation
- **interrogate** for documentation coverage metrics

#### **IDE Integration**
- All docstrings compatible with VS Code, PyCharm IntelliSense
- Hover documentation shows examples and type information
- Auto-completion understands return types and exceptions

## Consequences

### Positive
- ✅ **AI-Friendly**: Structured docstrings help AI assistants understand code context
- ✅ **Self-Documenting**: Type hints + docstrings reduce separate documentation need
- ✅ **Tool Integration**: Modern IDEs provide rich code assistance
- ✅ **Consistency**: Clear standards for all team members
- ✅ **Maintainability**: Examples in docstrings serve as inline tests

### Negative
- ⚠️ **Initial Overhead**: More time spent writing documentation
- ⚠️ **Maintenance Cost**: Docstrings need updates when code changes
- ⚠️ **Verbosity**: Some simple methods become heavily documented

### Neutral
- 📝 **Learning Curve**: Team needs to adopt Google docstring style
- 📝 **Tool Setup**: Requires configuration of documentation tools

## Implementation Guidelines

### **Must Document**
- All public interfaces (ports, services)
- Domain entities and business rules
- Complex algorithms or business logic
- Error handling patterns

### **Should Document** 
- Public methods with non-obvious behavior
- Configuration and setup procedures
- Integration patterns

### **May Skip Documentation**
- Simple getters/setters with obvious behavior
- Private helper methods
- Trivial implementations

### **Documentation Checklist**
- [ ] Purpose clearly stated
- [ ] Parameters and return types documented
- [ ] Exceptions listed with conditions
- [ ] Usage examples provided (for interfaces)
- [ ] Business rules explained (for domain code)

## References
- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [Sphinx Documentation](https://www.sphinx-doc.org/)

---
**Next ADR**: ADR-003 will cover testing strategies and framework choices