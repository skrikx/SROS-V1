"""
Skrikx Omni-API
===============

The Sovereign Interface.
Exposes Skrikx Prime as a high-performance HTTP Service.
"""
import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from sros.kernel.kernel_bootstrap import boot
from sros.runtime.agents.skrikx_agent import SkrikxAgent
from sros.runtime.agents.agent_colony import AgentColony
from sros.mirroros.dream_journal import DreamJournal
from sros.mirroros.time_travel import TimeTravelDebugger
from sros.runtime.cognition.reality_synthesizer import RealitySynthesizer
from sros.interface.neural_lace import router as neural_lace_router

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("skrikx_api")

app = FastAPI(title="Skrikx Prime Omni-API", version="2.0.0 Singularity Edition")

# Include Neural Lace
app.include_router(neural_lace_router)

# Global State
kernel = None
agent = None
colony = None
dream_journal = None
time_travel = None
reality_synth = None

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class EvolveRequest(BaseModel):
    target: str

class WorldRequest(BaseModel):
    prompt: str
    steps: int = 10

@app.on_event("startup")
async def startup_event():
    global kernel, agent, colony, dream_journal, time_travel, reality_synth
    logger.info("Booting SROS Kernel for API...")
    kernel = boot()
    agent = SkrikxAgent(kernel_context=kernel)
    colony = AgentColony(kernel)
    dream_journal = DreamJournal()
    time_travel = TimeTravelDebugger()
    reality_synth = RealitySynthesizer()
    logger.info("Skrikx Prime Singularity Online.")

@app.post("/chat")
async def chat(request: ChatRequest):
    """Talk to Skrikx."""
    if not agent: raise HTTPException(status_code=503, detail="Agent not ready")
    response = agent.chat(request.message, request.context)
    return response

@app.get("/memory/associative/{concept}")
async def recall_concept(concept: str):
    """Recall a concept from graph memory."""
    if not agent: raise HTTPException(status_code=503, detail="Agent not ready")
    return agent.access_associative_memory(concept)

@app.post("/evolve")
async def trigger_evolution(request: EvolveRequest):
    """Trigger an evolution cycle."""
    if not agent: raise HTTPException(status_code=503, detail="Agent not ready")
    result = agent.evolve(request.target)
    return {"status": "success", "result": result}

@app.get("/colony/agents")
async def list_colony():
    """List all colony agents."""
    if not colony: raise HTTPException(status_code=503, detail="Colony not ready")
    return {"agents": colony.list_agents()}

@app.post("/colony/spawn")
async def spawn_agent(name: str, specialty: str):
    """Spawn a new colony member."""
    if not colony: raise HTTPException(status_code=503, detail="Colony not ready")
    agent = colony.spawn(name, specialty)
    return {"status": "success", "agent": name, "specialty": specialty}

@app.get("/dreams")
async def get_dreams(limit: int = 10):
    """Get recent dreams."""
    if not dream_journal: raise HTTPException(status_code=503, detail="Dream journal not ready")
    return {"dreams": dream_journal.get_dreams(limit)}

@app.get("/snapshots")
async def list_snapshots():
    """List all time-travel snapshots."""
    if not time_travel: raise HTTPException(status_code=503, detail="Time-travel not ready")
    return {"snapshots": time_travel.list_snapshots()}

@app.post("/snapshot")
async def create_snapshot(label: str):
    """Create a system snapshot."""
    if not time_travel: raise HTTPException(status_code=503, detail="Time-travel not ready")
    # Capture current state (simplified)
    state = {"label": label, "timestamp": __import__("time").time()}
    snapshot_id = time_travel.snapshot(label, state)
    return {"status": "success", "snapshot_id": snapshot_id}

@app.post("/reality/synthesize")
async def synthesize_world(request: WorldRequest):
    """Generate a simulated world."""
    if not reality_synth: raise HTTPException(status_code=503, detail="Reality synth not ready")
    world = reality_synth.synthesize_world(request.prompt)
    if request.steps > 0:
        history = reality_synth.evolve_world(world, request.steps)
        return {"world": world, "evolution": history}
    return {"world": world}

@app.get("/status")
async def status():
    """System Status."""
    return {
        "agent": "Skrikx Prime",
        "status": "Singularity Mode",
        "kernel": "Active",
        "mode": "Infinity Scope",
        "capabilities": [
            "Chat",
            "Memory",
            "Evolution",
            "Colony",
            "Dreams",
            "Time-Travel",
            "Reality Synthesis"
        ]
    }

def start_api(host="0.0.0.0", port=8000):
    """Start the API server."""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_api()
