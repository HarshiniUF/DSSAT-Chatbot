#!/usr/bin/env python3
"""
Integration Helper Module - Extract metadata from generated soil and weather files
No LLM/API dependencies - pure file generation and parsing
"""
import os
import re
from typing import Tuple, Optional

def generate_soil_file(latitude: float, longitude: float) -> Tuple[str, str]:
    """
    Generate soil file and extract site_id.
    
    Returns:
        Tuple[str, str]: (site_id, sol_filename)
    """
    print("\n" + "="*70)
    print("STEP 1: Generating Soil File")
    print("="*70)
    print(f"  Coordinates: Lat={latitude}, Lon={longitude}")
    
    from INTEGRATION.soil_tool import run_soil_file_generation
    
    try:
        result_message = run_soil_file_generation(lat=latitude, lon=longitude)
        
        # Extract site_id from result message
        site_id_match = re.search(r"Site ID '(\w+)'", result_message)
        if site_id_match:
            site_id = site_id_match.group(1)
            sol_filename = f"{site_id}.sol"
            
            print(f"\n✓ Soil file generated successfully!")
            print(f"  → Site ID (ID_SOIL): {site_id}")
            print(f"  → Filename: {sol_filename}")
            
            return site_id, sol_filename
        else:
            raise ValueError("Could not extract Site ID from soil generation result")
            
    except Exception as e:
        print(f"\n✗ Error generating soil file: {e}")
        raise

def generate_weather_file(latitude: float, longitude: float,
                         start_date: str, end_date: str) -> Tuple[str, str]:
    """
    Generate weather file and extract INSI code.
    
    Returns:
        Tuple[str, str]: (insi_code, wth_filename)
    """
    print("\n" + "="*70)
    print("STEP 2: Generating Weather File")
    print("="*70)
    print(f"  Coordinates: Lat={latitude}, Lon={longitude}")
    print(f"  Period: {start_date} to {end_date}")
    
    from INTEGRATION.config import WEATHER_SOURCE
    if WEATHER_SOURCE == "weatherx":
        from INTEGRATION.dssat_weather_new import generate_weather_for_location
    elif WEATHER_SOURCE == "openmeteo":
        from INTEGRATION.openmeteo_weather import generate_weather_for_location
    else:
        raise ValueError(
            f"Unknown WEATHER_SOURCE '{WEATHER_SOURCE}'. Expected 'openmeteo' or 'weatherx' "
            "(set via INTEGRATION/config.py or the WEATHER_SOURCE env var)."
        )
    
    try:
        wth_filename = generate_weather_for_location(
            latitude=latitude,
            longitude=longitude,
            start_date=start_date,
            end_date=end_date
        )
        
        # Extract INSI code from weather file
        insi_code = extract_insi_from_weather_file(wth_filename)
        
        print(f"\n✓ Weather file generated successfully!")
        print(f"  → INSI Code (WSTA): {insi_code}")
        print(f"  → Filename: {wth_filename}")
        
        return insi_code, wth_filename
        
    except Exception as e:
        print(f"\n✗ Error generating weather file: {e}")
        raise

def extract_insi_from_weather_file(wth_filename: str) -> str:
    """
    Extract INSI code from .WTH file header.
    
    Format in .WTH file:
    @ INSI      LAT     LONG  ELEV   TAV   AMP REFHT WNDHT
      KETR    1.02    35.00  1910.  20.5   2.8   2.0  10.0
    
    Returns:
        str: The INSI code (e.g., 'KETR')
    """
    try:
        with open(wth_filename, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        # Find the line with "@ INSI"
        for i, line in enumerate(lines):
            if line.strip().startswith("@ INSI"):
                # Next line contains the INSI code
                if i + 1 < len(lines):
                    data_line = lines[i + 1].strip()
                    # INSI is the first token
                    insi_code = data_line.split()[0]
                    return insi_code
                    
        raise ValueError(f"Could not find INSI header in {wth_filename}")
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Weather file not found: {wth_filename}")
    except Exception as e:
        raise Exception(f"Error reading weather file {wth_filename}: {e}")

def get_file_metadata(latitude: float, longitude: float,
                     start_date: str, end_date: str) -> dict:
    """
    Main integration function: Generate files and extract metadata.
    
    Returns:
        dict: {
            'id_soil': Site ID from soil file,
            'wsta': INSI code from weather file,
            'sol_file': Path to soil file,
            'wth_file': Path to weather file
        }
    """
    print("\n" + "="*70)
    print("DSSAT FILE INTEGRATION WORKFLOW")
    print("="*70)
    print(f"Location: Lat={latitude}, Lon={longitude}")
    print(f"Weather Period: {start_date} to {end_date}")
    print("="*70)
    
    # Step 1: Generate soil file
    site_id, sol_filename = generate_soil_file(latitude, longitude)
    
    # Step 2: Generate weather file
    insi_code, wth_filename = generate_weather_file(
        latitude, longitude, start_date, end_date
    )
    
    # Step 3: Compile metadata
    metadata = {
        'id_soil': site_id,
        'wsta': insi_code,
        'sol_file': sol_filename,
        'wth_file': wth_filename
    }
    
    print("\n" + "="*70)
    print("STEP 3: Metadata Extraction Complete")
    print("="*70)
    print(f"  → ID_SOIL: {metadata['id_soil']}")
    print(f"  → WSTA (INSI): {metadata['wsta']}")
    print(f"  → Soil File: {metadata['sol_file']}")
    print(f"  → Weather File: {metadata['wth_file']}")
    print("="*70 + "\n")
    
    return metadata

def validate_generated_files(sol_file: str, wth_file: str) -> bool:
    """Validate that generated files exist and are readable."""
    try:
        if not os.path.exists(sol_file):
            print(f"✗ Soil file not found: {sol_file}")
            return False
            
        if not os.path.exists(wth_file):
            print(f"✗ Weather file not found: {wth_file}")
            return False
            
        # Basic content check
        with open(sol_file, 'r', encoding='utf-8', errors='ignore') as f:
            sol_content = f.read()
            if len(sol_content) < 100:
                print(f"✗ Soil file appears empty or corrupted")
                return False
                
        with open(wth_file, 'r', encoding='utf-8', errors='ignore') as f:
            wth_content = f.read()
            if len(wth_content) < 100:
                print(f"✗ Weather file appears empty or corrupted")
                return False
                
        print("✓ File validation passed")
        return True
        
    except Exception as e:
        print(f"✗ File validation error: {e}")
        return False