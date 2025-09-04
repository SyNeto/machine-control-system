# ADR-003: Adoption of Dependency Injection for Hexagonal Architecture Assembly

**Date:** 2025-09-03  
**Author:** Ernesto Jiménez Villaseñor

## Context

Our IoT device management system follows Hexagonal Architecture (Ports & Adapters pattern) to maintain clean separation between domain logic and infrastructure concerns. As the system grows with multiple device adapters and application services, we need a robust mechanism to:

1. **Wire components across layers** without tight coupling between domain and infrastructure
2. **Manage object lifecycle** ensuring proper state management for stateful devices
3. **Enable testability** by allowing easy substitution of real adapters with test doubles
4. **Support configuration-driven deployment** for different environments and device setups
5. **Maintain architectural boundaries** preventing domain contamination with infrastructure details

The challenge lies in assembling the complete application while respecting the dependency inversion principle - domain ports should not know about concrete infrastructure adapters, yet the application needs to connect them at runtime.

## Decision

We will adopt **Dependency Injection (DI)** using the `dependency-injector` library with YAML-based configuration to assemble our hexagonal architecture layers.

The `dependency-injector` library was selected for its active maintenance, stable API, and established community support, providing confidence in long-term project sustainability and available resources for troubleshooting.

### Core Principles

1. **Inversion of Control**: Application services receive dependencies through constructor injection rather than creating them directly
2. **Configuration Externalization**: Device and service configurations are defined in YAML files, separate from business logic  
3. **Singleton Lifecycle**: Infrastructure adapters use singleton scope to maintain device state across the application lifecycle
4. **Container Composition**: Separate containers for different concerns (devices, services, application) with clear boundaries

### Implementation Strategy

- **Infrastructure Layer**: Contains DI containers and configuration loading
- **Adapter Registration**: Each infrastructure adapter registered as singleton provider
- **Service Assembly**: Application services receive domain ports as constructor dependencies
- **Configuration Management**: YAML files define concrete implementations and their parameters
- **Factory Pattern**: Container factory provides global access while maintaining testability

## Consequences

### Positive

- **Loose Coupling**: Domain layer remains independent of infrastructure implementations
- **Testability**: Easy to substitute real adapters with mocks for unit testing
- **Configuration Flexibility**: Runtime assembly based on external configuration files
- **State Management**: Singleton adapters maintain device state consistently
- **Architectural Compliance**: Enforces proper dependency direction (infrastructure → domain)
- **Maintainability**: Clear separation of concerns with explicit dependency graphs

### Negative

- **Additional Complexity**: Introduces DI framework learning curve and setup overhead
- **Runtime Dependencies**: Configuration errors only surface at application startup
- **Framework Lock-in**: Dependency on external DI library for core application assembly
- **Debugging Complexity**: Dependency resolution happens at container level, not in business logic

### Neutral

- **Performance Impact**: Minimal overhead as singletons are resolved once at startup
- **Configuration Maintenance**: YAML files require updates when adding new devices or services

## Alternatives Considered

### Manual Factory Pattern
Creating custom factory classes for each layer assembly. Rejected due to increased boilerplate and manual lifecycle management complexity.

### Service Locator Pattern  
Using a central registry for dependency lookup. Rejected as it creates hidden dependencies and makes testing more difficult.

### Framework-specific DI
Using web framework built-in DI (FastAPI, Django). Rejected to maintain framework independence and support multiple deployment scenarios.

## Implementation Notes

- DI configuration resides in `src/infrastructure/di/` to maintain architectural boundaries
- YAML configuration files externalized to `config/` directory for environment-specific deployments
- Container factory provides singleton access pattern while preserving testability through reset mechanisms
- Future application services will receive domain ports as constructor parameters, maintaining clean dependency direction

---

**Date**: 2025-09-03  
**Author**: Development Team  
**Reviewers**: Architecture Review Board
