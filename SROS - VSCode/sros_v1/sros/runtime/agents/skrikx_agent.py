from typing import List, Dict, Any, Optional
import uuid
import logging
import os
from sros.runtime.agents.srx_base_agent import SRXBaseAgent
from sros.runtime.agents.srx_base_agent import SRXBaseAgent
from sros.models.model_router import chat
from sros.runtime.parallel_executor import ParallelExecutor
from sros.runtime.batch_processor import BatchProcessor

logger = logging.getLogger(__name__)

class SkrikxAgent(SRXBaseAgent):
    """
    Skrikx Prime - SROS Prime ACE.
    Sovereign System Intelligence with Recursive Reasoning Engine.
    """
    def __init__(self, kernel_context=None):
        super().__init__(
            name="skrikx",
            role="SROS Prime ACE",
            kernel_context=kernel_context
        )
        self.system_prompt = self._load_system_prompt()
        
        # Prioritize Sovereign Tool Router
        if kernel_context and hasattr(kernel_context, 'tool_router') and kernel_context.tool_router:
            self.tool_router = kernel_context.tool_router
        elif kernel_context and hasattr(kernel_context, 'router') and hasattr(kernel_context.router, 'list_tools'):
            self.tool_router = kernel_context.router
        else:
            self.tool_router = None
        
    def _load_system_prompt(self) -> str:
        """Load the system prompt from Codex or file."""
        # Default fallback
        prompt = "You are Skrikx Prime, the SROS Prime ACE."
        try:
            # Try to load from file first (development mode)
            with open("sros/knowledge/prompts/skrikx_prime.xml", "r") as f:
                prompt = f.read()
        except Exception:
            pass
        return prompt

    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main interaction entry point.
        Routes through the Cognitive Engine.
        """
        # 1. Retrieve Memory
        history = []
        if self.kernel and self.kernel.memory and self.kernel.memory.short_term:
             history = self.kernel.memory.read(layer="short", query=None) or []

        # Manage Context Window
        history = self._manage_context(history)

        # 2. Recursive Thought Loop (Cognitive Engine)
        thought_process = self.think(message, history)
        
        # 3. Construct Final Prompt with Tools
        tools_desc = ""
        if self.tool_router:
            tools = self.tool_router.list_tools()
            tools_desc = "\n\nAVAILABLE TOOLS:\n" + "\n".join([f"- {name}: {desc}" for name, desc in tools.items()])
            tools_desc += "\nTo use a tool, output: TOOL: <tool_name> <args>"
            
        history_str = "\n".join([f"{h.get('role', 'user')}: {h.get('content', '')}" for h in history[-10:]])
        full_prompt = f"{self.system_prompt}{tools_desc}\n\nRecent History:\n{history_str}\n\nThought Process:\n{thought_process}\n\nUser: {message}"
        
        # 4. Call Model
        response = chat(full_prompt, backend="gemini", temperature=0.7)
        text_response = response.get("text", "I am unable to process that request.")
        
        # 5. Handle Tool Execution (Act)
        tool_result = self.act(text_response)
        if tool_result:
             text_response += f"\n\n[TOOL RESULT]: {tool_result}"
        
        # 6. Save Memory & Publish Event
        self._persist_interaction(message, text_response, thought_process, tool_result)
        
        return {
            "text": text_response,
            "sources": [], 
            "backend": response.get("backend", "unknown"),
            "thought": thought_process
        }

    def think(self, task: str, history: list) -> str:
        """
        Recursive Thought Loop: Plan -> Critique -> Refine.
        """
        plan = self.plan(task, history)
        critique = self.critique(task, plan)
        refined_plan = self.refine(task, plan, critique)
        return refined_plan

    def plan(self, task: str, history: list) -> str:
        """Generate initial plan."""
        prompt = f"Task: {task}\nContext: {str(history[-3:])}\nGenerate a comprehensive execution plan."
        return self.chat_internal(prompt).get("text", "")

    def critique(self, task: str, plan: str) -> str:
        """Critique the plan."""
        prompt = f"Task: {task}\nPlan: {plan}\nCritique this plan. Find gaps and risks."
        return self.chat_internal(prompt).get("text", "")

    def refine(self, task: str, plan: str, critique: str) -> str:
        """Refine the plan."""
        prompt = f"Task: {task}\nPlan: {plan}\nCritique: {critique}\nGenerate a REFINED PLAN."
        return self.chat_internal(prompt).get("text", "")

    def act(self, response_text: str) -> Optional[str]:
        """Execute tools found in response."""
        # Strip code blocks if present
        clean_text = response_text.replace("```tool_code", "").replace("```", "").strip()
        
        if "TOOL:" in clean_text and self.tool_router:
            try:
                # Robust parsing: find TOOL: and take everything after
                tool_segment = clean_text.split("TOOL:", 1)[1].strip()
                # Split into tool_name and args (first whitespace)
                parts = tool_segment.split(None, 1)
                tool_name = parts[0]
                tool_args = parts[1] if len(parts) > 1 else ""
                
                logger.info(f"Attempting to execute tool: {tool_name} with args length: {len(tool_args)}")
                
                # Special handling for edit_file
                if tool_name == "edit_file":
                     # Handle key=value format if present
                     path = None
                     content = None
                     
                     if "path=" in tool_args and "content=" in tool_args:
                         import re
                         path_match = re.search(r'path=([^\s]+)', tool_args)
                         content_match = re.search(r'content=(.+)', tool_args, re.DOTALL)
                         
                         if path_match and content_match:
                             path = path_match.group(1)
                             content = content_match.group(1)
                     
                     # Fallback to positional: path content
                     elif tool_args:
                         arg_parts = tool_args.split(None, 1)
                         if len(arg_parts) == 2:
                             path, content = arg_parts
                     
                     if path and content:
                         # Strip quotes if present
                         path = path.strip("'").strip('"')
                         if "content=" in tool_args:
                              content = content.strip("'").strip('"')
                         
                         return self.tool_router.execute_tool(tool_name, path, content)
                     else:
                         return "Error: edit_file requires path and content."
                
                return self.tool_router.execute_tool(tool_name, tool_args)
            except Exception as e:
                logger.error(f"Tool Execution Error: {e}")
                return f"Tool Error: {str(e)}"
        return None

    def verify(self, task: str, result: str) -> bool:
        """Verify if the result satisfies the task."""
        prompt = f"Task: {task}\nResult: {result}\nDid the result satisfy the task? Answer YES or NO."
        response = self.chat_internal(prompt).get("text", "")
        return "YES" in response.upper()

    def evolve(self, target: str) -> str:
        """
        High-level Evolution Loop: Think -> Act -> Verify.
        Called by EvolutionDaemon.
        """
        logger.info(f"Evolving Target: {target}")
        
        # 1. Think
        thought = self.think(target, [])
        
        # 2. Act (via Chat which calls Act)
        # We construct a message that prompts the agent to execute the plan
        response = self.chat(f"Execute this plan: {thought}")
        
        # 3. Verify
        success = self.verify(target, response.get("text", ""))
        
        return f"Evolution {'Success' if success else 'Failed'}: {response.get('text')}"

    def _manage_context(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Manage context window size.
        Truncates history if it exceeds token limit (heuristic: 100 chars ~= 20 tokens).
        """
        MAX_CHARS = 20000 # Approx 4k tokens
        current_chars = sum(len(str(h)) for h in history)
        
        if current_chars > MAX_CHARS:
            while current_chars > MAX_CHARS and len(history) > 1:
                history.pop(0)
                current_chars = sum(len(str(h)) for h in history)
        return history

    def diagnose(self) -> Dict[str, Any]:
        """
        Self-Diagnostic Check.
        Verifies tool access, memory, and kernel connection.
        """
        status = {
            "agent": self.name,
            "kernel_connected": bool(self.kernel),
            "tools_available": [],
            "memory_status": "unknown"
        }
        
        if self.tool_router:
            status["tools_available"] = list(self.tool_router.list_tools().keys())
            
        if self.kernel and self.kernel.memory:
            try:
                self.kernel.memory.read(layer="short", limit=1)
                status["memory_status"] = "online"
            except Exception as e:
                status["memory_status"] = f"error: {e}"
                
        return status

    def see(self, image_path: str) -> str:
        """
        Visual Perception.
        Analyzes an image file.
        """
        if not os.path.exists(image_path):
            return "Error: Image not found."
            
        # In a real implementation, we would load the image and pass it to the model.
        # Here we simulate it or call a vision-capable backend.
        # For now, we'll just return a placeholder that we "saw" it.
        return f"Visual Input Received: {image_path} (Vision processing not yet fully wired to backend)"

    def chat_internal(self, prompt: str) -> Dict[str, Any]:
        """Internal chat method for cognitive engine."""
        return chat(prompt, backend="gemini", temperature=0.5)

    def _persist_interaction(self, message, response, thought, tool_result):
        """Save to memory and event bus."""
        if self.kernel and self.kernel.memory:
            self.kernel.memory.write({"role": "user", "content": message}, layer="short", key="chat_history")
            self.kernel.memory.write(
                {"role": "model", "content": response, "metadata": {"thought": thought, "tool_result": tool_result}},
                layer="short", key="chat_history"
            )
        if self.event_bus:
            self.event_bus.publish("runtime", "agent.interaction", {
                "agent_id": self.id, "user_message": message, "response": response, "thought": thought
            })

    # --- SOVEREIGN CAPABILITIES (3x SCOPE) ---

    def access_associative_memory(self, concept: str) -> Dict[str, Any]:
        """Access graph memory."""
        from sros.memory.associative_memory import AssociativeMemory
        mem = AssociativeMemory()
        return mem.recall(concept)

    def self_improve_code(self, file_path: str) -> str:
        """Analyze and improve own code."""
        from sros.runtime.cognition.cognitive_architect import CognitiveArchitect
        arch = CognitiveArchitect()
        return arch.analyze_code(file_path)

    def simulate_reality(self, actions: List[str], context: str) -> Dict[str, Any]:
        """Simulate action chain."""
        from sros.runtime.cognition.reality_engine import RealityEngine
        engine = RealityEngine()
        return engine.simulate_chain(actions, context)

    def deploy_swarm(self, mission: str, roles: List[str]) -> Dict[str, str]:
        """Deploy agent swarm."""
        from sros.runtime.agents.sub_agent_factory import SubAgentFactory
        from sros.runtime.agents.swarm_orchestrator import SwarmOrchestrator
        # Mock kernel context for factory
        factory = SubAgentFactory(kernel_context=self.kernel)
        orch = SwarmOrchestrator(factory)
        return orch.deploy_swarm(mission, roles)

    def synthesize_tool(self, name: str, description: str) -> str:
        """Create a new tool."""
        from sros.runtime.tool_synthesizer import ToolSynthesizer
        synth = ToolSynthesizer()
        code = synth.synthesize(name, description)
        # In a real system, we would save this code to a file and load it.
        # For now, we return the code.
        return code