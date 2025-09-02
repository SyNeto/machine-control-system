# ADR-001: Machine Control Panel Architecture

## Status
**ACCEPTED** - 2025-09-02

## Context
Building a Machine Control Panel application for a technical assessment with the following requirements:
- **Backend**: Python-based machine simulator with controllable motor speed, valve state, and real-time temperature from external API
- **Frontend**: React application for machine control and monitoring
- **Architecture**: Need maintainable, testable, and extensible design

The application must simulate industrial machine behavior while being flexible enough to add new sensors/actuators in the future.

## Decision
We will implement a **Hexagonal Architecture** (Ports and Adapters) with the following structure:

### Core Architecture Layers

#### 1. **Domain Layer** (Business Logic)
- `Machine` entity as aggregate root
- `IODevice` port interface for unified I/O device abstraction
- Value objects for machine state representation
- **Location**: `src/domain/`

#### 2. **Application Layer** (Use Cases) 
- `MachineControlService` orchestrating domain operations
- Use case implementations (read sensors, control actuators, get status)
- **Location**: `src/application/services/`

#### 3. **Infrastructure Layer** (Adapters)
- **Input Adapters**: REST API controllers
- **Output Adapters**: Weather API client, device simulators
- **Location**: `src/infrastructure/adapters/`

### Key Design Decisions

#### Unified I/O Device Port
Instead of separating sensors and actuators, we chose a **single `IODevice` interface**:

```python
class IODevice(ABC):
    @property
    @abstractmethod
    def device_id(self) -> str: pass
    
    @property  
    @abstractmethod
    def device_type(self) -> str: pass
    
    @abstractmethod
    async def read(self) -> Any: pass
    
    @abstractmethod
    async def write(self, value: Any) -> bool: pass
    
    async def get_status(self) -> Dict[str, Any]: pass
```

**Rationale**: 
- Industrial PLCs handle sensors/actuators uniformly through I/O modules
- Many industrial devices are hybrid (servo motors read position + write speed)
- Simplifies device management and enables future extensibility
- Single interface reduces complexity while maintaining flexibility

#### Dependency Inversion
- Domain defines `IODevice` port interface
- Infrastructure implements concrete adapters (WeatherApiAdapter, MotorSimulator, ValveSimulator)  
- Application layer orchestrates domain through dependency injection

#### Machine as Aggregate Root
- Central entity managing all I/O devices
- Enforces business rules (initialization, device registration)
- Maintains machine state consistency

## Consequences

### Positive
- ✅ **Testable**: Easy to mock I/O devices for unit testing
- ✅ **Extensible**: Adding new device types requires only new adapters
- ✅ **Maintainable**: Clear separation of concerns
- ✅ **Industrial Realism**: Architecture reflects real PLC/SCADA patterns
- ✅ **Technology Agnostic**: Domain independent of external APIs/frameworks

### Negative  
- ⚠️ **Initial Complexity**: More files and interfaces than simple approach
- ⚠️ **Learning Curve**: Team needs to understand hexagonal architecture
- ⚠️ **Over-engineering Risk**: Might be complex for simple requirements

### Neutral
- 📝 **Code Structure**: Requires disciplined file organization
- 📝 **Documentation**: Architecture decisions need to be well documented

## Implementation Plan

### Phase 1: Core Domain
1. Implement `IODevice` port interface
2. Create `Machine` aggregate root
3. Define basic value objects

### Phase 2: Application Layer
1. Implement `MachineControlService`
2. Define use case interfaces

### Phase 3: Infrastructure
1. Create device adapters (WeatherAPI, Motor, Valve simulators)
2. Implement REST API controllers
3. Wire dependency injection

### Phase 4: Integration
1. Frontend integration
2. End-to-end testing
3. Documentation

## File Structure
```
src/
├── domain/
│   ├── ports/
│   │   └── io_device.py
│   ├── entities/
│   │   └── machine.py
│   └── value_objects/
│       └── machine_state.py
├── application/
│   └── services/
│       └── machine_control_service.py  
└── infrastructure/
    └── adapters/
        ├── weather_api_adapter.py
        ├── motor_adapter.py
        └── valve_adapter.py
```

## References
- [Hexagonal Architecture (Ports and Adapters) by Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
