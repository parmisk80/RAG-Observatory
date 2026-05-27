[README.md](https://github.com/user-attachments/files/28317523/README.md)
# RAG Observatory

A Modular and Observable Retrieval-Augmented Generation (RAG) System    
Built with FastAPI, Docker, ChromaDB, PostgreSQL, Redis, Prometheus, Loki, and Grafana.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# Project Vision

RAG Observatory is not designed as a simple chatbot project.

The purpose of this system is to build a production-inspired AI platform that focuses on:

\- Modular AI Architecture  
\- Observability  
\- Monitoring  
\- Evaluation  
\- Logging  
\- Traceability  
\- Scalability

This project combines and integrates concepts from multiple research areas:

\- Query Rewriting  
\- Modular RAG Systems  
\- RAGAS Evaluation  
\- AI Observability  
\- Monitoring & Logging Systems

The result is a complete AI pipeline that allows visibility into every stage of Retrieval-Augmented Generation.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# High-Level System Flow

text User  → FastAPI REST API  →Pipeline Orchestrator  → Query Rewriting  → Embedding Generation  → Vector Retrieval  → LLM Generation  → RAGAS Evaluation  → Observability Layer  → Grafana Dashboards 

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# Core System Architecture

text app/ ├── api/ │   └── routes/ │ ├── core/ │ ├── models/ │ ├── modules/ │   ├── ingestion/ │   ├── retrieval/ │   ├── generation/ │   ├── evaluation/ │   └── orchestration/ │ ├── infrastructure/ │   ├── logging/ │   ├── monitoring/ │   └── cache/ │ └── main.py 

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# Main Components

# 1\. FastAPI Backend

The backend is built using FastAPI.

Responsibilities:

\- REST API handling  
\- Request validation  
\- Route management  
\- Async processing  
\- API documentation  
\- Middleware integration

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# 2\. Pipeline Orchestrator

The orchestrator controls the execution flow of the entire RAG pipeline.

Responsibilities:

\- Managing pipeline stages  
\- State management  
\- Stage transitions  
\- Failure handling  
\- Request tracing  
\- Metrics collection

Pipeline Flow:

text rewrite  → retrieval  → generation  → evaluation 

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# 3\. Query Rewriting Module

This module improves the quality of user queries before retrieval.

Purpose:

\- Improve retrieval quality  
\- Reduce ambiguity  
\- Increase semantic matching accuracy

Example:

text Original Query: "Tell me about Docker"  Rewritten Query: "What is Docker and how does containerization work?" 

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# 4\. Document Ingestion Pipeline

This subsystem converts raw documents into searchable vector knowledge.

Flow:

text Document Upload  ↓ Parsing  ↓ Cleaning  ↓ Chunking  ↓ Embedding  ↓ Vector Storage 

Supported Formats:

\- PDF  
\- TXT  
\- Markdown  
\- DOCX

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# 5\. Chunking Strategy

The system uses recursive semantic-aware chunking.

Purpose:

\- Preserve context  
\- Improve retrieval quality  
\- Reduce hallucination

Chunk Flow:

text Large Document  ↓ Semantic Sections  ↓ Smaller Chunks  ↓ Embedding Generation 

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# 6\. Embedding System

Each chunk is converted into vector embeddings.

Embedding Purpose:

\- Semantic search  
\- Vector similarity matching  
\- Context retrieval

Technology:

\- Sentence Transformers

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# 7\. Vector Database

The system uses ChromaDB as the vector database.

Responsibilities:

\- Store embeddings  
\- Semantic vector search  
\- Similarity retrieval

Stored Data:

text Chunk Text Embedding Vector Metadata Document References 

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# 8\. Metadata Database

The system uses PostgreSQL for relational and metadata storage.

Responsibilities:

\- Document metadata  
\- Request history  
\- Analytics metadata  
\- System records

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# 9\. Cache Layer

The system uses Redis for caching.

Cached Data:

\- Query cache  
\- Embedding cache  
\- Retrieval cache

Purpose:

\- Reduce latency  
\- Reduce repeated computation  
\- Improve performance

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# API Architecture

Main REST API Endpoints:

text POST   /api/v1/ask POST   /api/v1/documents/upload POST   /api/v1/retrieval/search POST   /api/v1/evaluate GET    /api/v1/metrics GET    /health 

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# Stage Management

The pipeline is stage-based.

Stages:

text 1\. Rewrite 2\. Embedding 3\. Retrieval 4\. Generation 5\. Evaluation 

Each stage contains:

\- Status tracking  
\- Latency tracking  
\- Error handling  
\- Logging  
\- Metrics

Stage States:

text pending running completed failed skipped 

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# Logging Architecture

The system uses structured JSON logging.

Logging Flow:

text FastAPI  ↓ Structured Logs  ↓ Loki  ↓ Grafana 

Logged Information:

\- Request IDs  
\- Retrieval results  
\- Errors  
\- Latency  
\- Pipeline stages  
\- Evaluation scores

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# Monitoring Architecture

Monitoring is implemented using Prometheus and Grafana.

Monitoring Flow:

text FastAPI Metrics  ↓ Prometheus  ↓ Grafana Dashboards 

Monitored Metrics:

\- API latency  
\- Error rates  
\- Retrieval latency  
\- Token usage  
\- Hallucination metrics  
\- Evaluation scores  
\- System health

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# Observability Stack

The system uses Grafana Labs tools for observability.

Components:

| Tool | Purpose |  
|---|---|  
| Grafana | Visualization & Dashboards |  
| Prometheus | Metrics Collection |  
| Loki | Log Aggregation |

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# Background Task Processing

The system uses Celery for asynchronous and distributed background task execution.

Celery is responsible for handling long-running and resource-intensive operations outside the main API request cycle.

Background Tasks Include:

- Document ingestion
- Embedding generation
- RAG evaluation
- Metrics aggregation
- Scheduled monitoring jobs

Task Flow:

text FastAPI Request  ↓ Celery Task Queue  ↓ Worker Execution  ↓ Result Storage 

Benefits of Celery Integration:

- Non-blocking API responses
- Improved scalability
- Better resource management
- Async document processing
- Distributed task execution

Technologies Used:

- Celery
- Redis (Message Broker)
- FastAPI

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# Docker Architecture

The entire platform is containerized using Docker.

Container Flow:

text User  → FastAPI Container  → PostgreSQL Container  → ChromaDB Container  → Redis Container  → Grafana Stack 

Docker Components:

\- Dockerfile  
\- Docker Compose  
\- Multi-service Architecture

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# System Design Principles

The project follows these engineering principles:

\- Modular Monolith Architecture  
\- Separation of Concerns  
\- Observable Systems  
\- Async-ready Design  
\- Scalable Infrastructure  
\- Production-inspired Engineering

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# Future Improvements

Planned future extensions:

\- Hybrid Retrieval  
\- Multi-LLM Support  
\- Authentication & Authorization  
\- Streaming Responses  
\- Distributed Workers  
\- Kubernetes Deployment  
\- Advanced Evaluation Pipelines  
\- Semantic Routing  
\- Memory Systems  
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# Main Goal of the Project

The goal of this project is to move beyond a traditional academic implementation and build a real-world inspired AI system architecture.

This platform focuses not only on generating answers, but also on:

\- Understanding system behavior  
\- Monitoring AI quality  
\- Evaluating retrieval performance  
\- Observing pipeline execution  
\- Measuring hallucination  
\- Building scalable AI infrastructure

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# Technologies Used

| Category | Technology |  
| Backend API | FastAPI | Celery
| Validation | Pydantic |  
| Vector Database | ChromaDB |  
| Relational Database | PostgreSQL |  
| Cache | Redis |  
| Monitoring | Prometheus |  
| Logging | Loki |  
| Dashboards | Grafana |  
| Containerization | Docker |  
| Orchestration | Docker Compose |

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

# Project Summary

RAG Observatory is a modular, observable, and production-inspired AI platform that combines Retrieval-Augmented Generation, observability engineering, evaluation systems, monitoring infrastructure, and scalable backend architecture into a unified system.

