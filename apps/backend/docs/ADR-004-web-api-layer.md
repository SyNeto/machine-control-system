# ADR-004: Web API Layer with FastAPI

**Date:** 2025-09-03  
**Author:** Ernesto Jiménez Villaseñor

## Context

El sistema de Machine Control Panel requiere una interfaz web para:
1. **REST API**: Configuración y control de dispositivos desde una aplicación React
2. **WebSockets**: Streaming en tiempo real de datos de sensores con intervalos diferenciados
3. **Integration**: Exposición de la lógica de negocio existente (`MachineControlService`) sin modificar la arquitectura actual

### Requisitos específicos:
- Datos de sensores rápidos (motor, valve, servo): intervalos de 1-5 segundos
- Datos de temperatura: intervalos de 2 minutos (respeto al servicio gratuito OpenMeteo)
- Control de dispositivos via REST endpoints
- Comunicación bidireccional en tiempo real
- Integración transparente con la arquitectura hexagonal existente

### Opciones evaluadas:

1. **FastAPI**: Framework moderno async-first con soporte nativo para REST y WebSockets
2. **Flask + Flask-SocketIO**: Framework tradicional con extensiones para WebSockets
3. **Django + Channels**: Framework completo con manejo de WebSockets via channels
4. **Starlette**: Framework minimalista, base de FastAPI

## Decision

**Adoptamos FastAPI como framework web, ubicado en `src/infrastructure/web/`**

### Justificación técnica:

**FastAPI seleccionado por:**
- ✅ **Async nativo**: Compatible con la arquitectura async existente (`MachineControlService`)
- ✅ **WebSockets built-in**: Sin dependencias adicionales para real-time communication
- ✅ **REST + WebSockets**: Ambos protocolos en una sola aplicación
- ✅ **Pydantic integration**: Validación automática y serialización
- ✅ **OpenAPI docs**: Auto-documentación para el frontend team
- ✅ **Performance**: Uno de los frameworks Python más rápidos
- ✅ **Type hints**: Consistente con el codebase actual

**Ubicación en Infrastructure layer:**
- FastAPI actúa como **Input Adapter** en la arquitectura hexagonal
- Recibe requests HTTP/WebSocket y los traduce a llamadas del dominio
- No contiene lógica de negocio, solo orchestration y serialization
- Permite testing independiente mockando `MachineControlService`

### Arquitectura resultante:

```
src/infrastructure/web/
├── main.py               # FastAPI app + startup/shutdown
├── dependencies.py       # DI container integration
├── routers/
│   ├── devices.py        # REST endpoints (/api/v1/devices)
│   └── websockets.py     # WebSocket handlers (/ws)
├── models/
│   ├── requests.py       # Pydantic request schemas
│   └── responses.py      # Pydantic response schemas
└── background/
    └── sensor_polling.py # Background tasks con intervalos diferenciados
```

### Flujo de dependencias:
```
HTTP/WebSocket Request
    ↓
FastAPI Router (Infrastructure)
    ↓
MachineControlService (Application)
    ↓
IODevice Adapters (Infrastructure)
```

## Consequences

### Positive:
- **Separation of concerns**: Web layer separada de business logic
- **Testability**: Fácil testing unitario e integración
- **Scalability**: Background tasks y WebSocket connection pooling
- **Developer experience**: Auto-docs, type safety, async/await
- **Frontend ready**: REST API + real-time data streaming
- **Rate limiting**: Control granular de intervalos por tipo de sensor

### Negative:
- **New dependency**: Adiciona FastAPI + uvicorn al proyecto
- **Complexity**: Manejo de WebSocket connections y background tasks
- **Memory usage**: Mantener conexiones WebSocket activas

### Risks & Mitigations:

**Risk**: WebSocket connection overload
**Mitigation**: Connection pooling y heartbeat monitoring

**Risk**: Background task conflicts
**Mitigation**: Async locks y proper task lifecycle management

**Risk**: OpenMeteo rate limiting
**Mitigation**: 2-minute intervals específicos para temperature adapter

## Implementation Plan

1. **Phase 1**: Setup básico FastAPI + DI integration
2. **Phase 2**: REST endpoints para device control
3. **Phase 3**: WebSocket handlers + connection management
4. **Phase 4**: Background polling con intervalos diferenciados
5. **Phase 5**: Error handling y monitoring

## Notes

Esta decisión mantiene la arquitectura hexagonal existente intacta, con FastAPI actuando como un adapter de entrada que expone la funcionalidad del `MachineControlService` via HTTP/WebSocket protocols.

El diseño permite evolución futura hacia microservicios si fuera necesario, ya que la web layer está completamente desacoplada de la lógica de dominio.
