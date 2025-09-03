# ADR-001: Machine Control Panel Architecture

## Status
**ACCEPTED** - 2025-09-02

## Context
Building a Machine Control Panel application for a technical assessment with the following requirements:
- **Backend**: Python-based machine simulator with controllable motor speed, valve state, and real-time temperature from external API
- **Frontend**: React application for machine control and monitoring
- **Architecture**: Need maintainable, testable, and extensible design

The application must simulate industrial machine behavior while being flexible enough to add new sensors/actuators in the future. However, the **business logic is intentionally simple**: primarily reading sensor data and controlling actuators without complex domain rules.

## Decision
We will implement a **Simplified Hexagonal Architecture** (Ports and Adapters) optimized for straightforward I/O coordination rather than complex domain modeling.

### Architectural Rationale

#### Why Simplified Approach
- **Minimal Business Complexity**: Core operations are simple read/write device coordination
- **Declarative Focus**: Application services orchestrate devices in a clear, readable manner
- **Pragmatic over Purist**: Maintains clean architecture benefits without over-engineering
- **Integration-Centric**: Architecture optimized for device coordination rather than complex business rules

### Core Architecture Layers

#### 1. **Domain Layer** (Interfaces & Contracts)
- `IODevice` port interface for unified I/O device abstraction
- Domain interfaces without complex entities (business logic is simple)
- **Location**: `src/domain/ports/`

#### 2. **Application Layer** (Service Coordination) 
- `MachineControlService` coordinating device operations
- Simple orchestration of read/write operations across devices
- **Location**: `src/application/`

#### 3. **Infrastructure Layer** (Concrete Implementations)
- **Device Adapters**: Motor, Valve, Temperature, Servo implementations
- **Dependency Injection**: Container-based assembly with YAML configuration
- **Location**: `src/infrastructure/`

### Key Design Decisions

#### Service-Oriented Coordination
Instead of complex domain entities, we use a **service-based approach**:
- `MachineControlService` receives a list of `IODevice` implementations
- Provides both generic methods (`read_device`, `write_device`) and convenience methods (`set_motor_speed`, `get_temperature`)
- Business logic remains declarative and straightforward

#### Unified I/O Device Port
All devices implement a **single `IODevice` interface**:

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
│   └── ports/
│       └── io_device.py              # Abstract IODevice interface
├── application/
│   └── machine_service.py            # Service-based coordination
└── infrastructure/
    ├── adapters/
    │   ├── temperature_adapter.py    # OpenMeteo API integration
    │   ├── motor_adapter.py          # Motor simulation
    │   ├── valve_adapter.py          # Valve simulation
    │   └── servo_adapter.py          # Servo simulation
    └── di/
        ├── containers.py             # DI containers
        ├── factory.py                # Container factory
        └── config/
            └── devices.yaml          # Device configuration
```

## Benefits of Simplified Approach

### Maintained Clean Architecture Principles
- ✅ **Dependency Inversion**: Application depends on abstractions (`IODevice`)
- ✅ **Testability**: Easy mocking through dependency injection
- ✅ **Separation of Concerns**: Infrastructure isolated from application logic
- ✅ **Extensibility**: New device types integrate seamlessly

### Optimized for Simplicity
- ✅ **Declarative Code**: Service methods are clear and readable
- ✅ **Minimal Overhead**: No unnecessary abstraction layers
- ✅ **Configuration-Driven**: Device assembly through YAML and DI
- ✅ **Appropriate Complexity**: Architecture matches business requirements

## References
- [Hexagonal Architecture (Ports and Adapters) by Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
