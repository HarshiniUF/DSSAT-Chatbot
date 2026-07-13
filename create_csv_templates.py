#!/usr/bin/env python3
"""
CSV Template Generator for DSSAT Assistant
Creates minimal CSV files if they don't exist (Hybrid Option C support)
"""

import os
import csv

def create_knowledge_base():
    """Create basic knowledge_base.csv"""
    
    if os.path.exists("knowledge_base.csv"):
        print("✓ knowledge_base.csv already exists")
        return
    
    data = [
        ["question", "answer", "category"],
        ["What is DSSAT?", "DSSAT (Decision Support System for Agrotechnology Transfer) is a crop modeling software that simulates crop growth and development under different management practices and environmental conditions.", "definition"],
        ["What is crop simulation?", "Crop simulation is a mathematical modeling approach that predicts crop growth, development, and yield based on genetics, environment, and management factors.", "definition"],
        ["How does DSSAT help farmers?", "DSSAT helps farmers by simulating different management scenarios (planting dates, fertilizer rates, irrigation strategies) to identify optimal practices before implementing them in the field.", "benefits"],
        ["What is fertilizer?", "Fertilizer is a substance added to soil to supply essential nutrients (nitrogen, phosphorus, potassium) needed for plant growth and development.", "definition"],
        ["What is DAP fertilizer?", "DAP (Diammonium Phosphate) is a fertilizer containing 18% nitrogen and 46% phosphorus (as P2O5), commonly used as a basal fertilizer at planting.", "fertilizer"],
        ["What is CAN fertilizer?", "CAN (Calcium Ammonium Nitrate) is a fertilizer containing 26% nitrogen, commonly used for topdressing during crop growth.", "fertilizer"],
    ]
    
    with open("knowledge_base.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    print("✓ Created knowledge_base.csv")

def create_enhanced_knowledge_base():
    """Create enhanced_knowledge_base.csv with regional info"""
    
    if os.path.exists("enhanced_knowledge_base.csv"):
        print("✓ enhanced_knowledge_base.csv already exists")
        return
    
    data = [
        ["region", "altitude_m", "rainfall_mm", "temperature_c", "soil_type", "main_season", "planting_window", "cultivar_recommendation"],
        ["Trans Nzoia", "1800-2100", "1200-1500", "18-24", "Sandy clay loam", "March-August", "March 15 - April 15", "H614, H622"],
        ["Uasin Gishu", "1900-2200", "1000-1400", "17-23", "Clay loam", "March-August", "March 20 - April 20", "H614, DH04"],
        ["Nakuru", "1800-2400", "800-1200", "16-22", "Volcanic loam", "March-July", "March 10 - April 10", "H622, DH04"],
    ]
    
    with open("enhanced_knowledge_base.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    print("✓ Created enhanced_knowledge_base.csv")

def create_fertilizer_database():
    """Create fertilizer_database.csv with DSSAT codes"""
    
    if os.path.exists("fertilizer_database.csv"):
        print("✓ fertilizer_database.csv already exists")
        return
    
    data = [
        ["fertilizer", "nitrogen", "phosphorus", "potassium", "cost_per_kg", "dssat_fmcd_code", "dssat_facd_code"],
        ["DAP", "18", "46", "0", "45.00", "FE005", "AP001"],
        ["CAN", "26", "0", "0", "35.00", "FE027", "AP002"],
        ["Urea", "46", "0", "0", "30.00", "FE001", "AP001"],
        ["MAP", "11", "52", "0", "48.00", "FE003", "AP001"],
        ["NPK 17-17-17", "17", "17", "17", "40.00", "FE900", "AP001"],
        ["NPK 23-23-0", "23", "23", "0", "42.00", "FE900", "AP001"],
        ["TSP", "0", "46", "0", "38.00", "FE004", "AP001"],
        ["MOP", "0", "0", "60", "32.00", "FE006", "AP001"],
    ]
    
    with open("fertilizer_database.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    print("✓ Created fertilizer_database.csv")

def main():
    """Create all CSV templates"""
    print("=" * 50)
    print("CSV Template Generator for DSSAT Assistant")
    print("=" * 50)
    print()
    
    create_knowledge_base()
    create_enhanced_knowledge_base()
    create_fertilizer_database()
    
    print()
    print("=" * 50)
    print("✓ All CSV templates created successfully!")
    print("=" * 50)
    print()
    print("Note: These are minimal templates.")
    print("For production use, expand with your actual data.")

if __name__ == "__main__":
    main()