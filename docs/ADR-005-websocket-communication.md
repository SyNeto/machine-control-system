# ADR-005: Real-Time WebSocket Communication

**Date:** 2025-09-03  
**Author:** Ernesto Jiménez Villaseñor  

## Context

The machine control panel requires real-time communication capabilities to provide immediate feedback on device state changes without the overhead of continuous polling. Users need to see device updates instantly when controls are actuated, and multiple clients should remain synchronized.

Traditional REST APIs require clients to poll for updates, which introduces latency, increases server load, and provides poor user experience for real-time monitoring applications.

## Decision

We will implement **WebSocket-based real-time communication** alongside the existing REST API to provide:

1. **Bidirectional real-time communication** between server and clients
2. **Automatic broadcasting** of device state changes to all connected clients
3. **Selective subscriptions** allowing clients to monitor specific devices
4. **Robust connection management** with error handling and reconnection capabilities
5. **Multiple concurrent client support** for collaborative monitoring

### Architecture Components

#### 1. Connection Manager (`src/infrastructure/api/websockets/manager.py`)
- Centralized WebSocket connection pool management
- Device-specific subscription handling
- Broadcast capabilities for real-time updates
- Connection lifecycle management (connect/disconnect/error handling)

#### 2. WebSocket Endpoints (`src/infrastructure/api/websockets/endpoints.py`)
- WebSocket route handlers for client communication
- Message protocol implementation
- Integration with machine control services
- Real-time device status distribution

#### 3. REST API Integration
- Automatic WebSocket broadcasts when device states change via REST endpoints
- Non-blocking fire-and-forget broadcast implementation
- Fallback graceful degradation if WebSocket service unavailable

## Implementation Details

### WebSocket Endpoint
```
ws://localhost:8000/ws/devices?client_id=<optional_client_id>
```

### Message Protocol

#### Incoming Messages (Client → Server)
```json
// Subscribe to device updates
{"action": "subscribe", "device_id": "motor_01"}

// Unsubscribe from device updates  
{"action": "unsubscribe", "device_id": "motor_01"}

// Get current device status
{"action": "get_status", "device_id": "motor_01"}

// Get all devices status
{"action": "get_all_status"}
```

#### Outgoing Messages (Server → Client)
```json
// Connection establishment
{
  "type": "connection_established",
  "message": "Connected to Machine Control Panel",
  "timestamp": 1725364800.123,
  "total_connections": 3
}

// Real-time device updates (automatic broadcast)
{
  "type": "device_update", 
  "device_id": "motor_01",
  "data": {
    "device_id": "motor_01",
    "device_type": "motor",
    "previous_state": {"speed": 100},
    "new_state": {"speed": 150}, 
    "changed": true,
    "action": "device_control"
  },
  "timestamp": 1725364800.789
}

// Error messages
{
  "type": "error",
  "error_code": "device_not_found", 
  "message": "Device motor_99 not found",
  "timestamp": 1725364800.567
}
```

### Integration with REST API

The WebSocket system integrates seamlessly with existing REST endpoints:

1. **Client sends REST request** → `POST /api/v1/devices/motor_01 {"speed": 150}`
2. **Server processes update** → Updates device state, returns REST response
3. **Server broadcasts change** → Sends WebSocket update to all connected clients
4. **All clients receive update** → UIs update automatically without additional requests

### Connection Management Features

- **Automatic connection handling**: Accept/reject connections with logging
- **Subscription management**: Per-device subscription tracking
- **Broadcast optimization**: Concurrent message delivery with failure handling
- **Connection cleanup**: Automatic cleanup of failed/disconnected clients
- **Error resilience**: Non-blocking broadcasts that don't affect REST operations

## Alternatives Considered

### 1. Server-Sent Events (SSE)
- **Pros**: Simpler implementation, HTTP-based
- **Cons**: Unidirectional only, limited browser connection limits
- **Verdict**: Rejected due to lack of bidirectional communication

### 2. Polling-based updates
- **Pros**: Simple implementation, works with existing REST API
- **Cons**: High latency, increased server load, poor user experience
- **Verdict**: Rejected due to performance and UX concerns

### 3. WebRTC Data Channels
- **Pros**: Peer-to-peer communication, very low latency
- **Cons**: Complex implementation, NAT traversal issues, overkill for this use case
- **Verdict**: Rejected due to complexity vs. benefit ratio

