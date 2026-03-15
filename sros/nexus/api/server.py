"""SROS HTTP API Server.

The API runtime is available for internal and experimental use.
Public hardened v1 keeps this surface quarantined.
"""

import logging

logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    FASTAPI_AVAILABLE = False
    logger.warning("FastAPI not installed. API server unavailable.")

if FASTAPI_AVAILABLE:
    from .routes import register_routes, API_STATUS

    app = FastAPI(
        title="SROS API",
        description="Sovereign Runtime Operating System API",
        version="1.0.0a0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_routes(app)

    @app.get("/")
    def root():
        return {
            "name": "SROS API",
            "version": "1.0.0a0",
            "status": "quarantined",
            "api": API_STATUS,
        }

    @app.get("/health")
    def health():
        return {"status": "healthy", "api_surface": "quarantined"}
else:
    app = None


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the API server."""
    if not FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI not installed. Run: pip install fastapi uvicorn")

    try:
        import uvicorn

        uvicorn.run(app, host=host, port=port)
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("uvicorn not installed. Run: pip install uvicorn") from exc


if __name__ == "__main__":
    start_server()
