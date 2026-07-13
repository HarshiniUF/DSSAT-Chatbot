"""
State Serialization Safety Module

Ensures all data stored in LangGraph state is JSON-serializable.
Converts non-serializable objects (like DSSAT Planting, Fertilizer, etc.) to dictionaries.

This prevents: "Type is not msgpack serializable: Planting" errors
"""

import json
from typing import Any, Dict, List
from datetime import date, datetime


def make_serializable(obj: Any) -> Any:
    """
    Convert any object to a JSON-serializable format.
    
    Handles:
    - DSSAT objects (Planting, Fertilizer, Field, etc.) -> dicts
    - Custom classes -> dicts via __dict__
    - Standard types (dict, list, str, int, float, bool, None) -> pass through
    - Nested structures -> recurse
    
    Args:
        obj: Any object to serialize
        
    Returns:
        JSON-serializable version of the object
    """
    
    # Handle None
    if obj is None:
        return None
    
    # Handle standard JSON types
    if isinstance(obj, (str, int, float, bool)):
        return obj
    
    # Handle lists - recurse on each element
    if isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    
    # Handle dicts - recurse on values
    if isinstance(obj, dict):
        return {str(k): make_serializable(v) for k, v in obj.items()}
    
    # Handle custom objects with __dict__ (includes DSSAT classes)
    if hasattr(obj, '__dict__'):
        try:
            result = {}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):  # Skip private attributes
                    result[str(key)] = make_serializable(value)
            # Add class name for debugging
            result['__class__'] = obj.__class__.__name__
            return result
        except Exception:
            pass
    
    # Handle dataclasses
    if hasattr(obj, '__dataclass_fields__'):
        try:
            result = {}
            for field in obj.__dataclass_fields__:
                value = getattr(obj, field)
                result[field] = make_serializable(value)
            result['__class__'] = obj.__class__.__name__
            return result
        except Exception:
            pass
    
    # Fallback: convert to string
    try:
        return str(obj)
    except Exception:
        return "<non-serializable object>"


def sanitize_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure all values in state dict are JSON-serializable.
    Recursively processes nested structures.
    
    Args:
        state: LangGraph state dictionary
        
    Returns:
        Sanitized state with only serializable values
        
    Example:
        >>> state = {
        ...     "user_question": "What is the best planting date?",
        ...     "proposed_experiment": {...},
        ...     "planting_object": Planting(...)  # Non-serializable!
        ... }
        >>> clean_state = sanitize_state(state)
        >>> # planting_object is now a dict
    """
    
    sanitized = {}
    
    for key, value in state.items():
        try:
            # Try to JSON serialize - this will raise if not serializable
            json.dumps(make_serializable(value), default=str)
            sanitized[key] = make_serializable(value)
        except (TypeError, ValueError) as e:
            # If still not serializable, force convert
            sanitized[key] = make_serializable(value)
    
    return sanitized


def wrap_node_for_safety(node_func):
    """
    Decorator to ensure a LangGraph node always returns serializable state.
    
    Usage:
        @wrap_node_for_safety
        def my_node(state):
            return {...}
    
    Args:
        node_func: LangGraph node function
        
    Returns:
        Wrapped function that sanitizes its output
    """
    
    def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
        # Call original node
        result = node_func(state)
        
        # Sanitize before returning
        if isinstance(result, dict):
            return sanitize_state(result)
        return result
    
    wrapper.__name__ = getattr(node_func, '__name__', 'wrapped_node')
    wrapper.__doc__ = getattr(node_func, '__doc__', '')
    return wrapper


# Pre-made warning message for when non-serializable objects are detected
SERIALIZATION_WARNING = """
⚠️  Non-serializable objects detected in state!
   This usually means a DSSAT object (Planting, Fertilizer, etc.) 
   is being stored directly in the LangGraph state.
   
   Solution: Use sanitize_state() to convert objects to dicts before storing.
   
   Example:
       from agents.state_serializer import sanitize_state
       
       # Before returning from node:
       return sanitize_state({
           **state,
           "proposed_experiment": experiment,
           "other_field": value
       })
"""
