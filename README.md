# AI Knowledge Base

基于 RAG（检索增强生成）的智能知识库系统，支持文档管理、向量检索和 AI 对话问答。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + Vue Router |
| 后端 | Spring Boot 3.2 + JPA + Spring Security + JWT |
| AI 服务 | FastAPI + LangChain + ChromaDB |
| 数据库 | MySQL 8.0 + Redis 7 |
| 向量存储 | ChromaDB |
| 部署 | Docker Compose（一键启动 6 个服务） |

## 功能

- **用户认证** — JWT 登录 / 注册
- **知识库管理** — 文档上传、列表查看
- **AI 对话** — 基于知识库文档的 RAG 问答，带来源追溯
- **文档向量化** — 上传后自动分块、向量嵌入并存入 ChromaDB
- **多 LLM 支持** — DeepSeek / OpenAI / 智谱 / 通义千问 / Ollama 可切换

## 项目结构

```
├── frontend/          # Vue 3 前端
│   └── src/
│       ├── views/     # LoginView / KnowledgeView / ChatView
│       ├── router/    # 路由配置
│       └── api/       # Axios 接口封装
├── springboot/        # Spring Boot 后端
│   └── src/main/java/com/kb/
│       ├── controller/  # REST API
│       ├── service/     # 业务逻辑
│       ├── model/       # 实体 / DTO
│       ├── repository/  # JPA Repository
│       ├── security/    # JWT 认证与鉴权
│       └── client/      # FastAPI 客户端
├── fastapi/           # AI 服务 (Python)
│   ├── routes/        # ingest / chat / health
│   ├── services/      # RAG / embedding / LLM / vector_store
│   ├── models/        # Request / Response Schema
│   └── prompts/       # RAG Prompt 模板
└── docker-compose.yml # 6 服务编排
```

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入 LLM / Embedding API Key
```

### 2. 一键启动

```bash
docker-compose up -d
```

启动后访问：
- 前端页面：http://localhost
- Spring Boot API：http://localhost:8080
- FastAPI AI 服务：http://localhost:8000/docs
- ChromaDB：http://localhost:8001

### 3. 使用流程

1. 访问前端，注册 / 登录账号
2. 进入「知识库」页面上传文档（支持 txt、pdf 等）
3. 文档自动向量化并存入 ChromaDB
4. 进入「对话」页面，基于已上传的知识库文档进行 AI 问答

## LLM 提供商配置

在 `.env` 中配置：

```bash
LLM_PROVIDER=deepseek      # deepseek | openai | zhipu | qwen | ollama
LLM_MODEL=deepseek-chat
LLM_API_KEY=sk-your-key

EMBED_PROVIDER=openai      # openai | zhipu | qwen | ollama
EMBED_MODEL=text-embedding-3-small
EMBED_API_KEY=sk-your-key

JWT_SECRET=your-production-jwt-secret
```

## 服务架构

```
Browser (Vue3) ──→ Nginx :80 ──→ Spring Boot :8080 ──→ MySQL :3306
                                     │                    Redis :6379
                                     └──→ FastAPI :8000 ──→ ChromaDB :8001
                                                               LLM API
                                                               Embedding API
```

- **Nginx** 反向代理前端静态资源和后端 API
- **Spring Boot** 处理用户认证、文档管理、会话管理，对话请求代理转发至 FastAPI
- **FastAPI** 负责文档向量化摄取和 RAG 对话生成
- **ChromaDB** 存储文档向量块，支持语义检索
