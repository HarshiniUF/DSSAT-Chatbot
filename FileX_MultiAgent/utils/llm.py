"""
LLM wrapper utilities (supports model switching from Streamlit UI).
Uses University of Florida NaviGator API with Client-ID / Client-Secret headers.
"""

from __future__ import annotations

import os
import openai
from langchain_ollama import OllamaLLM
import streamlit as st


# ── Credential helpers ────────────────────────────────────────────────────────

def _get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key
    try:
        key = st.secrets.get("OPENAI_API_KEY")
        if key:
            return str(key)
    except Exception:
        pass
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Set it in .env or .streamlit/secrets.toml"
    )


def _get_base_url() -> str:
    url = os.getenv("OPENAI_BASE_URL")
    if url:
        return url
    try:
        url = st.secrets.get("OPENAI_BASE_URL")
        if url:
            return str(url)
    except Exception:
        pass
    return "https://api.ai.it.ufl.edu/v1"


def _get_navigator_headers() -> dict:
    """Return Client-ID and Client-Secret headers required by the NaviGator API."""
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    if not client_id or not client_secret:
        try:
            client_id = client_id or st.secrets.get("CLIENT_ID", "")
            client_secret = client_secret or st.secrets.get("CLIENT_SECRET", "")
        except Exception:
            pass
    return {
        "Client-ID": client_id or "",
        "Client-Secret": client_secret or "",
    }


def _get_base_public() -> str:
    return "https://api.openai.com/v1"


def _get_api_key_public() -> str:
    try:
        return st.secrets.get("OPENAI_API_KEY_PUBLIC", "")
    except Exception:
        return ""


# ── LLM class ─────────────────────────────────────────────────────────────────

class ChatGPTLLM:
    def __init__(self, model: str = "gpt-5", temperature: float = 0, use_public: bool = False):
        self.model = model
        self.temperature = temperature

        if use_public:
            self.client = openai.OpenAI(
                api_key=_get_api_key_public(),
                base_url=_get_base_public(),
            )
        else:
            self.client = openai.OpenAI(
                api_key=_get_api_key(),
                base_url=_get_base_url(),
                default_headers=_get_navigator_headers(),
            )

    def invoke(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        return response.choices[0].message.content.strip()


# ── Factory functions ──────────────────────────────────────────────────────────

def get_llm(mode: str = "local", model: str = "gpt-5", temperature: float = 0, use_public: bool = False):
    print("getting get_llm.......")
    if mode == "local":
        return OllamaLLM(model="llama3.1:8b", temperature=temperature)
    return ChatGPTLLM(model=model, temperature=temperature, use_public=use_public)


def get_judge_llm(model: str = "gpt-5", temperature: float = 0):
    return ChatGPTLLM(model=model, temperature=temperature)
