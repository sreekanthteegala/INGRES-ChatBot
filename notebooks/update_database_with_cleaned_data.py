"""
UPDATE DATABASE WITH CLEANED DATA
==================================

This script replaces the existing database with the newly cleaned dataset.
"""

import pandas as pd
import sqlite3
import os
from pathlib import Path

# Configuration
CLEANED_DATA = "processed_data/groundwater_cleaned.csv"
DATABASE_FILE = "groundwater.db"
TABLE_NAME = "groundwater"
BACKUP_DB = "groundwater_backup.db"

def main():
    print("="*70)
    print("DATABASE UPDATE WITH CLEANED DATA")
    print("="*70)
    
    # Check if cleaned data exists
    if not Path(CLEANED_DATA).exists():
        print(f"\n✗ ERROR: Cleaned data file not found: {CLEANED_DATA}")
        print("  Please run preprocess_groundwater_data.py first!")
        return
    
    # Load cleaned data
    print(f"\nLoading cleaned data from {CLEANED_DATA}...")
    df = pd.read_csv(CLEANED_DATA, low_memory=False)
    
    print(f"  → Loaded {len(df):,} rows")
    print(f"  → Columns: {len(df.columns)}")
    
    # Backup existing database
    if Path(DATABASE_FILE).exists():
        print(f"\nBacking up existing database to {BACKUP_DB}...")
        import shutil
        shutil.copy2(DATABASE_FILE, BACKUP_DB)
        print(f"  ✓ Backup created")
    
    # Connect to database
    print(f"\nConnecting to database: {DATABASE_FILE}")
    conn = sqlite3.connect(DATABASE_FILE)
    
    # Replace table
    print(f"\nReplacing table '{TABLE_NAME}' with cleaned data...")
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
    
    # Verify
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    row_count = cursor.fetchone()[0]
    
    print(f"  ✓ Table updated successfully")
    print(f"  ✓ Rows in database: {row_count:,}")
    
    # Verify data integrity
    print(f"\nVerifying data integrity...")
    
    cursor.execute(f"SELECT COUNT(DISTINCT STATE) FROM {TABLE_NAME}")
    state_count = cursor.fetchone()[0]
    print(f"  → Unique states: {state_count}")
    
    cursor.execute(f"SELECT COUNT(DISTINCT YEAR) FROM {TABLE_NAME}")
    year_count = cursor.fetchone()[0]
    print(f"  → Unique years: {year_count}")
    
    cursor.execute(f"SELECT YEAR, COUNT(*) FROM {TABLE_NAME} GROUP BY YEAR ORDER BY YEAR")
    year_counts = cursor.fetchall()
    print(f"\n  Row counts per year:")
    for year, count in year_counts:
        print(f"    • {year}: {count:,} rows")
    
    # Test query
    print(f"\nTesting sample query...")
    cursor.execute(f"""
        SELECT STATE, DISTRICT, YEAR 
        FROM {TABLE_NAME} 
        WHERE STATE = 'ASSAM' 
        LIMIT 3
    """)
    results = cursor.fetchall()
    print(f"  Sample results (Assam districts):")
    for row in results:
        print(f"    • {row[0]} - {row[1]} - {row[2]}")
    
    conn.close()
    
    print(f"\n{'='*70}")
    print("✓ DATABASE UPDATE COMPLETE!")
    print(f"{'='*70}")
    print(f"\nNext steps:")
    print(f"  1. Restart backend server to use new database")
    print(f"  2. Test queries in the dashboard")
    print(f"  3. If issues occur, restore from backup: {BACKUP_DB}")
    print()

if __name__ == "__main__":
    main()
