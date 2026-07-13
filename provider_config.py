"""
Provider Configuration for DSSAT Integrated Assistant
Navigator API Gateway Integration (University of Florida)
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

# Load environment variables from the single project-root .env file
load_dotenv(Path(__file__).resolve().parent / ".env")

@dataclass
class ProviderConfig:
    """Configuration for LLM provider"""
    provider: str
    api_key: str
    model: str
    base_url: str
    temperature: float = 0.1

# ============================================================================
# Navigator API Configuration (UF's AI Gateway - GPT-5 via API Gateway)
# ============================================================================

_api_key = os.getenv("OPENAI_API_KEY")
if not _api_key:
    raise ValueError(
        "Navigator API key required. Set OPENAI_API_KEY in your .env file "
        "or environment."
    )

NAVIGATOR_CONFIG = ProviderConfig(
    provider="navigator",
    api_key=_api_key,
    model="gpt-5",
    base_url="https://api.ai.it.ufl.edu/v1",
    temperature=0.1
)

# Alias for compatibility
GPT5_CONFIG = NAVIGATOR_CONFIG

# ============================================================================
# Active Configuration
# ============================================================================

def get_active_config() -> ProviderConfig:
    """Get the active provider configuration"""
    return GPT5_CONFIG

def get_api_key() -> str:
    """Get API key for active provider"""
    return GPT5_CONFIG.api_key

def get_model() -> str:
    """Get model name for active provider"""
    return GPT5_CONFIG.model

def get_provider() -> str:
    """Get provider name"""
    return GPT5_CONFIG.provider


# ============================================================================
# Configuration Info
# ============================================================================

def print_config():
    """Print active configuration"""
    config = get_active_config()
    print("🤖 DSSAT Assistant LLM Configuration")
    print("=" * 50)
    print(f"Provider: {config.provider.upper()}")
    print(f"Model: {config.model}")
    print(f"Temperature: {config.temperature}")
    print(f"API Key: {'***' + config.api_key[-8:] if len(config.api_key) > 8 else '***'}")
    print("=" * 50)

if __name__ == "__main__":
    print_config()