## Benefits

### Technical Benefits
- **Real-time responsiveness**: Sub-second update delivery
- **Efficient resource usage**: No continuous polling overhead
- **Scalable architecture**: Supports multiple concurrent clients
- **Robust error handling**: Graceful degradation and recovery
- **Clean separation**: WebSocket layer doesn't affect existing REST API

### User Experience Benefits
- **Immediate feedback**: Users see device changes instantly
- **Synchronized views**: Multiple users see consistent state
- **Responsive interface**: UI updates without user-initiated refreshes
- **Better engagement**: Real-time interaction feels more responsive

### Development Benefits
- **Clear protocol**: Well-defined message types and error codes
- **Easy integration**: Simple client-side implementation
- **Testable**: Comprehensive test coverage for all scenarios
- **Maintainable**: Modular design with clear responsibilities

## Risks and Mitigations

### Risk: WebSocket Connection Stability
- **Mitigation**: Automatic reconnection logic in client implementations
- **Mitigation**: Connection heartbeat monitoring
- **Mitigation**: Graceful fallback to REST polling if WebSocket unavailable

### Risk: Message Delivery Guarantees
- **Mitigation**: At-least-once delivery for critical updates
- **Mitigation**: Client can request current state on reconnection
- **Mitigation**: State reconciliation on connection establishment

### Risk: Scalability Under Load
- **Mitigation**: Connection pooling and efficient broadcast algorithms
- **Mitigation**: Per-device subscription filtering to reduce message volume
- **Mitigation**: Async/await implementation for non-blocking operations

### Risk: Security Considerations
- **Mitigation**: Same authentication/authorization as REST API
- **Mitigation**: Input validation on all incoming WebSocket messages
- **Mitigation**: Rate limiting on message frequency

## Implementation Status

### ✅ Completed
- WebSocket connection manager with full lifecycle handling
- Message protocol implementation with comprehensive error handling
- Integration with existing REST API endpoints
- Automatic broadcasting of device state changes
- Device-specific subscription capabilities
- Comprehensive test suite (8 test cases covering all scenarios)
- Client-side React integration examples and documentation

### 📊 Test Coverage
- **WebSocket endpoints**: 8 passing tests
- **Connection management**: All connection lifecycle scenarios tested
- **Message protocol**: All message types and error conditions tested
- **Integration**: REST API WebSocket broadcasting verified

### 🔧 Configuration
```python
# WebSocket settings (configurable)
MAX_CONNECTIONS = 100  # Maximum concurrent connections
HEARTBEAT_INTERVAL = 30  # Seconds between heartbeat checks  
RECONNECT_DELAY = 3  # Seconds before auto-reconnect attempt
MESSAGE_SIZE_LIMIT = 1024  # Maximum message size in bytes
```

## Future Enhancements

### Phase 2: Advanced Features
- **Message persistence**: Store and replay missed messages for reconnecting clients
- **Connection authentication**: Integrate with user authentication system
- **Performance metrics**: Connection count, message throughput monitoring
- **Rate limiting**: Prevent WebSocket message abuse

### Phase 3: Extended Capabilities  
- **Device groups**: Bulk operations and group subscriptions
- **Historical data streaming**: Real-time charts and trend data
- **Alert system**: Configurable real-time notifications
- **Multi-tenancy**: Isolated device access per user/organization

## Client Integration Guide

### React Hook Example
```jsx
const { 
  devices, 
  connectionStatus, 
  subscribeToDevice 
} = useDeviceWebSocket('my_client_id');

// Automatic UI updates when devices change
useEffect(() => {
  console.log('Devices updated:', devices);
}, [devices]);
```

### Connection Workflow
1. **Connect**: `new WebSocket('ws://localhost:8000/ws/devices')`
2. **Receive welcome**: Initial connection confirmation and device status
3. **Subscribe**: Send subscription messages for devices of interest
4. **Receive updates**: Handle real-time device update messages
5. **Control devices**: Use REST API, automatically receive WebSocket confirmations

## Conclusion

The WebSocket implementation provides a robust, scalable foundation for real-time machine control panel communication. The solution balances simplicity with feature completeness, ensuring excellent user experience while maintaining system reliability.

The architecture supports current requirements while providing extensibility for future enhancements such as authentication, performance monitoring, and advanced notification systems.

**This ADR establishes WebSockets as the standard for real-time communication in the machine control system.**
