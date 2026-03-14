"""
API Routes

REST API routes for SROS operations.
"""
from typing import Dict, Any, Optional
try:
    from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


if FASTAPI_AVAILABLE:
    # Request models
    class AgentRunRequest(BaseModel):
        agent_name: str
        task: str
    
    class MemoryWriteRequest(BaseModel):
        content: str
        layer: str = "short"
        key: Optional[str] = None

    class SkrikxChatRequest(BaseModel):
        message: str
        context: Optional[Dict[str, Any]] = None

    
    
    def register_routes(app):
        """Register all API routes."""
        
        def get_kernel():
            if not hasattr(app.state, "kernel"):
                raise HTTPException(status_code=503, detail="SROS Kernel not initialized")
            return app.state.kernel

        # Knowledge (Codex)
        @app.get("/api/knowledge/packs")
        def list_knowledge_packs():
            """List all knowledge packs in Codex."""
            kernel = get_kernel()
            if not kernel.memory.codex:
                return {"status": "error", "message": "Codex not initialized"}
                
            packs = kernel.memory.codex.list_packs()
            return {
                "status": "success",
                "count": len(packs),
                "packs": packs
            }

        @app.get("/api/knowledge/search")
        def search_knowledge(query: str):
            """Search knowledge packs."""
            kernel = get_kernel()
            if not kernel.memory.codex:
                return {"status": "error", "message": "Codex not initialized"}
                
            results = kernel.memory.codex.search_packs(query)
            return {
                "status": "success",
                "count": len(results),
                "results": [p.to_dict() for p in results]
            }

        
        # Agents
        @app.get("/api/agents")
        def list_agents():
            """List available agents."""
            return {
                "agents": [
                    {"name": "architect", "role": "System Architect"},
                    {"name": "builder", "role": "Code Builder"},
                    {"name": "tester", "role": "Test Engineer"}
                ]
            }
        
        @app.post("/api/agents/run")
        def run_agent(request: AgentRunRequest):
            """Run an agent with a task."""
            from sros.runtime.agents import ArchitectAgent, BuilderAgent, TesterAgent
            
            try:
                if request.agent_name == "architect":
                    agent = ArchitectAgent()
                elif request.agent_name == "builder":
                    agent = BuilderAgent()
                elif request.agent_name == "tester":
                    agent = TesterAgent()
                else:
                    raise HTTPException(status_code=404, detail=f"Agent not found: {request.agent_name}")
                
                agent.initialize()
                result = agent.act(request.task)
                
                return {
                    "status": "success",
                    "agent": request.agent_name,
                    "result": result
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Skrikx (SROS Prime)
        @app.post("/api/skrikx/chat")
        def skrikx_chat(request: SkrikxChatRequest):
            """Chat with Skrikx (SROS Prime)."""
            kernel = get_kernel()
            
            # Ensure Skrikx agent is available
            # In a real implementation, this might be a singleton or retrieved from a registry
            from sros.runtime.agents.skrikx_agent import SkrikxAgent
            
            try:
                # Initialize agent with kernel context
                agent = SkrikxAgent(kernel_context=kernel)
                
                # Run chat
                response = agent.chat(request.message, request.context)
                
                return {
                    "status": "success",
                    "response": response
                }
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=str(e))
        
        # Memory
        @app.get("/api/memory")
        def read_memory(layer: str = "short", query: Optional[str] = None):
            """Read from memory."""
            kernel = get_kernel()
            
            try:
                results = kernel.memory.read(query=query, layer=layer)
                
                return {
                    "status": "success",
                    "layer": layer,
                    "count": len(results),
                    "results": results
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/memory")
        def write_memory(request: MemoryWriteRequest):
            """Write to memory."""
            kernel = get_kernel()
            
            try:
                kernel.memory.write(request.content, layer=request.layer, key=request.key)
                
                return {
                    "status": "success",
                    "message": "Content written to memory"
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Status
        @app.get("/api/status")
        def get_status():
            """Get system status."""
            kernel = get_kernel()
            running_daemons = kernel.registry.running
            
            return {
                "status": "operational",
                "version": "1.0.0",
                "components": {
                    "kernel": "running",
                    "runtime": "ready",
                    "governance": "active",
                    "mirroros": "observing"
                },
                "daemons": running_daemons
            }
        
        # Adapters
        @app.get("/api/adapters")
        def list_adapters():
            """List available adapters."""
            from sros.adapters.registry import get_registry
            
            registry = get_registry()
            adapters = registry.list_adapters()
            
            return {
                "status": "success",
                "adapters": adapters
            }
        
        # Costs
        @app.get("/api/costs")
        def get_costs():
            """Get cost summary."""
            from sros.governance import CostTracker
            
            tracker = CostTracker()
            budget_status = tracker.check_budget()
            usage_report = tracker.get_usage_report()
            
            return {
                "status": "success",
                "budget": budget_status,
                "usage": usage_report
            }

        # Router
        @app.get("/api/router/tasks")
        def list_routed_tasks(limit: int = 10):
            """List recent routed tasks."""
            # In a real implementation, this would query the TaskRouter's history
            # For now, we return a mock list or empty list
            return {
                "status": "success",
                "tasks": []
            }

        @app.post("/api/router/tasks")
        def submit_routed_task(request: AgentRunRequest):
            """Submit a new task to the router."""
            from sros.models.model_router import chat
            
            # Use the model router to handle the task
            result = chat(request.task)
            
            return {
                "status": "success",
                "task_id": "task_" + request.agent_name, # Mock ID
                "result": result
            }

        # Logs
        @app.get("/api/logs")
        def get_logs(limit: int = 50):
            """Get recent system logs."""
            import os
            
            log_file = "sros_traces.jsonl"
            logs = []
            
            if os.path.exists(log_file):
                try:
                    with open(log_file, "r") as f:
                        lines = f.readlines()
                        # Get last N lines
                        last_lines = lines[-limit:] if len(lines) > limit else lines
                        import json
                        for line in last_lines:
                            try:
                                logs.append(json.loads(line))
                            except:
                                pass
                except Exception:
                    pass
            
            return {
                "status": "success",
                "count": len(logs),
                "logs": logs
            }

        # Kernel
        @app.get("/api/kernel/daemons")
        def get_daemon_status():
            """Get detailed daemon status."""
            return {
                "status": "success",
                "daemons": [
                    {"name": "memory_daemon", "status": "running", "uptime": "1h"},
                    {"name": "agent_router_daemon", "status": "running", "uptime": "1h"},
                    {"name": "scheduler_daemon", "status": "running", "uptime": "1h"},
                    {"name": "telemetry_daemon", "status": "running", "uptime": "1h"},
                    {"name": "security_daemon", "status": "running", "uptime": "1h"}
                ]
            }

        # Evolution
        @app.post("/api/evolution/cycle")
        def trigger_evolution_cycle():
            """Trigger a single evolution cycle."""
            from sros.evolution.ouroboros import OuroborosLoop
            
            try:
                # Initialize loop (in a real scenario, this would be a singleton service)
                loop = OuroborosLoop(config={"enabled": True})
                
                # Run cycle (async in production, sync for now)
                proposals = loop.run_cycle()
                
                return {
                    "status": "success",
                    "message": "Evolution cycle initiated",
                    "proposals_count": len(proposals),
                    "proposals": [p.title for p in proposals]
                }
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {
                    "status": "error",
                    "message": str(e)
                }

        @app.get("/api/evolution/status")
        def get_evolution_status():
            """Get current evolution status."""
            return {
                "status": "success",
                "enabled": True,
                "state": "idle",
                "last_cycle": "never"
            }

    # -------------------------------------------------
    # 📡 WebSocket for "big‑generation" (large responses)
    # -------------------------------------------------
    @app.websocket("/ws/biggen")
    async def ws_biggen(websocket: WebSocket):
        """
        Simple WebSocket that receives a JSON payload:
            { "prompt": "<user prompt>", "backend": "<optional backend>" }
        It runs the ModelRouter chat and streams the final text back.
        """
        await websocket.accept()
        try:
            data = await websocket.receive_json()
            prompt = data.get("prompt", "")
            backend = data.get("backend")
            from sros.models.model_router import chat
            result = chat(prompt, backend=backend, temperature=0.7)
            if result.get("success"):
                await websocket.send_json({"status": "success", "text": result["text"], "backend": result["backend"]})
            else:
                await websocket.send_json({"status": "error", "error": result.get("error", "unknown error")})
        except WebSocketDisconnect:
            pass
        except Exception as exc:
            await websocket.send_json({"status": "error", "error": str(exc)})
            await websocket.close()
else:
    def register_routes(app):
        """Placeholder when FastAPI not available."""
        pass
