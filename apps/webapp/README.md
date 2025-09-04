# Machine Control Frontend

[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5+-646CFF.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3+-38B2AC.svg)](https://tailwindcss.com/)
[![Zustand](https://img.shields.io/badge/Zustand-State%20Management-orange.svg)](https://zustand-demo.pmnd.rs/)

Modern React TypeScript frontend for the Machine Control Panel. Features real-time device monitoring, responsive controls, and WebSocket integration for industrial IoT applications.

## 🏗️ Architecture Overview

This frontend implements **Component-Driven Architecture** with modern React patterns and state management:

### Core Principles

- **📦 Component Composition** - Reusable UI building blocks with clear interfaces
- **🔄 Unidirectional Data Flow** - Predictable state updates with Zustand
- **🎯 Type Safety** - Full TypeScript coverage for all components and APIs
- **⚡ Real-time Updates** - WebSocket integration with automatic reconnection
- **🎨 Design System** - Consistent styling with Tailwind CSS utilities
- **🧪 Separation of Concerns** - Clear boundaries between UI, logic, and data layers

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                  Presentation Layer                        │
├─────────────────────┬─────────────────────┬─────────────────┤
│   UI Components     │   Layout Components │   Device Cards  │
│  ┌─────────────┐    │  ┌─────────────┐    │  ┌─────────────┐ │
│  │ToggleButton │    │  │ Header      │    │  │ MotorCard   │ │
│  │SliderControl│    │  │ Dashboard   │    │  │ ValveCard   │ │
│  │DisplayValue │    │  │ Sidebar     │    │  │ ServoCard   │ │
│  │HealthInd... │    │  └─────────────┘    │  │ TempCard    │ │
│  └─────────────┘    │                     │  └─────────────┘ │
└─────────────────────┴─────────────────────┴─────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Logic Layer                              │
├─────────────────────┬─────────────────────┬─────────────────┤
│   Custom Hooks      │   State Management  │  Event Handlers │
│  ┌─────────────┐    │  ┌─────────────┐    │  ┌─────────────┐ │
│  │ useDevice   │    │  │ DeviceStore │    │  │ Control     │ │
│  │ useDevices  │    │  │ (Zustand)   │    │  │ Handlers    │ │
│  │ useWebSocket│    │  │             │    │  │             │ │
│  └─────────────┘    │  └─────────────┘    │  └─────────────┘ │
└─────────────────────┴─────────────────────┴─────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer                            │
├─────────────────────┬─────────────────────┬─────────────────┤
│   API Services      │   WebSocket Client  │   Type Defs     │
│  ┌─────────────┐    │  ┌─────────────┐    │  ┌─────────────┐ │
│  │ Device API  │    │  │ WS Manager  │    │  │ Device      │ │
│  │ Health API  │    │  │ Auto-       │    │  │ Types       │ │
│  │ HTTP Client │    │  │ Reconnect   │    │  │ API Types   │ │
│  └─────────────┘    │  └─────────────┘    │  └─────────────┘ │
└─────────────────────┴─────────────────────┴─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** with npm
- **Backend API** running on localhost:8000 (optional for development)

### Installation & Setup

1. **Navigate to frontend directory**
   ```bash
   cd apps/webapp
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

   The application will be available at:
   - **Dashboard**: http://localhost:5173
   - **Alternate Port**: http://localhost:5174 (if 5173 is busy)

### 🌐 Development Modes

```bash
# Development with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test

# Type checking
npm run type-check

# Linting
npm run lint
```

## 📱 User Interface

### Device Dashboard

The main dashboard provides real-time control and monitoring:

- **🎛️ Motor Control**: PWM speed control (0-255) with RPM display (0-40000)
- **🔧 Valve Control**: Binary open/closed toggle with visual feedback
- **🎯 Servo Control**: Precise positioning (0-180°) with integer validation
- **🌡️ Temperature Display**: Real-time environmental data (read-only)
- **💓 Health Indicators**: Connection status and device availability
- **🔄 Auto-Updates**: Real-time WebSocket synchronization

### Responsive Design

- **📱 Mobile-First**: Optimized for mobile devices and tablets
- **💻 Desktop**: Full-featured desktop experience
- **🎨 Dark/Light**: Automatic theme adaptation (system preference)
- **♿ Accessibility**: ARIA labels and keyboard navigation support

## 🔧 Component Architecture

### UI Components (`src/components/ui/`)

**Core reusable components with consistent design:**

```typescript
// HealthIndicator - Device status visualization
<HealthIndicator 
  status="online" | "offline" | "error"
  label="Motor Status"
  size="sm" | "md" | "lg"
/>

// SliderControl - Numeric value control
<SliderControl
  label="Motor Speed"
  value={128}
  min={0}
  max={255}
  onChange={(value) => handleChange(value)}
  disabled={loading}
/>

// Toggle - Binary state control  
<Toggle
  label="Valve State"
  checked={true}
  onChange={(state) => handleToggle(state)}
  variant="success" | "danger"
/>

// DisplayValue - Read-only data display
<DisplayValue
  label="Temperature"
  value={23.5}
  unit="°C"
  variant="highlighted" | "muted"
/>
```

### Device Components (`src/components/devices/`)

**Device-specific control interfaces:**

- **MotorCard** - Speed control with PWM/RPM conversion
- **ValveCard** - Binary state toggle with animation
- **ServoCard** - Angle positioning with validation
- **TemperatureSensorCard** - Environmental data display

### Layout Components (`src/components/layout/`)

- **Header** - Navigation and system status
- **Dashboard** - Main application layout
- **Sidebar** - Device navigation (expandable)

## 🗄️ State Management

### Zustand Store (`src/store/deviceStore.ts`)

**Centralized state with type-safe actions:**

```typescript
// Device state interface
interface Device {
  device_id: string;
  device_type: 'motor' | 'servo' | 'valve' | 'temperature';
  status: 'online' | 'offline' | 'error';
  current_value: number | boolean | object;
  loading: boolean;
  error?: string;
}

// Store actions
const store = useDeviceStore();
store.loadDevices();                    // Fetch all devices
store.controlMotor('motor_01', 128);    // Control motor speed
store.controlValve('valve_01', true);   // Control valve state
store.controlServo('servo_01', 90);     // Control servo angle
```

### Custom Hooks (`src/hooks/`)

**Device-specific data access:**

```typescript
// Generic device management
const { health, connection, getDevicesArray } = useDevices();

// Type-specific device access
const motors = useMotors();           // Motor[] 
const valves = useValves();           // Valve[]
const servos = useServos();           // Servo[]
const sensors = useTemperatureSensors(); // TemperatureSensor[]
```

## 🔌 API Integration

### REST API Service (`src/services/api/devices.ts`)

**Type-safe HTTP client with error handling:**

```typescript
// Device control
await deviceApi.updateDevice('motor_01', { speed: 128 });
await deviceApi.updateDevice('valve_01', { state: true });
await deviceApi.updateDevice('servo_01', { angle: 90 });

// Device status
const device = await deviceApi.getDevice('motor_01');
const allDevices = await deviceApi.getDevices();
const health = await deviceApi.checkHealth();
```

### WebSocket Integration (`src/services/api/websocket.ts`)

**Real-time bi-directional communication:**

```typescript
// WebSocket manager with auto-reconnection
const wsManager = new WebSocketManager('ws://localhost:8000/ws/devices');

// Event handlers
onDeviceUpdate((update: DeviceUpdateMessage) => {
  console.log(`Device ${update.device_id} updated:`, update.new_state);
});

onConnectionStateChange((state: ConnectionState) => {
  console.log('WebSocket connection:', state.status);
});
```

## 📁 Project Structure

```
apps/webapp/
├── README.md                          # This file
├── package.json                       # npm configuration  
├── tsconfig.json                      # TypeScript configuration
├── vite.config.ts                     # Vite build configuration
├── tailwind.config.js                 # Tailwind CSS configuration
├── .prettierrc                        # Code formatting rules
├── docs/                              # Architecture Decision Records
│   ├── ADR-001-frontend-stack.md      # Technology stack decisions
│   └── ADR-002-component-architecture.md # Component design patterns
├── public/                            # Static assets
│   ├── favicon.ico
│   └── manifest.json
└── src/
    ├── main.tsx                       # Application entry point
    ├── App.tsx                        # Root component
    ├── App.css                        # Global styles
    ├── index.css                      # Tailwind CSS imports
    ├── components/                    # 🧩 React Components
    │   ├── ui/                        # Reusable UI components
    │   │   ├── HealthIndicator.tsx    # Status visualization
    │   │   ├── DisplayValue.tsx       # Data display component
    │   │   ├── SliderControl.tsx      # Numeric input control
    │   │   ├── Toggle.tsx             # Binary state control
    │   │   └── index.ts               # Component exports
    │   ├── layout/                    # Layout components
    │   │   ├── Header.tsx             # Navigation header
    │   │   ├── Dashboard.tsx          # Main layout
    │   │   └── index.ts               # Layout exports  
    │   ├── devices/                   # Device-specific components
    │   │   ├── DeviceCard.tsx         # Generic device card
    │   │   ├── MotorCard.tsx          # Motor control interface
    │   │   ├── ValveCard.tsx          # Valve control interface
    │   │   ├── ServoCard.tsx          # Servo control interface
    │   │   ├── TemperatureSensorCard.tsx # Temperature display
    │   │   └── index.ts               # Device exports
    │   └── index.ts                   # All component exports
    ├── hooks/                         # 🪝 Custom React Hooks
    │   ├── useDevice.ts               # Device-specific hooks
    │   ├── useWebSocket.ts            # WebSocket management
    │   └── index.ts                   # Hook exports
    ├── services/                      # 🔧 External Service Integration
    │   └── api/                       # API client layer
    │       ├── devices.ts             # Device REST API client
    │       ├── websocket.ts           # WebSocket client manager
    │       └── index.ts               # Service exports
    ├── store/                         # 🏪 State Management
    │   ├── deviceStore.ts             # Zustand device store
    │   └── index.ts                   # Store exports
    ├── types/                         # 📘 TypeScript Definitions
    │   ├── devices.ts                 # Device type definitions
    │   └── index.ts                   # Type exports
    ├── config/                        # ⚙️ Configuration
    │   ├── api.ts                     # API endpoints and settings
    │   └── index.ts                   # Config exports
    └── utils/                         # 🛠️ Utility Functions
        └── index.ts                   # Utility exports
```

## 🎨 Design System

### Tailwind CSS Configuration

**Custom design tokens and utilities:**

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: { /* Custom color palette */ },
        secondary: { /* Device state colors */ },
      },
      animation: {
        'pulse-slow': 'pulse 3s infinite',
        'bounce-gentle': 'bounce 2s infinite',
      }
    }
  }
};
```

### Component Styling Patterns

- **🎯 Utility-First** - Tailwind CSS for rapid development
- **🔄 Responsive** - Mobile-first responsive design patterns
- **🎨 Consistent** - Design token system for colors and spacing
- **♿ Accessible** - WCAG 2.1 AA compliance with proper contrast ratios

## 🔄 Real-time Features

### WebSocket Integration

**Automatic device synchronization:**

- ✅ **Auto-Reconnection** - Handles network interruptions gracefully
- ✅ **Message Queuing** - Buffers updates during disconnections
- ✅ **Error Recovery** - Exponential backoff retry strategy
- ✅ **State Synchronization** - Automatic UI updates on device changes
- ✅ **Connection Status** - Visual feedback for connection health

### Optimistic Updates

**Responsive user interactions:**

1. **Immediate UI Update** - Control reflects change instantly
2. **Backend Request** - API call sent asynchronously  
3. **Confirmation/Rollback** - Update confirmed or reverted based on response
4. **WebSocket Sync** - Real-time updates from other clients

## 🧪 Testing Strategy

### Testing Setup

```bash
# Run unit tests
npm run test

# Run tests in watch mode  
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### Testing Patterns

- **🧩 Component Tests** - React Testing Library for UI components
- **🪝 Hook Tests** - Custom hook testing with renderHook
- **🔌 Integration Tests** - API client and WebSocket testing
- **📱 E2E Tests** - End-to-end user workflow testing
- **🎭 Mock Strategies** - MSW for API mocking in tests

## 🚀 Build & Deployment

### Production Build

```bash
# Build for production
npm run build

# Preview production build locally
npm run preview

# Analyze bundle size
npm run build-analyze
```

### Environment Configuration

```bash
# Development
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000

# Production  
VITE_API_BASE_URL=https://api.production.com
VITE_WS_BASE_URL=wss://api.production.com
```

### Docker Support

```dockerfile
# Multi-stage build for optimal size
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

## 📋 Key Features

- ✅ **Real-time Dashboard** - Live device monitoring and control
- ✅ **Type-Safe Development** - Full TypeScript coverage
- ✅ **Responsive Design** - Mobile-first adaptive interface
- ✅ **Component Library** - Reusable UI building blocks
- ✅ **WebSocket Integration** - Real-time bi-directional communication
- ✅ **State Management** - Predictable updates with Zustand
- ✅ **Error Handling** - Comprehensive error boundaries and recovery
- ✅ **Accessibility** - WCAG 2.1 AA compliance
- ✅ **Performance** - Code splitting and lazy loading
- ✅ **Developer Experience** - Hot reload, TypeScript, ESLint

## 🤝 Contributing

1. Follow React and TypeScript best practices
2. Maintain component composition patterns
3. Document component interfaces with TSDoc
4. Ensure responsive design across all screen sizes
5. Test components with React Testing Library
6. Follow conventional commits for messages
7. Update ADRs for architectural decisions

---

**Built with ❤️ using React 18, TypeScript 5, Vite, and modern frontend architecture.**