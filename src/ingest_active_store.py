# ingest_active_store.py
import os
import pandas as pd
from database import supabase

# Get the project root directory (parent of src/)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
excel_path = os.path.join(project_root, "data", "Sales & Active Stores Data 2_4df7a3c266e1468f89ea60b5663fbd6b_converted (3).xlsx")

# Define the columns that exist in the active_store table
SCHEMA_COLUMNS = [
    'customer_account_name',  # PRIMARY KEY
    # 2024 months
    'apr_2024', 'aug_2024', 'dec_2024', 'feb_2024', 'jan_2024',
    'jul_2024', 'jun_2024', 'mar_2024', 'may_2024', 'nov_2024',
    'oct_2024', 'sep_2024',
    'total_2024',
    # 2025 months
    'apr_2025', 'aug_2025', 'dec_2025', 'feb_2025', 'jan_2025',
    'jul_2025', 'jun_2025', 'mar_2025', 'may_2025', 'nov_2025',
    'oct_2025', 'sep_2025',
    'total_2025',
    # Overall
    'grand_total'
]

# Check if data already exists in the table
try:
    existing_data = supabase.table("active_store").select("customer_account_name", count="exact").limit(1).execute()
    if existing_data.count and existing_data.count > 0:
        print(f"⚠️  Warning: Table 'active_store' already contains {existing_data.count} records.")
        response = input("Do you want to continue and add more data? (yes/no): ").strip().lower()
        if response != "yes":
            print("Operation cancelled.")
            exit(0)
except Exception as e:
    print(f"Note: Could not check existing data: {e}")
    print("Proceeding with data ingestion...")

# Read Excel file
print("Reading Excel file...")
print(f"Looking for file at: {excel_path}")
if not os.path.exists(excel_path):
    print(f"❌ Error: File not found at {excel_path}")
    exit(1)

print("Reading sheet: 'Active Store'")
try:
    df = pd.read_excel(excel_path, sheet_name="Active Store")
    print(f"Loaded {len(df)} rows from Excel")
except Exception as e:
    print(f"❌ Error reading sheet 'Active Store': {e}")
    print("Available sheets:", pd.ExcelFile(excel_path).sheet_names)
    exit(1)

# Check if DataFrame is empty
if df.empty:
    print("❌ Error: The sheet 'Active Store' is empty or has no data!")
    exit(1)

# Check if DataFrame has columns
if len(df.columns) == 0:
    print("❌ Error: The sheet 'Active Store' has no columns!")
    exit(1)

# Clean column names to match your schema (lowercase, replace spaces with underscores)
# Convert column names to strings first to handle any non-string column names
df.columns = [str(col).lower().replace(" ", "_").strip() for col in df.columns]

# Map common column name variations to schema column names
column_mapping = {
    'customer_account_name': 'customer_account_name',
    'customer name': 'customer_account_name',
    'account_name': 'customer_account_name',
    'account name': 'customer_account_name',
    # Handle month variations (e.g., "Apr 2024", "APR 2024", "april_2024")
    'apr 2024': 'apr_2024', 'april 2024': 'apr_2024',
    'aug 2024': 'aug_2024', 'august 2024': 'aug_2024',
    'dec 2024': 'dec_2024', 'december 2024': 'dec_2024',
    'feb 2024': 'feb_2024', 'february 2024': 'feb_2024',
    'jan 2024': 'jan_2024', 'january 2024': 'jan_2024',
    'jul 2024': 'jul_2024', 'july 2024': 'jul_2024',
    'jun 2024': 'jun_2024', 'june 2024': 'jun_2024',
    'mar 2024': 'mar_2024', 'march 2024': 'mar_2024',
    'may 2024': 'may_2024',
    'nov 2024': 'nov_2024', 'november 2024': 'nov_2024',
    'oct 2024': 'oct_2024', 'october 2024': 'oct_2024',
    'sep 2024': 'sep_2024', 'september 2024': 'sep_2024',
    'total 2024': 'total_2024',
    # 2025 months
    'apr 2025': 'apr_2025', 'april 2025': 'apr_2025',
    'aug 2025': 'aug_2025', 'august 2025': 'aug_2025',
    'dec 2025': 'dec_2025', 'december 2025': 'dec_2025',
    'feb 2025': 'feb_2025', 'february 2025': 'feb_2025',
    'jan 2025': 'jan_2025', 'january 2025': 'jan_2025',
    'jul 2025': 'jul_2025', 'july 2025': 'jul_2025',
    'jun 2025': 'jun_2025', 'june 2025': 'jun_2025',
    'mar 2025': 'mar_2025', 'march 2025': 'mar_2025',
    'may 2025': 'may_2025',
    'nov 2025': 'nov_2025', 'november 2025': 'nov_2025',
    'oct 2025': 'oct_2025', 'october 2025': 'oct_2025',
    'sep 2025': 'sep_2025', 'september 2025': 'sep_2025',
    'total 2025': 'total_2025',
    'grand_total': 'grand_total',
    'grand total': 'grand_total',
    'total': 'grand_total',
}

