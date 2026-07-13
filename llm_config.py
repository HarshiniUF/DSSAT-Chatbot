"""
LLM Configuration - Navigator API (UF's AI Gateway)
Simplified configuration for unified GPT-5 usage via Navigator API
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from the single project-root .env file
load_dotenv(Path(__file__).resolve().parent / ".env")

class LLMConfig:
    """Configuration manager for Navigator API GPT-5"""
    
    DEFAULT_MODEL = "gpt-5"
    DEFAULT_BASE_URL = "https://api.ai.it.ufl.edu/v1"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize LLM configuration for Navigator API
        
        Args:
            api_key: Navigator API key
            model: Model name (defaults to gpt-5)
            base_url: Navigator API base URL
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or self.DEFAULT_MODEL
        self.base_url = base_url or self.DEFAULT_BASE_URL
        
        if not self.api_key:
            raise ValueError("Navigator API key required. Set OPENAI_API_KEY environment variable.")
    
    def create_llm(self, temperature: float = 0.1, **kwargs):
        """
        Create ChatOpenAI LLM instance with Navigator API
        
        Args:
            temperature: Model temperature
            **kwargs: Additional parameters
        """
        from langchain_openai import ChatOpenAI
        
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            temperature=temperature,
            **kwargs
        )
    
    def get_info(self) -> Dict[str, str]:
        """Get configuration information"""
        return {
            "provider": "navigator",
            "model": self.model,
            "base_url": self.base_url,
            "api_key_set": "***" if self.api_key else "Not Set"
        }

# ============================================================================
# Convenience Functions
# ============================================================================

def create_navigator_llm(api_key: Optional[str] = None, temperature: float = 0.1):
    """Create Navigator API LLM instance"""
    config = LLMConfig(api_key=api_key)
    return config.create_llm(temperature=temperature)

def get_llm(mode: str = "api", temperature: float = 0.1):
    """
    Get LLM instance (Navigator API GPT-5)
    
    Args:
        mode: Ignored (kept for backward compatibility)
        temperature: Model temperature
    """
    return create_navigator_llm(temperature=temperature)

# ============================================================================
# Direct Navigator API Wrapper (for multiagent compatibility)
# ============================================================================

class ChatGPTLLM:
    """Direct Navigator API wrapper for compatibility"""
    
    def __init__(self, model="gpt-5", temperature=0, api_key: Optional[str] = None, base_url: str = "https://api.ai.it.ufl.edu/v1"):
        self.model = model
        self.temperature = temperature
        self.base_url = base_url
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")

    def invoke(self, prompt: str) -> str:
        """Call Navigator API directly"""
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            base_url=self.base_url,
            temperature=self.temperature
        )
        
        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()

if __name__ == "__main__":
    # Test configuration
    config = LLMConfig()
    print("✓ LLM Configuration:")
    print(f"  Model: {config.model}")
    print(f"  API Key: {'Set' if config.api_key else 'Not Set'}")