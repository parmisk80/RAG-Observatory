# Agent Context — RAG Observatory

## System Identity

Project Name:

RAG Observatory

Tags : #python #modular_monolith #celery #FastAPI

Type:

Production-inspired modular Retrieval-Augmented Generation platform.

Primary Objective:

Build a highly observable, traceable, and extensible RAG system where every stage of the AI lifecycle can be monitored, evaluated, measured, and improved independently.

This system prioritizes:

- Observability
- Reliability
- Modularity
- Scalability
- Evaluation
- Explainability

This is NOT a chatbot project.

The system should be treated as an AI infrastructure platform.

---

# Core Mental Model

Think of the system as:

```text
Request
    ↓

Pipeline Orchestrator
    ↓

Independent Processing Modules
    ↓

Evaluation
    ↓

Observability Layer
```

Modules should behave as isolated services.

Modules communicate through defined interfaces and should not tightly couple to one another.

---

# Architecture Style

Current architecture:

```text
Modular Monolith
```

Long-term target:

```text
Distributed Event-Driven Architecture
```

The current design intentionally preserves boundaries so modules can later become microservices.

---

# System Components

Core components:

```text
FastAPI
Celery
Redis
PostgreSQL
ChromaDB
Prometheus
Loki
Grafana
Flower
Sentry
Docker
```

Responsibilities:

FastAPI:

- API layer
- request validation
- middleware
- routing

Celery:

- asynchronous execution
- background processing

Redis:

- broker
- cache

PostgreSQL:

- metadata persistence
- request history
- analytics

ChromaDB:

- vector storage

Observability stack:

- metrics
- logs
- traces

---

# Pipeline Execution Flow

Current pipeline:

```text
Rewrite
    ↓

Embedding
    ↓

Retrieval
    ↓

Generation
    ↓

Evaluation
```

Possible future pipeline:

```text
Rewrite
    ↓

Hybrid Retrieval
    ↓

Reranking
    ↓

Generation
    ↓

Judge LLM
    ↓

Evaluation
```

Agents must assume pipeline stages can change.

Never hardcode stage assumptions.

---

# Development Rules

## Rule 1

Never place business logic inside API routes.

Bad:

```python
@router.post("/ask")
async def ask():

    docs = chroma.search()

    result = llm.generate()
```

Good:

```python
@router.post("/ask")
async def ask():

    return await pipeline_service.execute()
```

---

## Rule 2

Modules own their logic.

Retrieval module:

Allowed:

- search
- ranking
- filtering

Not allowed:

- generation
- evaluation

---

## Rule 3

Avoid tight coupling.

Bad:

```python
retrieval_module.generation_module.run()
```

Good:

```python
pipeline.execute_stage()
```

---

## Rule 4

Every module emits observability data.

Required:

Logs

Metrics

Tracing

Latency

Errors

---

## Rule 5

Long-running tasks must be asynchronous.

Use:

Celery

Do not:

Block API workers

---

## Rule 6

All operations should be retry-safe.

Tasks must be idempotent.

Repeated execution should not create inconsistent state.

---

# Coding Standards

Preferred:

```python
async def function():
```

Avoid:

```python
def function():
```

for I/O-heavy operations.

---

Use:

```python
logger.info()
```

Never:

```python
print()
```

---

Use:

```python
pydantic models
```

for validation.

---

Use:

```python
dependency injection
```

for services.

---

Avoid:

Global state

---

# Observability Requirements

Every request must contain:

```text
request_id
trace_id
correlation_id
```

These identifiers must propagate through:

```text
API
↓
Celery
↓
Workers
↓
Database
↓
LLM
↓
Logs
```

---

# Required Logging Fields

```json
{
    "request_id":"",
    "trace_id":"",
    "stage":"",
    "status":"",
    "latency_ms":"",
    "message":""
}
```

---

# Required Metrics

Infrastructure:

- CPU
- Memory
- Queue depth
- Worker count

Application:

- API latency
- Error rate
- Request count

AI:

- Retrieval latency
- Faithfulness
- Context precision
- Hallucination score
- Token usage

---

# Agent Decision Rules

When modifying the system:

1. Preserve modularity

2. Preserve observability

3. Preserve async execution

4. Avoid introducing coupling

5. Preserve stage boundaries

6. Design for horizontal scaling

7. Prefer extension over replacement

---

# Extension Strategy

New features should be implemented as isolated modules.

Example:

Add:

```text
modules/

    reranking/

    judge_llm/

    memory/

    semantic_router/
```

instead of modifying unrelated components.

---

# Known Future Extensions

Planned:

- Hybrid retrieval
- Multi-LLM support
- Distributed workers
- Kubernetes deployment
- Agent routing
- Semantic cache
- Knowledge graphs
- Memory systems
- Streaming responses

---

# Agent Goal

Agents working on this project should optimize for:

1. maintainability

2. observability

3. scalability

4. reliability

5. extensibility

6. retrieval quality

7. evaluation quality

Code should feel production-oriented rather than experimental.
