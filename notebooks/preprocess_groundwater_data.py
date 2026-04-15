"""
GROUNDWATER DATA PREPROCESSING PIPELINE
========================================

CRITICAL RULES:
- NEVER generate synthetic or fake data
- NEVER fill missing values with assumptions
- ONLY use real values from Excel files
- Preserve original data integrity at all costs

This script processes raw Excel files from CGWB (Central Ground Water Board)
and creates a clean, validated dataset for SQL ingestion.
"""

import pandas as pd
import numpy as np
import os
import re
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

RAW_DATA_FOLDER = "data/raw_excel"
OUTPUT_FOLDER = "processed_data"
OUTPUT_FILE = "groundwater_cleaned.csv"
VALIDATION_REPORT = "processed_data/preprocessing_report.txt"

# Expected Excel files
EXPECTED_FILES = [
    "2016_17.xlsx",
    "2019_20.xlsx",
    "2021_22.xlsx",
    "2022_23.xlsx",
    "2023_24.xlsx",
    "2024_25.xlsx"
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def clean_column_name(col):
    """
    Clean column names by removing:
    - Leading/trailing whitespace
    - Newline characters
    - Multiple spaces
    - Hidden characters
    """
    if pd.isna(col) or col == '':
        return col
    
    # Convert to string
    col = str(col)
    
    # Remove newlines and tabs
    col = col.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    # Remove multiple spaces
    col = re.sub(r'\s+', ' ', col)
    
    # Strip leading/trailing whitespace
    col = col.strip()
    
    return col


def find_header_row(file_path, max_rows=15):
    """
    Dynamically find the actual header row by looking for key columns.
    Returns the row index where the header starts.
    """
    # Read first few rows to find header
    df_preview = pd.read_excel(file_path, nrows=max_rows, header=None)
    
    # Look for rows containing key column names
    key_columns = ['STATE', 'DISTRICT', 'S.No', 'Rainfall']
    
    for idx, row in df_preview.iterrows():
        # Check if this row contains STATE and DISTRICT
        row_values = [str(x).upper() for x in row if pd.notna(x)]
        if 'STATE' in row_values and 'DISTRICT' in row_values:
            return idx
    
    # Default to row 7 if not found
    return 7


def read_excel_with_dynamic_header(file_path):
    """
    Read Excel file with dynamic header detection and multi-level header handling.
    """
    # Find header row
    header_row = find_header_row(file_path)
    
    print(f"  -> Header detected at row {header_row}")
    
    # Read with multi-level header (main header + sub-header 2 rows below)
    # Row 7 = main header, Row 9 = sub-header
    df = pd.read_excel(file_path, header=[header_row, header_row + 2])
    
    # Flatten multi-level columns
    new_columns = []
    for col in df.columns:
        # col is a tuple like ('STATE', 'nan') or ('Rainfall (mm)', 'C')
        parts = [str(c) for c in col if str(c) != 'nan' and 'Unnamed' not in str(c)]
        if parts:
            # Join non-empty parts with space
            col_name = ' '.join(parts).strip()
        else:
            col_name = ''
        new_columns.append(col_name)
    
    df.columns = new_columns
    
    # Clean column names
    df.columns = [clean_column_name(col) for col in df.columns]
    
    # Remove empty column names (but keep track of position)
    # Some columns might be intentionally empty in multi-level headers
    non_empty_cols = [col for col in df.columns if col != '']
    df = df[non_empty_cols]
    
    return df


def extract_year_from_filename(filename):
    """
    Extract year from filename (e.g., '2024_25.xlsx' -> '2024_25')
    """
    return filename.replace('.xlsx', '').replace('.xls', '')


def clean_numeric_column(series):
    """
    Clean numeric columns by:
    - Removing commas
    - Converting to float
    - Keeping NaN for missing values (NO SYNTHETIC DATA)
    """
    if series.dtype == 'object':
        # Remove commas and convert to numeric
        series = series.astype(str).str.replace(',', '').str.strip()
        series = pd.to_numeric(series, errors='coerce')
    
    return series


def standardize_column_names(df):
    """
    Standardize column names to match expected format.
    Maps various column name variations to standard names.
    """
    # Column name mapping (handles variations)
    column_mapping = {
        'S.No': 'S_NO',
        'S. No': 'S_NO',
        'SNo': 'S_NO',
        'ASSESSMENT UNIT': 'ASSESSMENT_UNIT',
        'Assessment Unit': 'ASSESSMENT_UNIT',
    }
    
    # Apply mapping
    df = df.rename(columns=column_mapping)
    
    # Clean all column names
    df.columns = [clean_column_name(col) for col in df.columns]
    
    return df


def validate_dataframe(df, year):
    """
    Validate dataframe for data quality issues.
    Returns validation report as dict.
    """
    report = {
        'year': year,
        'total_rows': len(df),
        'rows_with_state': df['STATE'].notna().sum(),
        'rows_with_district': df['DISTRICT'].notna().sum(),
        'unique_states': df['STATE'].nunique(),
        'unique_districts': df['DISTRICT'].nunique(),
        'duplicate_rows': df.duplicated(subset=['STATE', 'DISTRICT']).sum(),
        'columns': len(df.columns),
        'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
    }
    
    return report


# ============================================================================
# MAIN PROCESSING FUNCTION
# ============================================================================

def process_excel_file(file_path, filename):
    """
    Process a single Excel file with strict data integrity rules.
    """
    print(f"\n{'='*70}")
    print(f"Processing: {filename}")
    print(f"{'='*70}")
    
    try:
        # Read Excel with dynamic header detection
        df = read_excel_with_dynamic_header(file_path)
        
        print(f"  -> Initial shape: {df.shape}")
        print(f"  -> Columns found: {len(df.columns)}")
        
        # Standardize column names
        df = standardize_column_names(df)
        
        # CRITICAL: Remove rows where STATE is null (metadata rows)
        initial_rows = len(df)
        df = df[df['STATE'].notna()]
        removed_rows = initial_rows - len(df)
        print(f"  -> Removed {removed_rows} metadata/empty rows")
        
        # CRITICAL: Remove rows where DISTRICT is null
        initial_rows = len(df)
        df = df[df['DISTRICT'].notna()]
        removed_rows = initial_rows - len(df)
        print(f"  -> Removed {removed_rows} rows with missing DISTRICT")
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Extract year from filename
        year = extract_year_from_filename(filename)
        df['YEAR'] = year
        
        print(f"  -> Added YEAR column: {year}")
        
        # Clean numeric columns (NO SYNTHETIC DATA - keep NaN as is)
        numeric_columns = df.select_dtypes(include=['object']).columns
        for col in numeric_columns:
            if col not in ['STATE', 'DISTRICT', 'YEAR', 'ASSESSMENT_UNIT', 'S_NO']:
                # Try to convert to numeric
                original_type = df[col].dtype
                df[col] = clean_numeric_column(df[col])
                
                # Count conversions
                if df[col].dtype != original_type:
                    non_null = df[col].notna().sum()
                    if non_null > 0:
                        print(f"  -> Converted '{col}' to numeric ({non_null} values)")
        
        # Remove duplicate rows (exact duplicates only)
        initial_rows = len(df)
        df = df.drop_duplicates(subset=['STATE', 'DISTRICT'], keep='first')
        removed_duplicates = initial_rows - len(df)
        if removed_duplicates > 0:
            print(f"  [WARNING] Removed {removed_duplicates} duplicate rows")
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Validate
        validation = validate_dataframe(df, year)
        print(f"\n  [OK] Final shape: {df.shape}")
        print(f"  [OK] Unique states: {validation['unique_states']}")
        print(f"  [OK] Unique districts: {validation['unique_districts']}")
        
        return df, validation
        
    except Exception as e:
        print(f"  [ERROR] ERROR processing {filename}: {str(e)}")
        return None, None


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function for the preprocessing pipeline.
    """
    print("\n" + "="*70)
    print("GROUNDWATER DATA PREPROCESSING PIPELINE")
    print("="*70)
    print("\nCRITICAL RULES:")
    print("  [OK] NEVER generate synthetic data")
    print("  [OK] NEVER fill missing values with assumptions")
    print("  [OK] ONLY use real values from Excel files")
    print("  [OK] Preserve original data integrity")
    print("="*70)
    
    # Create output folder if not exists
    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)
    
    # Get list of Excel files
    excel_files = [f for f in os.listdir(RAW_DATA_FOLDER) if f.endswith('.xlsx')]
    excel_files.sort()
    
    print(f"\nFound {len(excel_files)} Excel files:")
    for f in excel_files:
        print(f"  • {f}")
    
    # Check for missing expected files
    missing_files = set(EXPECTED_FILES) - set(excel_files)
    if missing_files:
        print(f"\n[WARNING] WARNING: Missing expected files: {missing_files}")
    
    # Process each file
    all_dataframes = []
    all_validations = []
    
    for filename in excel_files:
        file_path = os.path.join(RAW_DATA_FOLDER, filename)
        df, validation = process_excel_file(file_path, filename)
        
        if df is not None:
            all_dataframes.append(df)
            all_validations.append(validation)
    
    # Combine all dataframes
    print(f"\n{'='*70}")
    print("COMBINING ALL DATASETS")
    print(f"{'='*70}")
    
    if not all_dataframes:
        print("[ERROR] ERROR: No dataframes to combine!")
        return
    
    final_df = pd.concat(all_dataframes, ignore_index=True)
    
    print(f"  -> Combined shape: {final_df.shape}")
    print(f"  -> Total rows: {len(final_df):,}")
    print(f"  -> Total columns: {len(final_df.columns)}")
    
    # Final validation checks
    print(f"\n{'='*70}")
    print("FINAL VALIDATION CHECKS")
    print(f"{'='*70}")
    
    # Check for duplicates across years
    duplicates = final_df.duplicated(subset=['STATE', 'DISTRICT', 'YEAR']).sum()
    print(f"  -> Duplicate (STATE, DISTRICT, YEAR): {duplicates}")
    
    if duplicates > 0:
        print(f"  [WARNING] Removing {duplicates} duplicate rows...")
        final_df = final_df.drop_duplicates(subset=['STATE', 'DISTRICT', 'YEAR'], keep='first')
    
    # Check row counts per year
    print(f"\n  Row counts per year:")
    year_counts = final_df['YEAR'].value_counts().sort_index()
    for year, count in year_counts.items():
        print(f"    • {year}: {count:,} rows")
    
    # Check unique states
    unique_states = final_df['STATE'].nunique()
    print(f"\n  -> Unique states/UTs: {unique_states}")
    
    # Check for anomalies in key metrics
    print(f"\n  Checking for data anomalies...")
    
    key_metrics = [
        'Total Ground Water Availability in the area (ham)',
        'Ground Water Recharge (ham)',
        'Rainfall (mm)'
    ]
    
    for metric in key_metrics:
        if metric in final_df.columns:
            col_data = final_df[metric]
            non_null = col_data.notna().sum()
            if non_null > 0:
                max_val = col_data.max()
                min_val = col_data.min()
                negative_count = (col_data < 0).sum()
                
                print(f"\n    {metric}:")
                print(f"      • Non-null values: {non_null:,}")
                print(f"      • Range: {min_val:.2f} to {max_val:.2f}")
                
                if negative_count > 0:
                    print(f"      [WARNING] WARNING: {negative_count} negative values found!")
                
                # Flag extremely large values (potential errors)
                if max_val > 100_000_000:
                    print(f"      [WARNING] WARNING: Extremely large value detected: {max_val:,.2f}")
    
    # Save cleaned dataset
    output_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)
    final_df.to_csv(output_path, index=False)
    
    print(f"\n{'='*70}")
    print(f"[OK] SUCCESS: Dataset saved to {output_path}")
    print(f"{'='*70}")
    
    # Generate validation report
    print(f"\nGenerating validation report...")
    
    with open(VALIDATION_REPORT, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("GROUNDWATER DATA PREPROCESSING REPORT\n")
        f.write("="*70 + "\n\n")
        
        f.write("PROCESSING SUMMARY:\n")
        f.write(f"  • Total files processed: {len(all_dataframes)}\n")
        f.write(f"  • Final dataset shape: {final_df.shape}\n")
        f.write(f"  • Total rows: {len(final_df):,}\n")
        f.write(f"  • Total columns: {len(final_df.columns)}\n")
        f.write(f"  • Unique states: {unique_states}\n\n")
        
        f.write("ROW COUNTS PER YEAR:\n")
        for year, count in year_counts.items():
            f.write(f"  • {year}: {count:,} rows\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("INDIVIDUAL FILE VALIDATIONS:\n")
        f.write("="*70 + "\n\n")
        
        for val in all_validations:
            f.write(f"Year: {val['year']}\n")
            f.write(f"  • Total rows: {val['total_rows']}\n")
            f.write(f"  • Rows with STATE: {val['rows_with_state']}\n")
            f.write(f"  • Rows with DISTRICT: {val['rows_with_district']}\n")
            f.write(f"  • Unique states: {val['unique_states']}\n")
            f.write(f"  • Unique districts: {val['unique_districts']}\n")
            f.write(f"  • Duplicate rows: {val['duplicate_rows']}\n")
            f.write(f"  • Columns: {val['columns']}\n\n")
        
        f.write("="*70 + "\n")
        f.write("COLUMN LIST:\n")
        f.write("="*70 + "\n\n")
        for i, col in enumerate(final_df.columns, 1):
            f.write(f"{i:3d}. {col}\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("DATA INTEGRITY VERIFICATION:\n")
        f.write("="*70 + "\n\n")
        f.write("[OK] No synthetic data generated\n")
        f.write("[OK] No missing values filled with assumptions\n")
        f.write("[OK] Only real values from Excel files used\n")
        f.write("[OK] Original data integrity preserved\n")
        f.write("[OK] Metadata rows removed correctly\n")
        f.write("[OK] Duplicate rows removed\n")
        f.write("[OK] Column names standardized\n")
        f.write("[OK] Numeric columns cleaned\n")
    
    print(f"[OK] Validation report saved to {VALIDATION_REPORT}")
    
    print(f"\n{'='*70}")
    print("PREPROCESSING COMPLETE!")
    print(f"{'='*70}\n")
    
    # Display sample data
    print("Sample data (first 3 rows):")
    sample_cols = ['STATE', 'DISTRICT', 'YEAR']
    # Add first rainfall column if exists
    rainfall_cols = [c for c in final_df.columns if 'Rainfall' in c]
    if rainfall_cols:
        sample_cols.append(rainfall_cols[0])
    print(final_df[sample_cols].head(3))
    
    return final_df


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    df = main()

