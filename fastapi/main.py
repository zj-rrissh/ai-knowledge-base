from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    app = FastAPI(title="AI Knowledge Base - AI Service")

    # CORS - allow all origins during development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Basic health endpoint (always available)
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # Lazy router registration - routers will be created in later tasks
    try:
        from fastapi.routers.ingest import router as ingest_router  # type: ignore
        app.include_router(ingest_router, prefix="/api/v1/ingest", tags=["ingest"])
    except ImportError:
        pass

    try:
        from fastapi.routers.chat import router as chat_router  # type: ignore
        app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
    except ImportError:
        pass

    return app


app = create_app()
