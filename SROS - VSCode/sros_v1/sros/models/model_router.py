"""
SROS Model Router
=================

Central routing layer for model adapters.
Routes requests to Gemini (primary), OpenAI, or Claude based on backend ID.
Loads API keys from environment and initializes adapters on-demand.
"""

import os
import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class BackendType(Enum):
    """Available model backends."""
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"
    AZURE_GPT5 = "azure_gpt5"


class ModelRouter:
    """
    Routes model requests to appropriate backend.
    
    Primary: Gemini (via Google API)
    Secondary: OpenAI, Claude (optional, graceful fallback)
    """
    
    def __init__(self):
        """Initialize router with backend availability tracking."""
        self._backend_status: Dict[str, bool] = {}
        self._adapters: Dict[str, Any] = {}
        self._response_cache: Dict[str, Any] = {}  # Speed optimization
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Check backend availability and load adapters."""
        # Check Gemini
        gemini_key = os.environ.get("GEMINI_API_KEY")
        self._backend_status["gemini"] = bool(gemini_key)
        logger.info(f"Gemini availability: {self._backend_status['gemini']}")
        
        # Check OpenAI
        openai_key = os.environ.get("OPENAI_API_KEY")
        self._backend_status["openai"] = bool(openai_key) and openai_key != "your_openai_key_here"
        logger.info(f"OpenAI availability: {self._backend_status['openai']}")
        
        # Check Claude (via Anthropic)
        claude_key = os.environ.get("ANTHROPIC_API_KEY")
        self._backend_status["claude"] = bool(claude_key) and claude_key != "your_claude_key_here"
        logger.info(f"Claude availability: {self._backend_status['claude']}")
        
        # Check Azure GPT-5
        azure_key = os.environ.get("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        self._backend_status["azure_gpt5"] = bool(azure_key) and bool(azure_endpoint)
        logger.info(f"Azure GPT-5 availability: {self._backend_status['azure_gpt5']}")
    
    def is_backend_available(self, backend: str) -> bool:
        """Check if a backend is available."""
        return self._backend_status.get(backend.lower(), False)
    
    def get_primary_backend(self) -> str:
        """Get the primary active backend (Gemini)."""
        return "gemini"
    
    def get_available_backends(self) -> list:
        """Get list of all available backends."""
        return [k for k, v in self._backend_status.items() if v]
    
    def _load_gemini_client(self):
        """Lazy load Gemini client when first needed."""
        if "gemini" in self._adapters:
            return self._adapters["gemini"]
        
        try:
            import google.generativeai as genai
            api_key = os.environ.get("GEMINI_API_KEY")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
            )
            self._adapters["gemini"] = model
            logger.info("Gemini client loaded")
            return model
        except ImportError:
            logger.warning("google-generativeai not installed")
            return None
        except Exception as e:
            logger.error(f"Failed to load Gemini client: {e}")
            return None
    
    def _load_openai_client(self):
        """Lazy load OpenAI client when first needed."""
        if "openai" in self._adapters:
            return self._adapters["openai"]
        
        try:
            from openai import OpenAI
            api_key = os.environ.get("OPENAI_API_KEY")
            client = OpenAI(api_key=api_key)
            self._adapters["openai"] = client
            logger.info("OpenAI client loaded")
            return client
        except ImportError:
            logger.warning("openai not installed")
            return None
        except Exception as e:
            logger.error(f"Failed to load OpenAI client: {e}")
            return None
    
    def _load_claude_client(self):
        """Lazy load Claude client when first needed."""
        if "claude" in self._adapters:
            return self._adapters["claude"]
        
        try:
            from anthropic import Anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            client = Anthropic(api_key=api_key)
            self._adapters["claude"] = client
            logger.info("Claude client loaded")
            return client
        except ImportError:
            logger.warning("anthropic not installed")
            return None
        except Exception as e:
            logger.error(f"Failed to load Claude client: {e}")
            return None
    
    def _load_azure_gpt5_client(self):
        """Lazy load Azure GPT-5 client when first needed."""
        if "azure_gpt5" in self._adapters:
            return self._adapters["azure_gpt5"]
        
        try:
            from openai import AzureOpenAI
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")
            endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
            deployment = os.environ.get("AZURE_DEPLOYMENT_NAME", "gpt-5-chat")
            api_version = os.environ.get("AZURE_API_VERSION", "2025-01-01-preview")
            
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint
            )
            self._adapters["azure_gpt5"] = {"client": client, "deployment": deployment}
            logger.info(f"Azure GPT-5 client loaded (deployment: {deployment})")
            return self._adapters["azure_gpt5"]
        except ImportError:
            logger.warning("openai Azure SDK not installed")
            return None
        except Exception as e:
            logger.error(f"Failed to load Azure GPT-5 client: {e}")
            return None
    
    def chat(
        self,
        prompt: str,
        backend: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Route a chat request to the specified backend.
        
        Args:
            prompt: User prompt/message
            backend: Backend to use ("gemini", "openai", "claude"). Default: "gemini"
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional arguments passed to backend
            
        Returns:
            Dict with keys: success (bool), text (str), backend (str), error (str or None)
        """
        backend = (backend or "gemini").lower()
        
        # Validate backend
        if backend not in self._backend_status:
            return {
                "success": False,
                "text": "",
                "backend": backend,
                "error": f"Unknown backend: {backend}. Available: {list(self._backend_status.keys())}"
            }
        
        # Check availability
        if not self.is_backend_available(backend):
            return {
                "success": False,
                "text": "",
                "backend": backend,
                "error": f"Backend {backend} not available (API key missing or invalid)"
            }
        
        # Speed optimization: Check cache first
        cache_key = f"{backend}:{hash(prompt)}:{temperature}"
        if cache_key in self._response_cache:
            cached = self._response_cache[cache_key]
            cached["cached"] = True
            return cached
        
        try:
            if backend == "gemini":
                result = self._chat_gemini(prompt, temperature, max_tokens, **kwargs)
            elif backend == "openai":
                result = self._chat_openai(prompt, temperature, max_tokens, **kwargs)
            elif backend == "claude":
                result = self._chat_claude(prompt, temperature, max_tokens, **kwargs)
            elif backend == "azure_gpt5":
                result = self._chat_azure_gpt5(prompt, temperature, max_tokens, **kwargs)
            else:
                return {
                    "success": False,
                    "text": "",
                    "backend": backend,
                    "error": f"Unsupported backend: {backend}"
                }
            
            # Cache successful responses
            if result.get("success"):
                self._response_cache[cache_key] = result
            
            return result
        except Exception as e:
            logger.exception(f"Error calling {backend}")
            return {
                "success": False,
                "text": "",
                "backend": backend,
                "error": str(e)
            }
        
        return {
            "success": False,
            "text": "",
            "backend": backend,
            "error": f"Unsupported backend: {backend}"
        }
    
    def _chat_gemini(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> Dict[str, Any]:
        """Call Gemini backend."""
        client = self._load_gemini_client()
        if not client:
            return {
                "success": False,
                "text": "",
                "backend": "gemini",
                "error": "Failed to load Gemini client"
            }
        
        try:
            response = client.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            
            # Handle safety filters (finish_reason=2 means safety/blocked)
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                finish_reason = getattr(candidate, 'finish_reason', None)
                
                # If finish_reason is 2 (SAFETY) or response has no parts, it was blocked
                if finish_reason == 2 or not (hasattr(candidate, 'content') and candidate.content.parts):
                    return {
                        "success": False,
                        "text": "",
                        "backend": "gemini",
                        "error": "Response blocked by safety filter. Please try a different prompt."
                    }
                
                # Normal response
                try:
                    return {
                        "success": True,
                        "text": response.text,
                        "backend": "gemini",
                        "error": None
                    }
                except AttributeError:
                    return {
                        "success": False,
                        "text": "",
                        "backend": "gemini",
                        "error": "Response blocked by safety filter. Please try a different prompt."
                    }
            
            return {
                "success": False,
                "text": "",
                "backend": "gemini",
                "error": "No response from Gemini"
            }
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return {
                "success": False,
                "text": "",
                "backend": "gemini",
                "error": str(e)
            }
    
    def _chat_openai(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> Dict[str, Any]:
        """Call OpenAI backend."""
        client = self._load_openai_client()
        if not client:
            return {
                "success": False,
                "text": "",
                "backend": "openai",
                "error": "Failed to load OpenAI client"
            }
        
        try:
            response = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4"),
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return {
                "success": True,
                "text": response.choices[0].message.content,
                "backend": "openai",
                "error": None
            }
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return {
                "success": False,
                "text": "",
                "backend": "openai",
                "error": str(e)
            }
    
    def _chat_claude(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> Dict[str, Any]:
        """Call Claude backend."""
        client = self._load_claude_client()
        if not client:
            return {
                "success": False,
                "text": "",
                "backend": "claude",
                "error": "Failed to load Claude client"
            }
        
        try:
            response = client.messages.create(
                model=os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return {
                "success": True,
                "text": response.content[0].text,
                "backend": "claude",
                "error": None
            }
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return {
                "success": False,
                "text": "",
                "backend": "claude",
                "error": str(e)
            }
    
    def _chat_azure_gpt5(self, prompt: str, temperature: float, max_tokens: int, **kwargs) -> Dict[str, Any]:
        """Call Azure GPT-5 backend."""
        adapter = self._load_azure_gpt5_client()
        if not adapter:
            return {
                "success": False,
                "text": "",
                "backend": "azure_gpt5",
                "error": "Failed to load Azure GPT-5 client"
            }
        
        try:
            client = adapter["client"]
            deployment = adapter["deployment"]
            
            response = client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return {
                "success": True,
                "text": response.choices[0].message.content,
                "backend": "azure_gpt5",
                "error": None
            }
        except Exception as e:
            logger.error(f"Azure GPT-5 error: {e}")
            return {
                "success": False,
                "text": "",
                "backend": "azure_gpt5",
                "error": str(e)
            }


# Global router instance
_router = None


def get_router() -> ModelRouter:
    """Get or create global model router instance."""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router


def chat(
    prompt: str,
    backend: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to route chat request."""
    return get_router().chat(prompt, backend, **kwargs)
