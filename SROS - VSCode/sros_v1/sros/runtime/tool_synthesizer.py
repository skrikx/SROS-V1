"""
Tool Synthesizer
================

Dynamic Tool Creation.
Allows the agent to write new Python tools on the fly and register them.
"""
import logging
from typing import Callable, Dict, Any
from sros.models.model_router import chat

logger = logging.getLogger(__name__)

class ToolSynthesizer:
    """
    Synthesizes new tools from descriptions.
    """
    def synthesize(self, tool_name: str, description: str) -> str:
        """
        Generate Python code for a new tool.
        """
        prompt = f"""
        You are a Python Tool Generator.
        
        Tool Name: {tool_name}
        Description: {description}
        
        Task:
        Write a Python function for this tool.
        It must be self-contained (imports inside).
        Return ONLY the code.
        """
        response = chat(prompt, backend="gemini", temperature=0.2)
        code = response.get("text", "")
        return code
