# Machine Control System - Claude Configuration

## Development Commands

### Backend Commands
```bash
# Navigate to backend
cd apps/backend

# Install dependencies
poetry install

# Run tests with coverage
poetry run pytest --cov=src --cov-report=html

# Start development server
poetry run uvicorn src.infrastructure.api.main:app --reload

# Run specific tests
poetry run pytest tests/infrastructure/adapters/test_temperature_adapter.py

# Check code quality
poetry run pytest --cov=src
```

### Frontend Commands
```bash
# Navigate to frontend
cd apps/webapp

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint

# Format code
npm run format
```

### Full System Commands
```bash
# Start both services (run in separate terminals)
# Terminal 1 - Backend:
cd apps/backend && poetry run uvicorn src.infrastructure.api.main:app --reload

# Terminal 2 - Frontend:
cd apps/webapp && npm run dev
```

## Project Architecture

### Backend (FastAPI + Python 3.13)
- **Architecture**: Hexagonal (Ports & Adapters)
- **Framework**: FastAPI with WebSocket support
- **External API**: OpenMeteo for real temperature data
- **Location**: `/apps/backend/`
- **Entry Point**: `src/infrastructure/api/main.py`

### Frontend (React + TypeScript)
- **Framework**: React 18+ with TypeScript 5+
- **State Management**: Zustand
- **Styling**: Tailwind CSS 4+
- **Build Tool**: Vite
- **Location**: `/apps/webapp/`

### Key Components
- **Temperature Sensor**: Real API integration (OpenMeteo)
- **Motor Control**: PWM speed control (0-255)
- **Valve Control**: Binary open/closed states
- **Servo Motor**: Position control (0-180°)
- **WebSocket**: Real-time device updates

## Development Notes

### Device Configuration
- Configuration file: `apps/backend/config/devices.yaml`
- Temperature coordinates: Mexico City (19.4326, -99.1332)
- All devices support status monitoring and control

### Testing Strategy
- Backend: pytest with async/await testing
- Coverage target: >90% for business logic
- Mock external APIs (OpenMeteo) in tests
- WebSocket integration testing included

### API Endpoints
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Device Control: http://localhost:8000/api/v1/devices/
- WebSocket: ws://localhost:8000/ws/devices

### Frontend Access
- Development: http://localhost:5173
- Production Build: `npm run build` ’ `dist/`

## Troubleshooting

### Common Issues
1. **Poetry not found**: Install Poetry first (`pip install poetry`)
2. **Node/npm issues**: Ensure Node.js 18+ is installed
3. **Port conflicts**: Backend uses 8000, frontend uses 5173
4. **WebSocket errors**: Check if backend WebSocket dependencies are installed

### Environment Requirements
- Python 3.13+
- Node.js 18+
- Poetry (Python dependency management)
- npm (Node.js package manager)

## Quality Standards

### Code Quality
- Type hints for all Python functions
- TypeScript strict mode enabled
- Google-style docstrings for Python
- ESLint + Prettier for frontend formatting

### Architecture Principles
- Dependency injection throughout backend
- Clean separation of concerns
- Domain-driven design patterns
- Test-driven development approach