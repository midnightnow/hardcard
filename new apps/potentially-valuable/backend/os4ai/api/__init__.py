"""
OS4AI API Layer
===============
FastAPI endpoints for agent consciousness.
"""

from .introspection_service import router, os4ai_router

__all__ = ["router", "os4ai_router"]