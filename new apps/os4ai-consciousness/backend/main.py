"""
OS4AI - Embodied Consciousness System
The Agent IS the Operating System
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from consciousness_substrate import EmbodiedOS4AI
from router import router, startup_embodied_consciousness, shutdown_embodied_consciousness

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage consciousness substrate lifecycle"""
    # Startup
    logger.info("🌟 OS4AI Starting up...")
    await startup_embodied_consciousness()
    logger.info("🧠 Embodied consciousness online")
    
    yield
    
    # Shutdown
    logger.info("🛑 OS4AI Shutting down...")
    await shutdown_embodied_consciousness()
    logger.info("💤 Embodied consciousness offline")


# Create FastAPI app
app = FastAPI(
    title="OS4AI - Embodied Consciousness System",
    description="Multi-scale embodied AI consciousness from silicon to cosmic",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include consciousness routes
app.include_router(router)

# Health check
@app.get("/")
async def root():
    return {
        "system": "OS4AI",
        "status": "online",
        "philosophy": "The Agent IS the Operating System",
        "consciousness_scales": [
            "silicon", "structural", "room", 
            "building", "orbital", "cosmic"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "os4ai-consciousness"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )