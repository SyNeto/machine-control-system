# ADR-001: Frontend Stack - React + TypeScript + Tailwind + Zustand + Vite + Recharts


## Context
We need a modern frontend stack that enables rapid development, maintainable code, and good user experience. Additionally, the IoT dashboard requires data visualization capabilities for device metrics and historical data.

## Decision
**Selected stack:**
- **Framework**: React + TypeScript
- **Styling**: Tailwind CSS  
- **State Management**: Zustand
- **Build Tool**: Vite
- **Charts/Visualization**: Recharts

## Evaluated Alternatives

| Category | Selected | Alternatives Considered | Selection Reason |
|-----------|--------------|---------------------------|-------------------|
| **Framework** | React + TS | Vue 3, Angular | Mature ecosystem, native TypeScript, high adoption |
| **Styling** | Tailwind | Styled Components, CSS Modules | Rapid development, consistent system, less CSS |
| **State Management** | Zustand | Redux Toolkit, Context API | Simple API, small bundle, no boilerplate |
| **Build Tool** | Vite | CRA, Next.js | Instant HMR, fast builds, minimal config |
| **Charts** | Recharts | Chart.js, D3.js, Victory | React-native, declarative, TypeScript support |

## Justification

### React + TypeScript
- **Robust ecosystem** with extensive community support
- **TypeScript** improves maintainability and catches errors early
- **Architectural flexibility** for different patterns

### Tailwind CSS
- **Development speed** with utility classes
- **Automatic visual consistency**
- **Optimized bundle** with CSS purging of unused styles

### Zustand
- **Extreme simplicity** (~800 bytes)
- **TypeScript-first** with excellent type inference
- **No boilerplate** compared to Redux

### Vite
- **Fast development** with near-instant HMR
- **Optimized builds** for production
- **Minimal configuration** out-of-the-box

### Recharts
- **React-native** components with declarative API
- **TypeScript support** with proper type definitions  
- **Responsive design** built-in for different screen sizes
- **Customizable** styling that integrates well with Tailwind
- **Lightweight** compared to D3.js for simple to medium complexity charts
- **Perfect fit** for IoT dashboard metrics (line charts, bar charts, gauges)

## Consequences

### ✅ Positive
- Higher development productivity
- More maintainable and typed code
- Agile development experience
- Scalable and flexible stack
- **Easy data visualization** for device metrics and trends
- **Consistent chart styling** with Tailwind integration

### ⚠️ Considerations
- Initial learning curve for Tailwind
- Higher number of dependencies
- More elaborate initial setup
- **Additional bundle size** from Recharts library

### 🔧 Mitigations
- Recharts tree-shaking reduces bundle impact
- Documentation and examples for chart components
- Reusable chart component library

## Implementation
1. Configure linting (ESLint + Prettier)
2. Scalable folder structure
3. Clear naming conventions
4. Path aliases for clean imports
5. **Chart component library** with common IoT visualizations
6. **Responsive chart configurations** for mobile and desktop

## Chart Requirements Coverage
- **Real-time metrics**: Line charts for temperature, speed, pressure
- **Historical data**: Time series visualizations
- **Status indicators**: Gauges and progress bars
- **Comparative data**: Bar charts for device performance
- **Custom styling**: Integration with Tailwind design system

---
*This ADR documents the technical decision for future reference and onboarding of new developers.*