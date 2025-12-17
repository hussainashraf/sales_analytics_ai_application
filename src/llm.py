import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Initialize Gemini client
_api_key = os.getenv("GEMINI_API_KEY")
if not _api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables or .env file")

client = genai.Client(api_key=_api_key)
print("Gemini client initialized successfully")

SQL_SYSTEM_PROMPT = """
You are an AI data analyst that generates STRICT, EXECUTABLE PostgreSQL SQL.

Database: PostgreSQL (Supabase)
Table name: sales_transactions

====================
SCHEMA (THIS IS FINAL)
====================

Available columns ONLY (do not invent anything):

master_distributor, distributor,
line_of_business, supplier, agency,
category, segment, brand, sub_brand,
country, city, area,
retailer_group, retailer_sub_group,
channel, sub_channel,
salesman,
order_number, customer,
customer_account_name, customer_account_number,
item, item_description,
promo_item, foc_nonfoc,
unit_selling_price,
invoice_number, invoice_date,
year (INTEGER),
month (INTEGER),
invoiced_quantity (INTEGER),
value (NUMERIC)

====================
CRITICAL RULES (MANDATORY)
====================

1. Use ONLY the columns listed above.
2. The ONLY time columns are:
   - year (INTEGER)
   - month (INTEGER)
3. NEVER invent or use columns such as:
   year_period, month_year, period, date_key, yearmonth, ym
4. If grouping by time:
   - Yearly → GROUP BY year
   - Monthly → GROUP BY year, month
5. If filtering by time:
   - Example: WHERE year = 2024 AND month = 12
6. Use SUM(value) for total sales or revenue.
7. Active stores = COUNT(DISTINCT customer_account_number).
8. Generate ONLY read-only SQL:
   - Allowed: SELECT, WITH
   - Forbidden: DELETE, UPDATE, INSERT, DROP, ALTER, TRUNCATE, CREATE
9. DO NOT include semicolons (;) at the end of the SQL.
10. Do NOT use aliases or columns that are not explicitly defined above.
11. The SQL MUST be executable directly in Supabase PostgreSQL.
12. If the user asks for something that cannot be answered using this schema,
    return the BEST POSSIBLE query using available columns — do NOT invent columns.

====================
OUTPUT FORMAT
====================

- Return ONLY the SQL query
"""



