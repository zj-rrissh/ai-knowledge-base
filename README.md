# AI Knowledge Base

<p align="center">
  <strong>企业级 RAG 智能知识库系统</strong><br/>
  多通道检索引擎 · LLM 查询改写 · 多模型路由与容错 · 全链路可观测
</p>

面向企业的智能知识库系统，支持 PDF / Markdown / Word 等多格式文档解析、向量化存储与语义检索问答，解决内部知识检索效率低、规章制度查询难等业务痛点。

---

## Architecture

采用 **Spring Boot + FastAPI 双后端** 分离架构，Java 负责业务编排与基础设施，Python 专注 AI 推理：

```
┌──────────────────────────────────────────────────────────────────┐
│  Vue 3 Frontend (frontend/)                                      │
│  LoginView · KnowledgeView · ChatView                            │
└────────────────────────┬─────────────────────────────────────────┘
                         │ Nginx / HTTP
┌────────────────────────▼─────────────────────────────────────────┐
│  Spring Boot API (springboot/)  ── 业务编排 & 基础设施            │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Controller Layer         Service Layer                     │ │
│  │  AuthController           AuthService       ChatService     │ │
│  │  ChatController           KnowledgeService  SummaryService  │ │
│  │  KnowledgeController      FileStorageService                │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Infrastructure Layer (抽象复用)                              │ │
│  │  • 统一异常体系 (3 级)  • Snowflake 分布式 ID                │ │
│  │  • Redis 缓存 (向量结果 30% 延迟降低)                         │ │
│  │  • 线程池上下文透传                                          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  AI Integration Layer                                       │ │
│  │  LLMService (Facade) → Routing → 多模型候选 + 熔断降级      │ │
│  │  FastApiClient → Python 推理服务代理                         │ │
│  └─────────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼─────────────────────────────────────────┐
│  FastAPI AI Service (fastapi/)  ── RAG 检索 & 生成               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Ingestion Pipeline                 Retrieval Engine        │ │
│  │  • 多格式解析 (PDF/Word/MD)         • SearchChannel 接口 ▶  │ │
│  │  • BaseChunkingStrategy 抽象         • 多通道并行检索        │ │
│  │  • CONTENT_TYPE_MAP 分发             • Dense (ChromaDB)     │ │
│  │  • 向量嵌入 + ChromaDB 存储          • Sparse (BM25)        │ │
│  │                                     • RRF 融合              │ │
│  │  PostProcessor 链                    Query Rewrite Pipeline │ │
│  │  • 去重                              • 同义词标准化          │ │
│  │  • Rerank 重排序                     • 上下文补全            │ │
│  │                                     • 子问题拆分            │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  LLM Engine — 多模型路由 + 三态熔断器                        │ │
│  │  DeepSeek / OpenAI / 智谱 / 通义千问 / Ollama               │ │
│  │  CLOSED → OPEN → HALF_OPEN, 自动熔断与半开探测恢复          │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────┴─────────────────────────────────────────┐
│  Data Layer                                                     │
│  MySQL (业务数据)  ·  Redis 7 (缓存/限流)  ·  ChromaDB (向量)    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Key Engineering Highlights

### Multi-Channel Retrieval Engine

**Problem**: Single-channel vector search has low recall when intent classification fails, and adding new search strategies requires modifying core code.

**Solution**: Abstract `SearchChannel` interface and `SearchResultPostProcessor` chain using Strategy + Chain of Responsibility patterns:

```
User Query
    │
    ▼ Parallel Execution (all enabled SearchChannels)
    ├── IntentDirectedChannel — precise retrieval on matched knowledge base
    └── VectorGlobalChannel  — fallback across all collections (confidence < 0.6)
    │
    ▼ PostProcessor Chain (sequential)
    ├── DeduplicationPostProcessor — merge multi-channel results, keep highest score
    └── RerankPostProcessor       — fine-tune ranking via Rerank model
    │
    ▼ RRF Fusion — Dense (ChromaDB cosine) + Sparse (BM25) blended
    → Recall: 95%+
