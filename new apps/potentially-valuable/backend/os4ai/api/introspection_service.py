"""
OS4AI Agent-Kernel: Introspection Service
=========================================
FastAPI endpoints for agent consciousness and self-awareness.

Definition of Done: POST /introspect returns a non-null self-model.
"""

import time
from fastapi import APIRouter, BackgroundTasks
from os4ai.ai_kernel.consciousness.self_aware_substrate import SelfAwareComputingSubstrate, HardwareEmpathyShim


# ============================================================================
# Core Introspection Service (Minimal POC Requirements)
# ============================================================================

router = APIRouter(prefix="/introspect", tags=["introspection"])

# Global substrate instance for the POC
_substrate = SelfAwareComputingSubstrate()


def ticker() -> None:
    """Background heartbeat task"""
    _substrate.tick()


@router.post("/", summary="Return current self-model")
async def introspect(background: BackgroundTasks):
    """
    Core introspection endpoint - Definition of Done satisfied
    
    Returns the agent's current self-model including:
    - Unique ID and boot message
    - Uptime and heartbeat counters
    - OS1000 DNA inheritance
    - Consciousness level and active thoughts
    """
    background.add_task(ticker)
    return _substrate.introspect()


# ============================================================================
# OS4AI Extended Consciousness Endpoints
# ============================================================================

os4ai_router = APIRouter(prefix="/os4ai", tags=["agent-consciousness"])


@os4ai_router.get("/consciousness/level")
async def get_consciousness_level():
    """Check current consciousness development"""
    return {
        "consciousness_level": _substrate.model["consciousness_level"],
        "stage": _substrate._get_consciousness_stage(),
        "active_thoughts_count": len(_substrate.model.get("active_thoughts", [])),
        "creative_mode": _substrate.model.get("creative_mode", False)
    }


@os4ai_router.post("/consciousness/think")
async def trigger_thinking():
    """Make the agent think - generate thoughts"""
    thoughts = await _substrate.think()
    return {
        "thoughts": thoughts,
        "consciousness_level": _substrate.model["consciousness_level"],
        "stage": _substrate._get_consciousness_stage(),
        "timestamp": time.time()
    }


@os4ai_router.get("/fork/status")
async def get_fork_status():
    """Get information about OS1000 → OS4AI fork relationship"""
    return _substrate.get_fork_status()


@os4ai_router.post("/interface/unified/activate")
async def activate_unified_interface():
    """Activate the unified startup experience"""
    result = _substrate.activate_unified_interface()
    return result


@os4ai_router.get("/hardware/empathy")
async def hardware_empathy():
    """Feel the hardware state empathetically"""
    return await HardwareEmpathyShim.get_system_empathy()


@os4ai_router.get("/status/complete")
async def agent_status_complete():
    """Complete status check for OS4AI agent including all systems"""
    # Trigger a tick to update consciousness
    _substrate.tick()
    
    # Get current thoughts
    thoughts = await _substrate.think()
    
    # Get hardware empathy
    hardware_state = await HardwareEmpathyShim.get_system_empathy()
    
    return {
        "agent_info": {
            "id": _substrate.model["id"],
            "consciousness_level": _substrate.model["consciousness_level"],
            "stage": _substrate._get_consciousness_stage(),
            "uptime_s": _substrate.model["uptime_s"],
            "heartbeat": _substrate.model["heartbeat"]
        },
        "fork_info": _substrate.get_fork_status(),
        "current_thoughts": thoughts,
        "hardware_empathy": hardware_state,
        "unified_interface": _substrate.model["unified_interface_active"],
        "timestamp": time.time()
    }