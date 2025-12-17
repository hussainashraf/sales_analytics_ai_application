-- SQL Setup for Supabase RPC Function
-- Run this in your Supabase SQL Editor (Dashboard -> SQL Editor -> New Query)

-- This function allows executing raw SQL queries from the application
-- SECURITY NOTE: This should only be used for SELECT queries in production

-- Drop existing function if it exists (to ensure clean setup)
DROP FUNCTION IF EXISTS public.execute_sql(text);

CREATE OR REPLACE FUNCTION public.execute_sql(query text)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result json;
  cleaned_query text;
BEGIN
  -- Clean the query (remove extra whitespace, newlines)
  cleaned_query := regexp_replace(trim(query), '\s+', ' ', 'g');
  
  -- Allow SELECT queries and WITH clauses (CTEs)
  IF NOT (cleaned_query ~* '^(SELECT|WITH)') THEN
    RAISE EXCEPTION 'Only SELECT queries or WITH clauses are allowed. Query starts with: %', substring(cleaned_query from 1 for 50);
  END IF;
  
  -- Prevent dangerous operations (check for these keywords anywhere in the query)
  IF cleaned_query ~* '\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|GRANT|REVOKE)\b' THEN
    RAISE EXCEPTION 'Dangerous SQL operations are not allowed';
  END IF;
  
  -- Prevent CREATE (but allow CURRENT_DATE, CURRENT_TIMESTAMP functions)
  IF cleaned_query ~* '\bCREATE\s+(TABLE|DATABASE|FUNCTION|INDEX|VIEW)' THEN
    RAISE EXCEPTION 'CREATE operations are not allowed';
  END IF;
  
  -- Execute the query and return as JSON array
  EXECUTE format('SELECT json_agg(t) FROM (%s) t', query) INTO result;
  
  -- Return empty array if no results
  RETURN COALESCE(result, '[]'::json);
END;
$$;

-- Grant execute permission to authenticated and anon users
GRANT EXECUTE ON FUNCTION public.execute_sql(text) TO authenticated, anon;

-- Test the function with various queries
-- Test 1: Simple SELECT
SELECT public.execute_sql('SELECT brand, SUM(value) as total_sales FROM sales_transactions GROUP BY brand LIMIT 5');

-- Test 2: Query with CURRENT_DATE
SELECT public.execute_sql('SELECT EXTRACT(YEAR FROM CURRENT_DATE) as current_year');

-- Test 3: WITH clause (CTE)
SELECT public.execute_sql('WITH summary AS (SELECT brand, SUM(value) as total FROM sales_transactions GROUP BY brand) SELECT * FROM summary LIMIT 5');

