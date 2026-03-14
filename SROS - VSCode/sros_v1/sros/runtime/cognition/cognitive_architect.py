"""
Cognitive Architect
===================

Self-Coding Engine.
Allows the agent to read, analyze, and rewrite its own source code.
"""
import logging
import os
from typing import Dict, Any
from sros.models.model_router import chat

logger = logging.getLogger(__name__)

class CognitiveArchitect:
    """
    Architect of the Self.
    """
    def __init__(self):
        pass

    def analyze_code(self, file_path: str) -> str:
        """Analyze a source file for improvements."""
        if not os.path.exists(file_path):
            return "Error: File not found."
            
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
            
        prompt = f"""
        Analyze this Python code.
        File: {file_path}
        
        Code:
        {code}
        
        Task:
        Identify architectural weaknesses, bugs, or missing features.
        Propose a refactoring plan.
        """
        response = chat(prompt, backend="gemini", temperature=0.3)
        return response.get("text", "Analysis failed.")

    def generate_patch(self, file_path: str, instruction: str) -> str:
        """Generate a code patch."""
        if not os.path.exists(file_path):
            return "Error: File not found."
            
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
            
        prompt = f"""
        You are an Expert Python Architect.
        
        File: {file_path}
        Instruction: {instruction}
        
        Current Code:
        {code}
        
        Task:
        Rewrite the code to satisfy the instruction.
        Return the FULL NEW CODE.
        """
        response = chat(prompt, backend="gemini", temperature=0.2)
        return response.get("text", "Patch generation failed.")
