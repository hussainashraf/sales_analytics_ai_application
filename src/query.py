# query.py
from .database import supabase
import re

def execute_sql(sql: str) -> list:
    """
    Execute SQL query using Supabase RPC function.
    This allows executing raw SQL queries with security checks.
    """
    try:
        sql = sql.strip()
        print(f"Executing SQL: {sql}")
        
        # Security: Block dangerous SQL operations (but allow CURRENT_DATE, etc.)
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE']
        sql_upper = sql.upper()
        
        # Use word boundaries to avoid false positives (e.g., CURRENT_DATE contains CREATE)
        import re
        for keyword in dangerous_keywords:
            if re.search(rf'\b{keyword}\b', sql_upper):
                raise ValueError(f"SQL operation '{keyword}' is not allowed for security reasons")
        
        # Check for CREATE with specific objects (but allow CURRENT_DATE, CURRENT_TIMESTAMP)
        if re.search(r'\bCREATE\s+(TABLE|DATABASE|FUNCTION|INDEX|VIEW)', sql_upper):
            raise ValueError("CREATE operations are not allowed for security reasons")
        
        # Use Supabase RPC to execute raw SQL
        # Note: You need to create this RPC function in your Supabase database
        # SQL function to create in Supabase:
        # CREATE OR REPLACE FUNCTION execute_sql(query text)
        # RETURNS json AS $$
        # BEGIN
        #   RETURN (SELECT json_agg(t) FROM (EXECUTE query) t);
        # END;
        # $$ LANGUAGE plpgsql SECURITY DEFINER;
        
        try:
            # Call the RPC function with proper parameter name
            response = supabase.rpc('execute_sql', {'query': sql}).execute()
            print(f"RPC response status: {response}")
            
            # Handle the response data
            result = response.data if hasattr(response, 'data') else []
            
            # If result is None, return empty list
            if result is None:
                print("Query returned no results (NULL)")
                return []
            
            print(f"Query result: {len(result) if isinstance(result, list) else 'single'} rows")
            return result if result else []
            
        except Exception as rpc_error:
            error_msg = str(rpc_error)
            print(f"RPC Error: {error_msg}")
            
            # Check if it's an RPC not found error
            if 'execute_sql' in error_msg.lower() or 'function' in error_msg.lower():
                print("RPC function 'execute_sql' not found. Please run the setup SQL in Supabase.")
                raise Exception(f"RPC function 'execute_sql' not found. Please run setup_supabase_rpc.sql in your Supabase SQL Editor. Error: {error_msg}")
            
            # For other errors, don't use fallback as it's unreliable for complex queries
            raise Exception(f"Error calling RPC: {error_msg}")
        
    except Exception as e:
        error_msg = f"Error executing SQL: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)

def _execute_sql_fallback(sql: str) -> list:
    """
    Fallback method using basic SQL parsing when RPC is not available.
    Only handles simple SELECT queries.
    """
    print("Using fallback SQL execution (limited functionality)")
    
    try:
        # Basic SQL parsing - extract table name
        table_match = re.search(r'FROM\s+(\w+)', sql, re.IGNORECASE)
        if not table_match:
            raise ValueError("Could not parse table name from SQL")
        
        table_name = table_match.group(1).lower()
        
        # For simple queries, just return all data from table
        query = supabase.table(table_name).select("*").limit(100)
        
        response = query.execute()
        result = response.data if hasattr(response, 'data') else []
        print(f"Fallback query returned {len(result)} rows")
        return result
        
    except Exception as e:
        raise Exception(f"Fallback SQL execution failed: {str(e)}")

def total_sales(brand, start_date, end_date):
    """Legacy function - kept for backward compatibility"""
    query = f"""
        SELECT SUM(value) AS total_sales
        FROM sales_transactions
        WHERE brand = '{brand}'
        AND invoice_date BETWEEN '{start_date}' AND '{end_date}'
    """
    return execute_sql(query)
