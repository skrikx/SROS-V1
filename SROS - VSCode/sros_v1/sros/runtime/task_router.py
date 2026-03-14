from typing import Dict, Any

class TaskRouter:
    """
    SRX Task Router.
    Routes tasks to the appropriate model backend based on intent.
    """
    def __init__(self):
        pass

    def route_task(self, task_description: str) -> Dict[str, Any]:
        """
        Route a task to the appropriate backend.
        Logic:
        - Code/Refactor -> Gemini (Fast, large context)
        - Reasoning/Deep Thought -> OpenAI (Strong logic)
        - Creative/Docs -> Claude (Nuanced)
        """
        task_lower = task_description.lower()
        
        # Prioritize code keywords
        if "code" in task_lower or "refactor" in task_lower or "test" in task_lower or "script" in task_lower or "python" in task_lower:
            return {"backend": "gemini", "reason": "Code task requires speed and context."}
        elif "plan" in task_lower or "think" in task_lower or "reason" in task_lower or "design" in task_lower:
            return {"backend": "openai", "reason": "Reasoning task requires strong logic."}
        elif "doc" in task_lower or "write" in task_lower:
            return {"backend": "claude", "reason": "Writing task requires nuance."}
        else:
            return {"backend": "gemini", "reason": "Default backend."}