# Apply column name mapping
for old_name, new_name in column_mapping.items():
    if old_name in df.columns and new_name not in df.columns:
        df.rename(columns={old_name: new_name}, inplace=True)

# Filter to only include columns that exist in the database schema
available_columns = [col for col in SCHEMA_COLUMNS if col in df.columns]
missing_columns = [col for col in SCHEMA_COLUMNS if col not in df.columns]

if missing_columns:
    print(f"⚠️  Warning: The following schema columns are missing from Excel: {', '.join(missing_columns)}")

# Ensure customer_account_name exists (it's required as PRIMARY KEY)
if 'customer_account_name' not in df.columns:
    print("❌ Error: 'customer_account_name' column is required but not found in Excel!")
    print(f"Available columns: {', '.join(df.columns)}")
    exit(1)

if not available_columns:
    print("❌ Error: No matching columns found between Excel and database schema!")
    exit(1)

print(f"✓ Found {len(available_columns)} matching columns: {', '.join(available_columns)}")
df = df[available_columns]  # Keep only schema columns

# Convert integer columns (handle float to int conversion properly)
def convert_to_int64(series):
    """Convert a series to nullable Int64, handling float values and NaN"""
    # Convert to numeric first (handles strings, etc.)
    numeric = pd.to_numeric(series, errors='coerce')
    # Round to nearest integer (handles any decimal values)
    numeric = numeric.round()
    # Convert to Int64 (nullable integer type)
    return numeric.astype('Int64')

# Convert all numeric columns (except customer_account_name) to integers
for col in df.columns:
    if col != 'customer_account_name':
        df[col] = convert_to_int64(df[col])

# Replace NaN/NaT with None for proper JSON serialization
df = df.where(pd.notnull(df), None)

# Convert DataFrame to list of dictionaries
records = df.to_dict('records')

# Additional cleanup: handle NaN/NA values and convert pandas nullable integers
for record in records:
    for key, value in record.items():
        if pd.isna(value) or value == 'nan' or value == 'NaT' or str(value) == '<NA>':
            record[key] = None
        # Convert pandas nullable integer to Python int or None
        elif isinstance(value, (int, float)) and not pd.isna(value):
            # Convert to int if it's a whole number
            if isinstance(value, float) and value.is_integer():
                record[key] = int(value)
            elif isinstance(value, int):
                record[key] = value
        # Ensure customer_account_name is a string
        elif key == 'customer_account_name' and value is not None:
            record[key] = str(value).strip()

# Remove any records with None customer_account_name (invalid primary key)
records = [r for r in records if r.get('customer_account_name') is not None and r.get('customer_account_name') != '']

if not records:
    print("❌ Error: No valid records to insert (all records have empty customer_account_name)")
    exit(1)

total_batches = (len(records) + 999) // 1000  # Calculate total batches

# Insert in batches (Supabase has limits on batch size, typically 1000 rows)
batch_size = 1000
inserted_count = 0
failed_batches = 0

print(f"\nStarting data ingestion ({total_batches} batches)...")
for i in range(0, len(records), batch_size):
    batch = records[i:i + batch_size]
    batch_num = i//batch_size + 1
    try:
        supabase.table("active_store").insert(batch).execute()
        inserted_count += len(batch)
        print(f"✓ Inserted batch {batch_num}/{total_batches} ({len(batch)} rows) - Total: {inserted_count} rows")
    except Exception as e:
        failed_batches += 1
        print(f"✗ Error inserting batch {batch_num}/{total_batches}: {e}")
        # Print first record of failed batch for debugging
        if batch:
            print(f"  Sample record keys: {list(batch[0].keys())}")

print(f"\n{'='*50}")
if failed_batches == 0:
    print(f"✅ Data ingested successfully! Total rows inserted: {inserted_count}")
else:
    print(f"⚠️  Completed with errors. Inserted: {inserted_count} rows, Failed batches: {failed_batches}")
print(f"{'='*50}")

