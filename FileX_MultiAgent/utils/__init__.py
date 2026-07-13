"""
Utility modules
"""

# DSSATState depends on DSSATTools (requires pandas, rosetta-soil, etc.).
# Wrapped in try/except so standalone scripts like generate_dataset.py
# can import utils.llm and utils.helpers cleanly without the full DSSAT stack.
try:
    from .state import DSSATState
    _DSSAT_STATE_AVAILABLE = True
except ImportError:
    _DSSAT_STATE_AVAILABLE = False

from .llm import get_llm, get_judge_llm, ChatGPTLLM
from .helpers import (
    convert_date_to_dssat_date,
    parse_codebook_section,
    make_code_options_text,
    strip_markdown_fences,
    get_crop_name,
)
from .cache_manager import SimpleCacheManager


__all__ = [
    'DSSATState',
    'get_llm',
    'get_judge_llm',
    'ChatGPTLLM',
    'convert_date_to_dssat_date',
    'parse_codebook_section',
    'make_code_options_text',
    'strip_markdown_fences',
    'get_crop_name',
    'SimpleCacheManager',
]
