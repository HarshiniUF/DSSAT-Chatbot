"""
Simple cache manager for agent outputs (UI-friendly).
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List


class SimpleCacheManager:
    """Manages caching of agent outputs to avoid redundant LLM calls"""

    def __init__(self, cache_file: str = "cache.json", use_cache: bool = True):
        self.cache_file = cache_file
        self.use_cache = use_cache
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        if not os.path.exists(self.cache_file):
            return {}
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_cache(self) -> None:
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception:
            # Don't crash pipeline for cache write failures
            return

    def get_cache_key(self, config_path: str, crop_code: str, lat: float, lon: float) -> str:
        filename = os.path.splitext(os.path.basename(config_path))[0]
        return f"{filename}_{crop_code}_{lat}_{lon}"

    def should_run_agent(self, agent_name: str, run_list: List[str]) -> bool:
        """
        True  => run agent fresh
        False => try cache
        """
        if not self.use_cache:
            return True

        if "ALL" in run_list:
            return True

        return agent_name in run_list

    def get_cached_output(self, agent_name: str, cache_key: str) -> Optional[Dict[str, Any]]:
        if not self.use_cache:
            return None
        return self.cache.get(cache_key, {}).get(agent_name)

    def save_agent_output(self, agent_name: str, cache_key: str, data: Dict[str, Any]) -> None:
        if not self.use_cache:
            return

        data = dict(data)
        data["timestamp"] = datetime.now().strftime("%d %B, %Y")

        if cache_key not in self.cache:
            self.cache[cache_key] = {}

        self.cache[cache_key][agent_name] = data
        self._save_cache()

    def clear_agent_cache(self, agent_name: str, cache_key: str) -> None:
        if cache_key in self.cache and agent_name in self.cache[cache_key]:
            del self.cache[cache_key][agent_name]
            self._save_cache()
