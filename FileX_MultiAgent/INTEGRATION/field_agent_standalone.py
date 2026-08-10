#!/usr/bin/env python3
"""
Standalone FieldAgent Test Runner - Complete Field Parameters
Outputs ALL field parameters in JSON format
Handles partial success - extracts soil even if weather fails
"""

import json
import sys
from typing import Dict, Any

# ============================================================================
# COMPLETE FIELDAGENT WITH PROPER PARTIAL SUCCESS HANDLING
# ============================================================================

class FieldAgent:
    """
    Agent responsible for generating complete field metadata.
    Outputs ALL field parameters in JSON format.
    """
    
    @staticmethod
    def process(config: Dict[str, Any], xcrd: float, ycrd: float) -> Dict[str, Any]:
        field_config = config.get("field", {})
        
        print("\n" + "="*70)
        print("FieldAgent: Generating Soil and Weather Files")
        print("="*70)
        
        result = {
            "field_metadata": None,
            "messages": [],
            "errors": []
        }
        
        # Variables to track partial success
        id_soil = None
        insi_code = None
        new_wsta = None
        id_field = None
        sol_file = None
        wth_file = None
        start_date = None
        end_date = None
        duration_years = None
        
        # GET WEATHER DATE RANGE FROM CONFIG.JSON
        weather_config = config.get("weather", {})
        
        # Try to get from weather section first
        start_date = weather_config.get("start_date")
        end_date = weather_config.get("end_date")
        
        # If not in weather section, check if it's at root level
        if not start_date:
            start_date = config.get("start_date")
        if not end_date:
            end_date = config.get("end_date")
        
        # If still not found, use defaults
        if not start_date or not end_date:
            print("⚠️  Weather dates not in config, using defaults")
            start_date = "2024-01-01"
            end_date = "2025-12-31"
        
        print(f"  → Coordinates: Lat={xcrd}, Lon={ycrd}")
        print(f"  → Weather Period (from config): {start_date} to {end_date}")
        
        # Try to generate files - catch errors but extract what we can
        try:
            # Try soil generation separately first (cached on lat/lon)
            from INTEGRATION.field_data_cache import get_or_generate_soil, get_or_generate_weather

            try:
                id_soil, sol_file = get_or_generate_soil(xcrd, ycrd)
                print(f"\n✅ Captured soil: ID_SOIL={id_soil}, file={sol_file}")
            except Exception as soil_err:
                print(f"\n⚠️  Soil generation failed: {soil_err}")

            # Try weather generation separately (cached on lat/lon/date range)
            try:
                insi_code, wth_file = get_or_generate_weather(xcrd, ycrd, start_date, end_date)
                print(f"✅ Captured weather: INSI={insi_code}, file={wth_file}")
            except Exception as weather_err:
                print(f"⚠️  Weather generation failed: {weather_err}")
                result["errors"].append(f"Weather generation failed: {str(weather_err)[:200]}")
            
        except Exception as e:
            error_msg = f"File generation error: {e}"
            result["errors"].append(error_msg)
            print(f"\n⚠️  {error_msg}")
        
        # Calculate WSTA and duration even if weather failed
        try:
            from datetime import datetime

            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

            # 6-month rounding: remainder > 6 months → round up, else round down
            full_years = end_date_obj.year - start_date_obj.year
            if (end_date_obj.month, end_date_obj.day) < (start_date_obj.month, start_date_obj.day):
                full_years -= 1
            try:
                anniversary = start_date_obj.replace(year=start_date_obj.year + full_years)
            except ValueError:
                anniversary = start_date_obj.replace(year=start_date_obj.year + full_years, day=28)
            remaining_months = (end_date_obj - anniversary).days / 30.44
            duration_years = max(1, full_years + 1 if remaining_months > 6 else full_years)

            start_year_yy = start_date_obj.year % 100
            
            # Use generated INSI if available, otherwise create generic
            if insi_code and insi_code != "XXXX":
                new_wsta = f"{insi_code[:4]}{start_year_yy:02d}{duration_years:02d}"
            else:
                # Generic WSTA based on coordinates if weather failed
                new_wsta = f"UNKN{start_year_yy:02d}{duration_years:02d}"
            
            id_field = new_wsta
            
        except Exception as date_err:
            print(f"⚠️  Date calculation error: {date_err}")
            new_wsta = "UNKN0000"
            id_field = "UNKN0000"
        
        # Build field result with whatever we got
        # Use generated values if available, otherwise fallback to config, otherwise defaults
        
        final_id_soil = id_soil if id_soil else field_config.get("id_soil", field_config.get("ID_SOIL", "DFLT000001"))
        final_wsta = new_wsta if new_wsta else field_config.get("wsta", field_config.get("WSTA", "DFLT0101"))
        final_id_field = id_field if id_field else field_config.get("id_field", field_config.get("ID_FIELD", "DEFAULT01"))
        
        # Build narrative based on what succeeded
        if id_soil and insi_code and insi_code != "XXXX":
            narrative = f"Field configuration for location at Lat={xcrd}, Lon={ycrd}. " \
                       f"Soil and weather files generated successfully. Weather data spans " \
                       f"{duration_years} year(s) from {start_date} to {end_date}. " \
                       f"The field uses soil profile {final_id_soil} and weather station {final_wsta}."
            status_msg = "Soil ✓, Weather ✓"
        elif id_soil and (not insi_code or insi_code == "XXXX"):
            narrative = f"Field configuration for location at Lat={xcrd}, Lon={ycrd}. " \
                       f"Soil file generated successfully (ID_SOIL: {final_id_soil}), " \
                       f"but weather file generation failed due to network issues. " \
                       f"Using generic WSTA: {final_wsta}."
            status_msg = "Soil ✓, Weather ✗"
        else:
            narrative = f"Using fallback field configuration due to generation errors. " \
                       f"Location: Lat={xcrd}, Lon={ycrd}."
            status_msg = "Fallback"
        
        # Create COMPLETE JSON output with ALL field parameters
        field_result = {
            "narrative": narrative,
            "field_section": {
                # Generated/Fallback fields
                "id_field": final_id_field,
                "wsta": final_wsta,
                "id_soil": final_id_soil,
                "xcrd": xcrd,
                "ycrd": ycrd,
                
                # Optional fields - use config if present, otherwise -99
                "flsa": field_config.get("flsa", field_config.get("FLSA", -99)),
                "flob": field_config.get("flob", field_config.get("FLOB", -99)),
                "fldt": field_config.get("fldt", field_config.get("FLDT", "-99")),
                "fldd": field_config.get("fldd", field_config.get("FLDD", -99)),
                "flds": field_config.get("flds", field_config.get("FLDS", -99)),
                "flst": field_config.get("flst", field_config.get("FLST", -99)),
                "sltx": field_config.get("sltx", field_config.get("SLTX", -99)),
                "sldp": field_config.get("sldp", field_config.get("SLDP", -99)),
                "flname": field_config.get("flname", field_config.get("FLNAME", -99)),
                "elev": field_config.get("elev", field_config.get("ELEV", -99)),
                "area": field_config.get("area", field_config.get("AREA", -99)),
                "slen": field_config.get("slen", field_config.get("SLEN", -99)),
                "flwr": field_config.get("flwr", field_config.get("FLWR", -99)),
                "slas": field_config.get("slas", field_config.get("SLAS", -99)),
                "flhst": field_config.get("flhst", field_config.get("FLHST", -99)),
                "fhdur": field_config.get("fhdur", field_config.get("FHDUR", -99)),
                
                # Additional metadata
                "metadata": {
                    "original_insi": insi_code if insi_code else "N/A",
                    "sol_file": sol_file if sol_file else "N/A",
                    "wth_file": wth_file if wth_file else "N/A",
                    "weather_start": start_date,
                    "weather_end": end_date,
                    "weather_duration_years": duration_years if duration_years else "N/A",
                    "generation_status": {
                        "soil_generated": bool(id_soil),
                        "weather_generated": bool(insi_code and insi_code != "XXXX")
                    }
                }
            }
        }
        
        # Print JSON output to terminal
        print()
        print(f"Field results ({status_msg})" + "-"*(70-len(f"Field results ({status_msg})")))
        print(json.dumps(field_result, indent=2))
        print("end result" + "-"*65)
        print()
        
        result["field_metadata"] = field_result["field_section"]
        result["messages"].append(
            f"FieldAgent: Generated Field metadata "
            f"(ID_FIELD={final_id_field}, WSTA={final_wsta}, ID_SOIL={final_id_soil})"
        )
        
        if id_soil:
            result["messages"].append(f"✓ Soil generation successful: {sol_file}")
        else:
            result["messages"].append(f"✗ Soil generation failed")
            
        if insi_code and insi_code != "XXXX":
            result["messages"].append(f"✓ Weather generation successful: {wth_file}")
        else:
            result["messages"].append(f"✗ Weather generation failed (network issue)")
        
        return result


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run only FieldAgent"""
    
    if len(sys.argv) < 2:
        print("Usage: python test_field_agent_simple.py <config.json>")
        print("Example: python test_field_agent_simple.py MZ_Kenya_Configure_Inputs.json")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    print("="*70)
    print("STANDALONE FIELDAGENT TEST - ALL PARAMETERS")
    print("="*70)
    print(f"Loading config: {config_path}\n")
    
    # Load config
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        sys.exit(1)
    
    # Extract coordinates
    latitude = config.get("Location", {}).get("Latitude")
    longitude = config.get("Location", {}).get("Longitude")
    
    if latitude is None or longitude is None:
        print("✗ Missing Location.Latitude or Location.Longitude in config")
        sys.exit(1)
    
    print(f"📍 Location: Lat={latitude}, Lon={longitude}\n")
    
    # Run FieldAgent
    result = FieldAgent.process(config, latitude, longitude)
    
    # Display results
    print("\n" + "="*70)
    print("FIELDAGENT EXECUTION COMPLETE")
    print("="*70)
    
    if result["errors"]:
        print("\n❌ Errors:")
        for err in result["errors"]:
            print(f"  • {err}")
    
    if result["messages"]:
        print("\n✅ Messages:")
        for msg in result["messages"]:
            print(f"  • {msg}")
    
    if result.get("field_metadata"):
        print("\n📊 Complete Field Metadata (ALL PARAMETERS):")
        print(json.dumps(result["field_metadata"], indent=2))
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()