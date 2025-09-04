# ADR-002: Arquitectura de Componentes Frontend


## Contexto
El dashboard de dispositivos IoT requiere una estructura de componentes escalable, mantenible y que facilite la reutilización de código. Necesitamos una organización clara que separe responsabilidades y permita desarrollo eficiente.

## Decisión

### **Estructura de Carpetas**
```
src/
├── components/
│   ├── layout/          # Componentes de estructura
│   │   ├── Header.tsx
│   │   ├── Dashboard.tsx
│   │   └── index.ts
│   ├── ui/              # Componentes base reutilizables
│   │   ├── HealthIndicator.tsx
│   │   ├── SliderControl.tsx
│   │   ├── Toggle.tsx
│   │   ├── DisplayValue.tsx
│   │   └── index.ts
│   ├── devices/         # Componentes específicos de dispositivos
│   │   ├── DeviceCard.tsx
│   │   ├── MotorCard.tsx
│   │   ├── ValveCard.tsx
│   │   ├── TemperatureSensorCard.tsx
│   │   ├── ServoMotorCard.tsx
│   │   └── index.ts
│   └── index.ts
├── types/               # TypeScript types
│   └── devices.ts
└── store/               # Zustand stores
    └── deviceStore.ts
```

## Alternativas Consideradas

| Enfoque | Pros | Contras | Decisión |
|---------|------|---------|----------|
| **Separación por dominio** | Clara separación de responsabilidades | Mejor escalabilidad | ✅ **Seleccionado** |
| **Carpeta plana** | Simplicidad inicial | No escala, difícil navegación | ❌ Descartado |
| **Por tipo de archivo** | Agrupación técnica | Lógica de negocio dispersa | ❌ Descartado |
| **Atomic Design** | Metodología probada | Complejidad innecesaria para 4 dispositivos | ❌ Overkill |

## Justificación

### **Separación por Dominio**
- **`layout/`**: Componentes estructurales del dashboard
- **`ui/`**: Componentes reutilizables sin lógica de negocio
- **`devices/`**: Lógica específica de cada tipo de dispositivo
- **`types/`**: Definiciones TypeScript centralizadas
- **`store/`**: Estado global con Zustand

### **Ventajas de esta Arquitectura**

#### **🎯 Separación Clara de Responsabilidades**
- Componentes UI puros sin lógica de dispositivos
- Lógica de negocio encapsulada en componentes específicos
- Layout separado de la funcionalidad

#### **🔄 Reutilización Maximizada**
- `SliderControl` usado por Motor y ServoMotor
- `DeviceCard` como base común
- `DisplayValue` compartido entre múltiples dispositivos

#### **📈 Escalabilidad**
- Fácil agregar nuevos tipos de dispositivos
- Componentes UI crecen independientemente
- Store centralizado permite múltiples instancias

#### **🛠️ Mantenibilidad**
- Archivos `index.ts` para exports limpios
- Tipos centralizados evitan duplicación
- Fácil localización de componentes

## Patrones de Componentes

### **Composición sobre Herencia**
```typescript
// DeviceCard como wrapper reutilizable
<DeviceCard title="Motor" status="active">
  <SliderControl value={speed} onChange={setSpeed} />
  <DisplayValue label="Velocidad" value={`${speed} RPM`} />
</DeviceCard>
```

### **Hooks Personalizados**
- Estado de dispositivos centralizado en store
- Lógica reutilizable extraída a hooks
- Separación entre UI y lógica de negocio

### **Props Tipadas**
```typescript
interface SliderControlProps {
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  onChange: (value: number) => void;
}
```

## Consecuencias

### ✅ **Positivas**
- **Desarrollo rápido**: Componentes reutilizables reducen duplicación
- **Testing simplificado**: Componentes aislados y focused
- **Onboarding fácil**: Estructura intuitiva y predecible
- **Extensibilidad**: Fácil agregar nuevos dispositivos o UI components

### ⚠️ **Consideraciones**
- **Setup inicial**: Más archivos que estructura plana
- **Over-engineering**: Podría ser complejo para proyecto muy simple
- **Imports**: Múltiples niveles de carpetas

### 🔧 **Mitigaciones**
- Archivos `index.ts` simplifican imports
- Documentación clara de patrones
- Ejemplos de uso en cada componente

## Reglas de Implementación

1. **Componentes UI**: Solo props, sin estado global
2. **Device Components**: Pueden conectar con store
3. **Layout Components**: Orquestan otros componentes
4. **Un archivo por componente**: Máximo una exportación default
5. **Index files**: Re-exports para imports limpios

## Ejemplo de Uso
```typescript
// ✅ Import limpio
import { MotorCard, ValveCard } from '@/components/devices';
import { Header, Dashboard } from '@/components/layout';

// ✅ Composición clara
<Dashboard>
  <MotorCard deviceId="motor-01" />
  <ValveCard deviceId="valve-01" />
</Dashboard>
```

---
*Esta arquitectura balancea simplicidad actual con necesidades futuras de crecimiento.*