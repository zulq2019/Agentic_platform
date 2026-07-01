# Platform Object Framework — Architecture Diagram

**Story:** US-02.01  
**PI:** PI-02 Metadata Engine

```mermaid
flowchart TB
    subgraph Contract
        PO_SCHEMA[platform-object.schema.json]
    end

    subgraph aep_meta["aep_meta library"]
        PO[PlatformObject aggregate]
        VAL[PlatformObjectValidator]
        SVC[PlatformObjectService]
        LSM[LifecycleStateMachine]
        PO --> VAL
        VAL --> SVC
        LSM --> PO
    end

    subgraph Ports
        REPO[PlatformObjectRepository]
        AUDIT[AuditRecorderPort]
        MET[MetricsRecorderPort]
    end

    subgraph metadata_engine["metadata-engine service"]
        API[REST API /api/v1/platform-objects]
        API --> SVC
    end

    subgraph Persistence
        MEM[InMemoryRepository]
        PG[(metadata.platform_objects)]
    end

    PO_SCHEMA --> VAL
    SVC --> REPO
    SVC --> AUDIT
    SVC --> MET
    REPO --> MEM
    REPO -.-> PG
```

## Layer responsibilities

| Layer | Responsibility |
|-------|----------------|
| **Contract** | Authoritative JSON Schema for all primitives |
| **Domain** | Identity, metadata, lifecycle, relationships — no I/O |
| **Application** | Validation orchestration, lifecycle use cases |
| **Infrastructure** | Schema adapter, repository implementations |
| **Service** | HTTP adapter only — no business rules |
