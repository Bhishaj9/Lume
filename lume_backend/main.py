"""
Lume Media Research API - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lume_backend.routers import media


def create_application() -> FastAPI:
    """
    Application factory pattern.
    Allows for easy testing and configuration.
    """
    app = FastAPI(
        title="Lume Media Research API",
        description=""
        "A clean, provider-based API for media research.\n\n"
        "Features:\n"
        "- Abstract Provider Pattern for easy swapping\n"
        "- Pydantic models for type safety\n"
        "- Dependency injection for testability\n"
        "- Comprehensive error handling",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost", "http://10.0.2.2"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(media.router)

    return app


# Create app instance
app = create_application()


@app.get("/", tags=["health"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Lume Media Research API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "resolve": "/resolve/{query}",
            "search": "/resolve/search/{query}",
            "health": "/resolve/health/provider",
        },
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "lume_backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
