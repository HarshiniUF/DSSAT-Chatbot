"""
Date integration module for DSSAT experiment agents.
Integrates current date logic from sim_config.py to ensure experiments use appropriate dates.
"""

from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add parent directory to path for sim_config import
sys.path.append(str(Path(__file__).parent.parent))

try:
    from sim_config import SimulationConfig
except ImportError:
    SimulationConfig = None
    

def get_current_date() -> date:
    """Get current date using SimulationConfig if available, otherwise system date."""
    if SimulationConfig:
        config = SimulationConfig()
        return config.current_date
    else:
        return date.today()


def get_simulation_window() -> Dict[str, Any]:
    """Get simulation window (current date + simulation years)."""
    if SimulationConfig:
        config = SimulationConfig()
        return {
            "start_date": config.current_date,
            "simulation_years": config.simulation_years,
            "end_date": date(config.current_date.year + config.simulation_years, 12, 31)
        }
    else:
        current = date.today()
        return {
            "start_date": current,
            "simulation_years": 2,
            "end_date": date(current.year + 2, 12, 31)
        }


def ensure_future_date(target_date: str, offset_days: int = 0) -> str:
    """
    Ensure the given date is in the future (at least current date + offset).
    If the date is in the past, adjust it to the current/next appropriate season.
    
    Args:
        target_date: Date string in YYYY-MM-DD format
        offset_days: Minimum days from current date (default: 0)
        
    Returns:
        Adjusted date string in YYYY-MM-DD format
    """
    try:
        parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        current = get_current_date()
        min_date = current + timedelta(days=offset_days)
        
        if parsed_date >= min_date:
            return target_date  # Date is already in the future
            
        # Date is in the past, adjust to current/next year
        # Preserve month/day but use current or next year
        target_month = parsed_date.month
        target_day = parsed_date.day
        
        # Try current year first
        try:
            candidate = date(current.year, target_month, target_day)
            if candidate >= min_date:
                return candidate.strftime("%Y-%m-%d")
        except ValueError:
            # Handle leap year issues (Feb 29)
            pass
            
        # Use next year
        try:
            candidate = date(current.year + 1, target_month, target_day)
            return candidate.strftime("%Y-%m-%d")
        except ValueError:
            # Handle leap year issues, use Feb 28 instead of Feb 29
            candidate = date(current.year + 1, target_month, 28)
            return candidate.strftime("%Y-%m-%d")
            
    except ValueError:
        # Invalid date format, return a safe future date
        current = get_current_date()
        safe_date = current + timedelta(days=max(30, offset_days))  # At least 30 days in future
        return safe_date.strftime("%Y-%m-%d")


def get_planting_season_dates(region_hint: str = "Trans Nzoia") -> Dict[str, str]:
    """
    Get appropriate planting season dates for the region, ensuring they are in the future.
    
    Args:
        region_hint: Region name for seasonal adjustments
        
    Returns:
        Dictionary with planting season start and end dates
    """
    current = get_current_date()
    
    # Kenya has two main seasons:
    # Long rains (March-July): Plant March-April
    # Short rains (October-December): Plant October-November
    
    # Determine which season we should target
    current_month = current.month
    
    if current_month >= 1 and current_month <= 6:
        # We're in first half of year, target long rains season
        season_start_month = 3  # March
        season_end_month = 4    # April
        target_year = current.year
        
        # If we're past April, target next year
        if current_month > 4:
            target_year = current.year + 1
            
    elif current_month >= 7 and current_month <= 9:
        # We're in July-September, target short rains season
        season_start_month = 10  # October
        season_end_month = 11   # November
        target_year = current.year
        
    else:
        # We're in October-December, target next year's long rains
        season_start_month = 3  # March
        season_end_month = 4    # April
        target_year = current.year + 1
    
    # Generate specific dates
    season_start = date(target_year, season_start_month, 15)  # Mid-month for flexibility
    season_end = date(target_year, season_end_month, 30)
    
    # Ensure dates are at least 7 days in the future for planning
    min_date = current + timedelta(days=7)
    if season_start < min_date:
        # Adjust to next season
        if season_start_month == 3:  # Was long rains, move to short rains
            season_start = date(target_year, 10, 15)
            season_end = date(target_year, 11, 30)
        else:  # Was short rains, move to next year's long rains
            season_start = date(target_year + 1, 3, 15)
            season_end = date(target_year + 1, 4, 30)
    
    return {
        "long_season_start": season_start.strftime("%Y-%m-%d"),
        "long_season_end": season_end.strftime("%Y-%m-%d"),
        "season_type": "long_rains" if season_start.month == 3 else "short_rains"
    }


def update_knowledge_context_dates(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update knowledge context with current/future dates instead of hardcoded past dates.
    
    Args:
        context: Knowledge context dictionary from experiment agents
        
    Returns:
        Updated context with appropriate future dates
    """
    # Get current seasonal dates
    season_dates = get_planting_season_dates(
        context.get("region", {}).get("county", "Trans Nzoia")
    )
    
    # Update region information with current season dates
    if "region" in context:
        context["region"].update(season_dates)
    
    # Update default planting date to be in the future
    if "planting_date" in context:
        context["planting_date"] = ensure_future_date(
            context["planting_date"], 
            offset_days=7  # At least a week in the future
        )
    
    # Update guidelines if they exist
    if "guidelines" in context and "default_planting_date" in context["guidelines"]:
        context["guidelines"]["default_planting_date"] = ensure_future_date(
            context["guidelines"]["default_planting_date"],
            offset_days=7
        )
    
    return context


def format_date_for_display(date_str: str) -> str:
    """
    Format date string for user-friendly display.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        Formatted date string
    """
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        return parsed.strftime("%B %d, %Y")
    except ValueError:
        return date_str


def get_simulation_metadata() -> Dict[str, Any]:
    """Get simulation metadata for experiment design."""
    window = get_simulation_window()
    season = get_planting_season_dates()
    
    return {
        "current_date": get_current_date().strftime("%Y-%m-%d"),
        "simulation_window": window,
        "recommended_season": season,
        "simulation_years": window["simulation_years"],
        "weather_forecast_available": True,  # We have forecast data from current date
    }
