# ADR-001: Modular Architecture for Future Microservices

## Status

Accepted

## Context

The Mimi Core application is initially built as a single service MNVP (Minimum Non-Viable Product), but needs to be architected in a way that allows easy splitting into microservices later.

## Decision

We will use a modular folder structure with clear separation of concerns:

- `app/api/`: HTTP endpoints with no business logic
- `app/services/`: Core business logic services
- `app/models/`: Data transfer objects and type definitions
- `app/policies/`: Processing policies and rules
- `app/infra/`: Infrastructure concerns (config, logging)

Each service will have well-defined interfaces and minimal coupling.

## Consequences

### Positive

- Easy to extract services into separate repositories/containers
- Clear separation of concerns
- Testable components
- Scalable architecture

### Negative

- More complex initial setup
- Slightly more overhead for single-service deployment

---

# ADR-002: Vector Storage Backend Selection

## Status

Accepted

## Context

Need to choose vector storage backend for embeddings and similarity search.

## Decision

Support both Qdrant and OpenAI Vector Store via adapter pattern, configurable by environment variable.

- Qdrant: Self-hosted, full-featured vector database
- OpenAI: Managed service, simpler for small deployments

## Consequences

### Positive

- Flexibility in deployment options
- Can switch backends without code changes
- Testable with different backends

### Negative

- Additional complexity in adapter implementation
- Need to maintain compatibility with both APIs

---

# ADR-003: SQLite for Metadata Storage

## Status

Accepted

## Context

Need lightweight persistence for document metadata, events, and chunk tracking.

## Decision

Use SQLite for metadata storage in MNVP phase.

## Consequences

### Positive

- No external dependencies
- Simple deployment
- ACID compliance
- Good performance for single-service

### Negative

- Not suitable for multi-service architecture
- Will need migration to PostgreSQL/MySQL for microservices
- Limited concurrent write performance
