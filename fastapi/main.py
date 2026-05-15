from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Knowledge Base - AI Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers will be created in Task 7, import after routes/ files exist
try:
    from routes.ingest import router as ingest_router
    app.include_router(ingest_router)
except ImportError:
    pass

try:
    from routes.chat import router as chat_router
    app.include_router(chat_router)
except ImportError:
    pass

try:
    from routes.health import router as health_router
    app.include_router(health_router)
except ImportError:
    pass

try:
    from routes.metadata import router as metadata_router
    app.include_router(metadata_router)
except ImportError:
    pass
