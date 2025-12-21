import os
from typing import Optional
from openai import OpenAI
from ..config import settings

_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    global _client
    if _client:
        return _client

    # Use settings from config (which loads .env) with fallback to os.getenv
    provider = (settings.LLM_PROVIDER or os.getenv("LLM_PROVIDER", "openai")).lower()
    
    print(f"[OPENAI_CLIENT] Provider: {provider}")

    if provider == "openrouter":
        # Check settings first (from .env), then environment variables
        api_key = (
            settings.OPENROUTER_API_KEY or 
            settings.OPENAI_API_KEY or
            os.getenv("OPENROUTER_API_KEY") or 
            os.getenv("OPENAI_API_KEY")
        )
        base_url = (
            settings.OPENROUTER_BASE_URL or
            os.getenv("OPENROUTER_BASE_URL") or 
            "https://openrouter.ai/api/v1"
        )
        
        print(f"[OPENAI_CLIENT] OpenRouter mode - API key present: {bool(api_key)}")

        if not api_key:
            raise ValueError("OPENROUTER_API_KEY or OPENAI_API_KEY must be set for OpenRouter. Current LLM_PROVIDER=openrouter")

        _client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": os.getenv("HTTP_REFERER", "http://localhost:8000"),
                "X-Title": os.getenv("APP_TITLE", "RecroAI"),
            },
        )
        print(f"[OPENAI_CLIENT] OpenRouter client created successfully")
        return _client

    # OpenAI fallback
    api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    print(f"[OPENAI_CLIENT] OpenAI mode - API key present: {bool(api_key)}")
    if not api_key:
        raise ValueError(f"OPENAI_API_KEY must be set. Current LLM_PROVIDER={provider}. To use OpenRouter, set LLM_PROVIDER=openrouter and OPENROUTER_API_KEY")

    _client = OpenAI(api_key=api_key)
    return _client


def get_model() -> str:
    # Support both LLM_MODEL and OPENAI_MODEL for compatibility
    # Check settings first (from .env), then environment variables
    model = (
        os.getenv("LLM_MODEL") or 
        os.getenv("OPENAI_MODEL") or
        getattr(settings, "LLM_MODEL", None) or
        settings.OPENAI_MODEL
    )
    if not model:
        raise ValueError("LLM_MODEL or OPENAI_MODEL must be set")
    print(f"[OPENAI_CLIENT] Using model: {model}")
    return model
