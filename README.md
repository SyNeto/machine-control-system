# Machine Control Panel

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![Poetry](https://img.shields.io/badge/Poetry-Dependency%20Management-blue.svg)](https://python-poetry.org/)
[![Code Style](https://img.shields.io/badge/Code%20Style-Google-blue.svg)](https://google.github.io/styleguide/pyguide.html)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal-green.svg)](https://alistair.cockburn.us/hexagonal-architecture/)

A modern device control system built with simplified hexagonal architecture, providing real-time monitoring and control of industrial devices through REST API and WebSocket interfaces.

## 🚀 Project Overview

The Machine Control Panel is a backend system designed to coordinate multiple control devices in an industrial environment. It provides:

- **Real-time monitoring** of temperature, motor speed, valve states, and servo positions
- **Device control** through standardized interfaces
- **External API integration** with OpenMeteo for environmental data
- **Scalable architecture** using dependency injection and hexagonal design
- **Comprehensive testing** with async/await patterns and HTTP mocking

### Key Features

- 🌡️ **Temperature Monitoring**: Real-time environmental data via OpenMeteo API
- ⚙️ **Motor Control**: Speed management with realistic simulation
- 🔧 **Valve Management**: Binary state control (open/closed)
- 🎛️ **Servo Control**: Precise position control (0-180°)
- 📡 **WebSocket Streaming**: Real-time data updates with configurable intervals
- 🔌 **REST API**: Device configuration and control endpoints

## 🏗️ Architecture

This project implements a **Simplified Hexagonal Architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Layer                     │
├─────────────────────┬─────────────────────┬─────────────────┤
│   Input Adapters    │   Output Adapters   │  Configuration  │
│  ┌─────────────┐    │  ┌─────────────┐    │  ┌─────────────┐ │
│  │ FastAPI     │    │  │ Temperature │    │  │ Dependency  │ │
│  │ (Web API)   │    │  │ Adapter     │    │  │ Injection   │ │
│  │             │    │  │             │    │  │ Container   │ │
│  └─────────────┘    │  ├─────────────┤    │  └─────────────┘ │
│                     │  │ Motor       │    │                 │
│                     │  │ Adapter     │    │                 │
│                     │  │             │    │                 │
│                     │  ├─────────────┤    │                 │
│                     │  │ Valve       │    │                 │
│                     │  │ Adapter     │    │                 │
│                     │  │             │    │                 │
│                     │  ├─────────────┤    │                 │
│                     │  │ Servo       │    │                 │
│                     │  │ Adapter     │    │                 │
│                     │  └─────────────┘    │                 │
└─────────────────────┴─────────────────────┴─────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            MachineControlService                    │    │
│  │  - **Device coordination and orchestration**: Service-oriented device coordination           │    │
│  │  • Business logic for device interactions          │    │
│  │  • Service-oriented architecture approach          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  IODevice Port                      │    │
│  │  • Abstract interface for all devices              │    │
│  │  • Defines read(), write(), get_status() contracts │    │
│  │  • Technology-agnostic device operations           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

- **Domain**: Core business rules and device abstractions
- **Application**: Service coordination and business workflows  
- **Infrastructure**: External integrations, web APIs, and device adapters

## 🛠️ Quick Start

### Prerequisites

- **Python 3.13+** 
- **Poetry** for dependency management

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd valiot_technical_test
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Activate virtual environment**
   ```bash
   poetry shell
   ```

4. **Run tests**
   ```bash
   poetry run pytest
   ```

5. **Check code coverage**
   ```bash
   poetry run pytest --cov=src --cov-report=term-missing
   ```

### Development Commands

```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/domain/test_io_device.py

# Install new dependency
poetry add <package-name>

# Install development dependency
poetry add --group dev <package-name>
```

## 📁 Project Structure

```
valiot_technical_test/
├── README.md                          # Project documentation
├── pyproject.toml                     # Poetry configuration
├── config/
│   └── devices.yaml                   # Device configuration
├── docs/                              # Architecture Decision Records
│   ├── ADR-001-architecture.md        # Simplified hexagonal architecture
│   ├── ADR-002-documentation.md       # Google-style docstrings
│   ├── ADR-003-dependency-injection.md # DI container patterns
│   └── ADR-004-web-api-layer.md       # FastAPI integration
├── src/
│   ├── domain/                        # Core business logic
│   │   └── ports/
│   │       └── io_device.py           # Device abstraction interface
│   ├── application/                   # Business workflows
│   │   └── machine_service.py         # Device coordination service
│   ├── infrastructure/                # External integrations
│   │   ├── adapters/                  # Device implementations
│   │   │   ├── temperature_adapter.py # OpenMeteo API integration
│   │   │   ├── motor_adapter.py       # Motor control simulation
│   │   │   ├── valve_adapter.py       # Valve state management
│   │   │   └── servo_adapter.py       # Servo position control
│   │   ├── di/                        # Dependency injection
│   │   │   ├── containers.py          # DI container setup
│   │   │   └── factory.py             # Container factory
│   │   └── web/                       # [Coming Soon] FastAPI layer
└── tests/                             # Comprehensive test suite
    ├── domain/                        # Domain layer tests
    ├── application/                   # Application layer tests
    └── infrastructure/                # Infrastructure layer tests
```

## 🔧 Supported Devices

### Temperature Sensor
- **Integration**: OpenMeteo API for real environmental data
- **Coordinates**: Currently configured for specific geographic location
- **Polling**: Optimized 2-minute intervals to respect free API limits
- **Error Handling**: Robust HTTP error mapping and fallback strategies

### Motor Control
- **Simulation**: Realistic speed control with acceleration curves
- **Range**: 0-100% speed control
- **Status**: Current speed, acceleration state, operational status
- **Safety**: Built-in limits and error conditions

### Valve Management  
- **States**: Binary open/closed control
- **Feedback**: Position confirmation and transition status
- **Safety**: Fail-safe modes and timeout protection
- **Simulation**: Realistic operation timing

### Servo Control
- **Range**: 0-180° position control
- **Precision**: High-accuracy positioning simulation
- **Feedback**: Current position and movement status
- **Calibration**: Self-calibration and limit detection

## 🧪 Development Workflow

### Testing Strategy

- **Unit Tests**: Comprehensive coverage for all layers
- **Integration Tests**: Device adapter validation with HTTP mocking
- **Async Testing**: Full async/await pattern testing
- **Mock Strategies**: Proper isolation of external dependencies

### Code Coverage

Coverage analysis excludes infrastructure configuration (DI containers) to focus on business logic:

```bash
# Generate coverage report
poetry run pytest --cov=src --cov-report=html

# View detailed coverage
open htmlcov/index.html
```

### Architecture Decision Records

All major architectural decisions are documented in the `docs/` directory:

- **ADR-001**: Simplified hexagonal architecture rationale
- **ADR-002**: Documentation standards (Google-style docstrings)  
- **ADR-003**: Dependency injection patterns and container design
- **ADR-004**: Web API layer design with FastAPI

## 🚧 Roadmap

### Phase 1: Core Backend ✅
- [x] Domain layer with device abstractions
- [x] Infrastructure adapters for all device types
- [x] Application service coordination
- [x] Dependency injection container
- [x] Comprehensive testing suite

### Phase 2: Web API Layer 🚧
- [ ] FastAPI integration with REST endpoints
- [ ] WebSocket real-time data streaming
- [ ] Background polling with device-specific intervals
- [ ] API documentation and validation

### Phase 3: Frontend Integration 📋
- [ ] React frontend integration
- [ ] Real-time dashboard with WebSocket connections
- [ ] Device control interface
- [ ] System monitoring and alerts

### Phase 4: Production Features 📋
- [ ] Authentication and authorization
- [ ] Data persistence and logging
- [ ] System health monitoring
- [ ] Deployment configuration

## 🤝 Contributing

1. Follow the established architecture patterns
2. Maintain comprehensive test coverage
3. Document architectural decisions in ADRs
4. Use Google-style docstrings
5. Ensure async/await compatibility

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ using Python, Poetry, and Hexagonal Architecture principles.**