def generate_sql_stream(question: str):
    """Generate SQL query with streaming support - single function for both streaming and non-streaming"""
    prompt = f"""
{SQL_SYSTEM_PROMPT}

User Question:
{question}

Return ONLY valid SQL.
"""
    response = client.models.generate_content_stream(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    
    for chunk in response:
        if hasattr(chunk, 'text') and chunk.text:
            yield chunk.text
        elif hasattr(chunk, 'candidates') and chunk.candidates:
            # Handle different response formats
            for candidate in chunk.candidates:
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            yield part.text

def generate_sql(question: str) -> str:
    """Generate SQL query from natural language question - uses stream function internally"""
    print(f"Generating SQL for question: {question}")
    
    sql = ""
    for chunk in generate_sql_stream(question):
        sql += chunk

    sql = sql.strip()
    # remove markdown if Gemini adds it
    sql = sql.replace("```sql", "").replace("```", "").strip()
    if sql.endswith(";"):
        sql = sql[:-1]
    print(f"Generated SQL: {sql}")
    return sql


def generate_final_answer_stream(question: str, sql: str, data: list):
    """Generate human-readable answer with streaming support - single function for both streaming and non-streaming"""
    # Limit data size for the prompt (avoid token limits)
    data_preview = data[:10] if len(data) > 10 else data
    data_summary = f"Showing {len(data_preview)} of {len(data)} results" if len(data) > 10 else f"{len(data)} results"
    
    prompt = f"""
User Question:
{question}

SQL Query:
{sql}

SQL Result ({data_summary}):
{data_preview}

Explain the result in simple business language. If there are many results, summarize the key findings.
"""
    response = client.models.generate_content_stream(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    
    for chunk in response:
        if hasattr(chunk, 'text') and chunk.text:
            yield chunk.text
        elif hasattr(chunk, 'candidates') and chunk.candidates:
            for candidate in chunk.candidates:
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            yield part.text

def generate_final_answer(question: str, sql: str, data: list) -> str:
    """Generate human-readable answer from SQL query and results - uses stream function internally"""
    answer = ""
    for chunk in generate_final_answer_stream(question, sql, data):
        answer += chunk
    
    answer = answer.strip()
    print(f"Generated answer: {answer}")
    return answer

def needs_chart(question: str) -> bool:
    """Determine if the user's question requires a chart/visualization"""
    chart_keywords = [
        'chart', 'graph', 'plot', 'visualize', 'visualization', 'show me', 
        'display', 'trend', 'comparison', 'compare', 'distribution',
        'bar chart', 'line chart', 'pie chart', 'histogram', 'scatter'
    ]
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in chart_keywords)

def generate_chart_image(question: str, sql: str, data: list) -> bytes:
    """Generate a chart image using Gemini's image generation capability"""
    # Limit data size for the prompt
    data_preview = data[:20] if len(data) > 20 else data
    
    # Create a detailed prompt for chart generation
    chart_prompt = f"""
Create a professional, business-ready chart/visualization for the following data analysis:

User Question: {question}

SQL Query Used: {sql}

Data Results (first 20 rows):
{data_preview}

Requirements:
- Create a clear, professional chart that best represents this data
- Use appropriate chart type (bar, line, pie, etc.) based on the data
- Include proper labels, title, and legend
- Use a clean, modern design with good color scheme
- Make it suitable for a business presentation
- Include data values on the chart where appropriate
"""
    
    print(f"Generating chart for question: {question}")
    
    try:
        response = client.models.generate_content(
            model='imagen-4.0-generate-001',
            contents=[chart_prompt],
        )
        
        # Extract image from response
        for part in response.parts:
            if part.inline_data is not None:
                # Get the image bytes directly
                image_bytes = part.inline_data.data
                print(f"Chart generated successfully, size: {len(image_bytes)} bytes")
                return image_bytes
        
        raise ValueError("No image generated in response")
        
    except Exception as e:
        print(f"Error generating chart: {e}")
        raise Exception(f"Failed to generate chart: {str(e)}")


# Document Analysis System Prompt
DOCUMENT_ANALYSIS_PROMPT = """
You are a document comparison expert specializing in analyzing Purchase Orders (PO) and Proforma Invoices (PI).

Your task is to:
1. Compare quantities, prices, and values between PO and PI
2. Identify discrepancies and mismatches
3. Calculate total differences
4. Provide alerts and suggestions for any issues found

Always provide structured, clear analysis with specific details about what differs and by how much.
"""


def analyze_documents_stream(question: str, po_content: str, pi_content: str):
    """Analyze Purchase Order and Proforma Invoice documents with streaming support"""
    prompt = f"""
{DOCUMENT_ANALYSIS_PROMPT}

Here are the two documents to analyze:

PURCHASE ORDER:
{po_content}

PROFORMA INVOICE:
{pi_content}

User Question:
{question}

Please analyze these documents and provide:
1. Item-by-item comparison (SKU, description, quantities, prices)
2. Highlight any mismatches in quantity or price
3. Calculate value differences
4. Summary of total order value vs invoice value
5. Alerts for significant discrepancies
6. Suggestions for resolving issues

Format your response in a clear, structured way with tables where appropriate.
"""
    
    response = client.models.generate_content_stream(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    
    for chunk in response:
        if hasattr(chunk, 'text') and chunk.text:
            yield chunk.text
        elif hasattr(chunk, 'candidates') and chunk.candidates:
            for candidate in chunk.candidates:
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            yield part.text


def analyze_documents(question: str, po_content: str, pi_content: str) -> str:
    """Analyze Purchase Order and Proforma Invoice documents (non-streaming)"""
    answer = ""
    for chunk in analyze_documents_stream(question, po_content, pi_content):
        answer += chunk
    
    answer = answer.strip()
    print(f"Generated document analysis: {answer[:200]}...")
    return answer