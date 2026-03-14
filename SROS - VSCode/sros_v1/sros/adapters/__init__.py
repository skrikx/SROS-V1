"""Adapters package

Registers built-in logical model adapters (gemini/openai/claude).
"""
from .base import AdapterResult, AdapterError
from .registry import get_registry

# Import adapter implementations
from .models.gemini_adapter import GeminiAdapter
from .models.openai_adapter import OpenAIAdapter
from .models.claude_adapter import ClaudeAdapter

# Register adapters with the global registry
_reg = get_registry()
try:
	_reg.register('model', 'gemini', GeminiAdapter)
	_reg.register('model', 'openai', OpenAIAdapter)
	_reg.register('model', 'claude', ClaudeAdapter)
except Exception:
	# Avoid breaking import-time errors in constrained environments
	pass

__all__ = ['AdapterResult', 'AdapterError', 'get_registry', 'GeminiAdapter', 'OpenAIAdapter', 'ClaudeAdapter']
