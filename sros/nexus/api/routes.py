"""API Routes.

Public hardened v1 routes are intentionally limited.
The broader API surface is quarantined until fully hardened.
"""

from typing import Dict, Any

try:
    from fastapi import HTTPException
    FASTAPI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    FASTAPI_AVAILABLE = False


API_STATUS = {
    "surface": "quarantined",
    "public_v1": False,
    "reason": "API route layer is experimental and not part of hardened public v1.",
}


def register_routes(app):
    """Register hardened API routes."""
    if not FASTAPI_AVAILABLE:
        return

    @app.get("/api/status")
    def get_status() -> Dict[str, Any]:
        return {
            "status": "quarantined",
            "api": API_STATUS,
        }

    @app.get("/api/capabilities")
    def get_capabilities() -> Dict[str, Any]:
        return {
            "public_endpoints": ["/", "/health", "/api/status", "/api/capabilities"],
            "experimental_endpoints_enabled": False,
        }

    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def reject_quarantined_routes(path: str):
        raise HTTPException(
            status_code=503,
            detail=f"API route '/api/{path}' is quarantined from hardened public v1.",
        )
