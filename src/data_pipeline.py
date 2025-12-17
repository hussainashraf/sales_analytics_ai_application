# ingest.py
import os
import pandas as pd
from datetime import datetime
from database import supabase

# Get the project root directory (parent of src/)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
excel_path = os.path.join(project_root, "data", "sales.xlsx")

# Define the columns that exist in the sales_transactions table (excluding id which is auto-generated)
SCHEMA_COLUMNS = [
    # Distributor hierarchy
    'master_distributor', 'distributor',
    # Business structure
    'line_of_business', 'supplier', 'agency',
    # Product hierarchy
    'category', 'segment', 'brand', 'sub_brand',
    # Geography
    'country', 'city', 'area',
    # Retail structure
    'retailer_group', 'retailer_sub_group', 'channel', 'sub_channel',
    # Sales team
    'salesman',
    # Order & customer details
    'order_number', 'customer', 'customer_account_name', 'customer_account_number',
    # Item details
    'item', 'item_description', 'promo_item', 'foc_nonfoc',
    # Pricing & invoice
    'unit_selling_price', 'invoice_number', 'invoice_date',
    # Time dimensions
    'year', 'month',
    # Metrics
    'invoiced_quantity', 'value'
]

# Check if data already exists in the table
try:
    existing_data = supabase.table("sales_transactions").select("id", count="exact").limit(1).execute()
    if existing_data.count and existing_data.count > 0:
        print(f"⚠️  Warning: Table 'sales_transactions' already contains {existing_data.count} records.")
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
print("Reading sheet: 'Sales 2022 Onwards'")
df = pd.read_excel(excel_path, sheet_name="Sales 2022 Onwards")
print(f"Loaded {len(df)} rows from Excel")

# Clean column names to match your schema
df.columns = df.columns.str.lower().str.replace(" ", "_")

# Map common column name variations to schema column names
column_mapping = {
    'salesmen': 'salesman',  # Handle plural form
    'sales_men': 'salesman',
    'quantity': 'invoiced_quantity',  # Map old column name to new
    'unit_price': 'unit_selling_price',  # Map old column name to new
    'line_total': 'value',  # Map old column name to new
    'invoice_id': 'invoice_number',  # Map old column name to new
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

if not available_columns:
    print("❌ Error: No matching columns found between Excel and database schema!")
    exit(1)

print(f"✓ Found {len(available_columns)} matching columns: {', '.join(available_columns)}")
df = df[available_columns]  # Keep only schema columns

# Convert datetime columns to strings (for JSON serialization)
# Suppress warnings for datetime parsing
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

for col in df.columns:
    if col == 'invoice_date' or 'date' in col.lower():
        # Convert datetime to date string (YYYY-MM-DD format)
        df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=False).dt.strftime('%Y-%m-%d')
        # Replace NaT (Not a Time) with None
        df[col] = df[col].replace('NaT', None).replace('nan', None)

# Replace NaN/NaT with None for proper JSON serialization
df = df.where(pd.notnull(df), None)

# Convert boolean columns properly (handle string booleans too)
if 'promo_item' in df.columns:
    if df['promo_item'].dtype == 'bool':
        # Already boolean, just ensure None handling
        df['promo_item'] = df['promo_item'].where(pd.notnull(df['promo_item']), None)
    else:
        # Convert string/other types to boolean
        def convert_to_bool(val):
            if pd.isna(val) or val is None:
                return None
            val_str = str(val).lower().strip()
            if val_str in ['true', 'yes', '1', 'y']:
                return True
            elif val_str in ['false', 'no', '0', 'n']:
                return False
            return None
        df['promo_item'] = df['promo_item'].apply(convert_to_bool)

# Convert integer columns (handle float to int conversion properly)
def convert_to_int64(series):
    """Convert a series to nullable Int64, handling float values and NaN"""
    # Convert to numeric first (handles strings, etc.)
    numeric = pd.to_numeric(series, errors='coerce')
    # Round to nearest integer (handles any decimal values)
    numeric = numeric.round()
    # Convert to Int64 (nullable integer type)
    return numeric.astype('Int64')

if 'invoiced_quantity' in df.columns:
    df['invoiced_quantity'] = convert_to_int64(df['invoiced_quantity'])
if 'year' in df.columns:
    df['year'] = convert_to_int64(df['year'])
# month is kept as text (as it comes from Excel) - no conversion needed

# Replace NaN/NaT with None for proper JSON serialization
df = df.where(pd.notnull(df), None)

# Convert DataFrame to list of dictionaries
records = df.to_dict('records')

# Additional cleanup: ensure all datetime objects are strings and handle NaN/NA values
for record in records:
    for key, value in record.items():
        if isinstance(value, datetime):
            record[key] = value.strftime('%Y-%m-%d')
        elif pd.isna(value) or value == 'nan' or value == 'NaT' or str(value) == '<NA>':
            record[key] = None
        # Convert pandas nullable integer to Python int or None
        elif isinstance(value, (int, float)) and not pd.isna(value):
            # Convert to int if it's a whole number, otherwise keep as float
            if isinstance(value, float) and value.is_integer():
                record[key] = int(value)
            elif isinstance(value, int):
                record[key] = value
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
        supabase.table("sales_transactions").insert(batch).execute()
        inserted_count += len(batch)
        print(f"✓ Inserted batch {batch_num}/{total_batches} ({len(batch)} rows) - Total: {inserted_count} rows")
    except Exception as e:
        failed_batches += 1
        print(f"✗ Error inserting batch {batch_num}/{total_batches}: {e}")

print(f"\n{'='*50}")
if failed_batches == 0:
    print(f"✅ Data ingested successfully! Total rows inserted: {inserted_count}")
else:
    print(f"⚠️  Completed with errors. Inserted: {inserted_count} rows, Failed batches: {failed_batches}")
print(f"{'='*50}")