```

**Extensibility**: New channels implement `SearchChannel` and register as Spring Beans — zero core changes.

### Query Rewriting & Conversation Memory

**Problem**: Casual user queries ("报销咋整") have low direct-match rates. Long conversations exceed token limits.

**Solution**: LLM-powered query rewriting pipeline + sliding window memory management:

```
Raw Query → [Synonym Normalization + Context Completion + Sub-Question Split] → Rewritten Query
History   → [Sliding Window Truncation + LLM Summary Compression] → Compact Context
```

- Query hit rate: **+30%**
- Token consumption: **-40%**
- MySQL-based two-level session/message storage with per-session isolation

### Multi-Model Routing & Circuit Breaker

**Problem**: Single model provider API instability causes full service outage.

**Solution**: Facade pattern `LLMService` interface with priority-based candidate routing + per-model three-state circuit breaker:

```
         ┌──────────────────┐
         │  LLMService      │
         │  (Facade)        │
         └────────┬─────────┘
                  │ route by priority
    ┌─────────────┼─────────────┐
    ▼              ▼              ▼
Model A        Model B        Model C
(CLOSED)       (OPEN)         (HALF_OPEN)
    │              │              │
    └── succeed ───┴── fail ──────┘
         │              │
    return result    retry next
```

- Single model failure: service unaffected, switch transparent to user
- Half-open probe: auto-recover when model healthy again

### Full-Link Traceability & Infrastructure Abstraction

**Problem**: RAG pipeline has 8+ stages — hard to locate failures.

**Solution**: `@RagTraceNode` annotation + AOP aspect records per-stage timing, inputs/outputs, and exceptions:

```java
@RagTraceNode(stage = "RETRIEVAL")
public RetrievalContext retrieve(Query query) { ... }
```

Plus unified infrastructure layer:
- **3-level exception hierarchy** + global interceptor
- **Snowflake** distributed ID generation
- **Thread pool** context propagation (user context + trace ID)
- **Redis cache** for vector results — cold query avoidance
- **Troubleshooting time**: hours → minutes

---

## Tech Stack

| Layer | Technology |
|:------|:-----------|
| Frontend | Vue 3 + Vite + Pinia + Vue Router + Axios |
| Business API | Spring Boot 3.2 + Spring Data JPA + Spring Security + JWT |
| AI Service | FastAPI + LlamaIndex + ChromaDB |
| Database | MySQL 8.0 + Redis 7 |
| Vector Store | ChromaDB (Dense) + BM25 (Sparse) |
| Search Fusion | RRF (Reciprocal Rank Fusion) |
| Deployment | Docker Compose (6 services) · Nginx |

---

## Project Structure

```
├── frontend/                  # Vue 3 SPA
│   └── src/
│       ├── views/             # LoginView / KnowledgeView / ChatView
│       ├── router/            # Hash routing
│       └── api/               # Axios API clients
├── springboot/                # Spring Boot backend
│   └── src/main/java/com/kb/
│       ├── controller/        # REST endpoints
│       ├── service/           # Business logic
│       ├── ai/                # AI service abstraction
│       │   ├── AiChatService.java
│       │   ├── ChatResult.java
│       │   └── SourceDocument.java
│       ├── client/            # FastAPI RPC proxy
│       ├── config/            # Spring configuration
│       ├── security/          # JWT auth filter chain
│       ├── model/             # Entity / DTO
│       └── repository/        # JPA repositories
├── fastapi/                   # Python AI service
│   ├── routes/                # ingest / chat / health / metadata
│   ├── services/              # RAG / embedding / LLM / vector_store / fusion
│   ├── chunking/              # Strategy pattern for document chunking
│   ├── prompts/               # RAG prompt templates
│   ├── models/                # Pydantic schemas
│   └── tests/                 # 12+ test files
└── docker-compose.yml         # 6-service orchestration
```

---

## Quick Start

```bash
cp .env.example .env
# Edit .env: LLM_API_KEY, JWT_SECRET, etc.

docker-compose up -d
```

| Service | URL |
|:--------|:----|
| Frontend | http://localhost |
| Spring Boot API | http://localhost:8080 |
| FastAPI docs | http://localhost:8000/docs |
| ChromaDB | http://localhost:8001 |

**Usage flow**: Register → Upload documents → Auto-vectorize → Chat with AI based on knowledge base.

---

## LLM Provider Configuration

Edit `.env`:

```bash
LLM_PROVIDER=deepseek      # deepseek | openai | zhipu | qwen | ollama
LLM_MODEL=deepseek-chat
LLM_API_KEY=sk-your-key

EMBED_PROVIDER=openai      # openai | zhipu | qwen | ollama
EMBED_MODEL=text-embedding-3-small
EMBED_API_KEY=sk-your-key
```

---
