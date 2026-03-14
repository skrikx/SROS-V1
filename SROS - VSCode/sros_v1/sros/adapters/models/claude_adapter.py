from typing import Any, Dict, Optional, List
import os
import logging

from ..base import ModelAdapter, AdapterResult

logger = logging.getLogger(__name__)


class ClaudeAdapter(ModelAdapter):
    """Logical Claude adapter stub.

    Routes to configured client callable (`config['client']`) if present.
    """

    def initialize(self) -> bool:
        client = self.config.get('client') or os.environ.get('CLAUDE_CLIENT')
        self._has_client = callable(client)
        self._initialized = True
        return True

    def health_check(self) -> bool:
        return getattr(self, '_has_client', False)

    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': 'claude',
            'model': self.config.get('model', os.environ.get('ANTHROPIC_MODEL', 'claude-3.7-sonnet')),
            'has_client': getattr(self, '_has_client', False)
        }

    def generate(self, prompt: str, tools: Optional[List[Dict]] = None, context: Optional[Dict[str, Any]] = None, stream: bool = False, **kwargs) -> AdapterResult:
        client = self.config.get('client')
        request = {
            'backend_id': 'claude',
            'system_prompt': (context or {}).get('system_prompt'),
            'messages': (context or {}).get('messages') or [{'role': 'user', 'content': prompt}],
            'temperature': kwargs.get('temperature', 0.2),
            'max_tokens': kwargs.get('max_tokens', 1024),
            'metadata': kwargs.get('metadata', {})
        }

        if callable(client):
            try:
                resp = client(request)
                return AdapterResult(success=True, data=resp, text=resp.get('output_text', ''), metadata=resp.get('diagnostics', {}))
            except Exception as e:
                logger.exception('Claude client raised')
                return AdapterResult(success=False, data=None, error=str(e))

        return AdapterResult(success=False, data=None, error='No Claude client configured')

    def count_tokens(self, text: str) -> int:
        return len(text.split())

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        return (prompt_tokens + completion_tokens) * 0.000015
