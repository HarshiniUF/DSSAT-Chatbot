"""
The Specialist Tool for DSSAT Data Lookup and File Generation.
This version performs the full workflow:
1.  TIF lookup -> map_id
2.  DB lookup -> site_id
3.  .SOL file search -> profile data
4.  New .SOL file creation
"""
import os
import sqlite3
import rasterio
def _extract_profile_from_file(source_path: str, site_id: str) -> list[str]:
    """
    Searches a large .SOL file for a specific site_id and extracts its profile.
    A profile starts with a line like '*SITE_ID...' and ends before the next
    line that starts with '*' or at the end of the file.
    """
    profile_data = []
    is_capturing = False
    
    try:
        with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # A profile starts with '*<site_id>'.
                if line.strip().startswith(f"*{site_id}"):
                    is_capturing = True
                
                # If we've started and hit the *next* profile, we should stop.
                elif is_capturing and line.strip().startswith('*'):
                    break
                
                # If we are in the correct section, collect the line.
                if is_capturing:
                    profile_data.append(line)
        
        return profile_data
    except FileNotFoundError:
        raise FileNotFoundError(f"The required source file '{source_path}' was not found.")

def run_soil_file_generation(lat: float, lon: float) -> str:
    """
    Orchestrates the full data lookup and file creation process.
    The output filename is generated dynamically from the site_id.
    """
    tif_path = 'INTEGRATION/soil/GHR_cleaned_2.tif'
    db_path  = 'INTEGRATION/soil/GHR.db'
    source_folder = 'INTEGRATION/eGHR'
    
    print("--- Tool: Starting full soil profile generation workflow. ---")
    
    try:
        # Step 1: Get the unique Map ID from the TIF file
        print(f"--- Tool: 1. Discovering Map ID from '{tif_path}'...")
        with rasterio.open(tif_path) as src:
            sample = next(src.sample([(lon, lat)]))[0]
            if sample is None or sample < 0:
                raise ValueError("Coordinates are outside the raster's bounds or hit a no-data pixel.")
            map_id = int(sample)
            print(f"   ✅ Discovered Map ID: {map_id}")
        # Step 2: Use Map ID to get the Site ID and create the output filename
        print(f"--- Tool: 2. Looking up Site ID in 'profile_map' for map_id={map_id}...")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT profile FROM profile_map WHERE id = ?", (map_id,))
            row = cursor.fetchone()
            if row is None or not row[0]:
                raise ValueError(f"No Site ID found for Map ID {map_id} in 'profile_map'.")
            site_id = row[0].strip()
            print(f"   ✅ Successfully looked up Site ID: {site_id}")
        
        # New: Dynamically generate the output filename from the site_id
        output_filename = f"{site_id}.sol"
        print(f"   ℹ️  Output filename will be '{output_filename}'.")
        # Step 3: Determine source .SOL file and search for the profile
        if len(site_id) < 2:
            raise ValueError(f"Site ID '{site_id}' is too short to determine the source file.")
        
        file_prefix = site_id[:2].upper()
        source_sol_filename = f"{file_prefix}.SOL"
        source_sol_path = os.path.join(source_folder, source_sol_filename)
        
        print(f"--- Tool: 3. Searching for profile in '{source_sol_path}'...")
        profile_data = _extract_profile_from_file(source_sol_path, site_id)
        
        if not profile_data:
            raise ValueError(f"Site ID '{site_id}' not found within the file '{source_sol_path}'.")
        print(f"   ✅ Found and extracted profile for Site ID {site_id}.")
        # Step 4: Write the extracted data to the new output file
        print(f"--- Tool: 4. Writing extracted profile to '{output_filename}'...")
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.writelines(profile_data)
        print(f"   ✅ Successfully created '{output_filename}'.")
        success_msg = (
            f"Process complete! Site ID '{site_id}' was found. "
            f"Its profile was extracted from '{source_sol_path}' and saved to '{output_filename}'."
        )
        print(f"--- Tool: {success_msg} ---")
        return success_msg
        
    except Exception as e:
        err_msg = f"Tool execution failed: {e}"
        print(f"--- Tool: {err_msg} ---")
        raise e