# Sales Analytics AI Application

An AI-powered sales data analytics platform with natural language querying capabilities. Ask questions in plain English and get SQL-backed insights with automatic chart generation, plus document analysis for Purchase Orders and Proforma Invoices.

## Features

- 🤖 Natural language to SQL conversion using Google Gemini AI
- 📊 Automatic chart generation for data visualization
- 📄 Document analysis mode for Purchase Orders and Proforma Invoices comparison
- 🔄 Streaming responses for real-time feedback
- 💾 PostgreSQL database via Supabase
- ⚡ FastAPI backend with CORS support
- 🎨 Modern Next.js frontend with TypeScript

---

## Backend Setup

### Prerequisites

- Python 3.8 or higher
- A Supabase account 
- Google Gemini API key 

### Step 1: Create Virtual Environment

```bash
# Navigate to project root
cd sales_project

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root directory with your Supabase and Gemini API credentials:

```bash
# .env file
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key
```

**How to get these credentials:**

**Supabase:**
1. Go to [supabase.com](https://supabase.com) and sign in
2. Create a new project or select an existing one
3. Go to Settings → API
4. Copy the "Project URL" as `SUPABASE_URL`
5. Copy the "anon public" key as `SUPABASE_KEY`

**Gemini API:**
1. Visit [Google AI Studio](https://ai.google.dev/)
2. Click "Get API Key"
3. Create a new API key or use an existing one
4. Copy it as `GEMINI_API_KEY`

### Step 4: Create Database Tables in Supabase

1. Go to your Supabase Dashboard
2. Navigate to **SQL Editor**
3. Click **New Query**
4. Copy and paste the contents of `setup_supabase_rpc.sql`
5. Click **Run** to execute the SQL

This will create:
- The `execute_sql` RPC function (allows the AI to run safe SELECT queries)
- The `sales_transactions` table (for storing sales data) again open sql editor with new snippet paste below code for table generation

```sql
CREATE TABLE public.sales_transactions (
    id BIGSERIAL PRIMARY KEY,
    master_distributor TEXT,
    distributor TEXT,
    line_of_business TEXT,
    supplier TEXT,
    agency TEXT,
    category TEXT,
    segment TEXT,
    brand TEXT,
    sub_brand TEXT,
    country TEXT,
    city TEXT,
    area TEXT,
    retailer_group TEXT,
    retailer_sub_group TEXT,
    channel TEXT,
    sub_channel TEXT,
    salesman TEXT,
    order_number TEXT,
    customer TEXT,
    customer_account_name TEXT,
    customer_account_number TEXT,
    item TEXT,
    item_description TEXT,
    promo_item BOOLEAN,
    foc_nonfoc TEXT,
    unit_selling_price NUMERIC,
    invoice_number TEXT,
    invoice_date DATE,
    year INTEGER,
    month TEXT,
    invoiced_quantity INTEGER,
    value NUMERIC
);
```

### Step 5: Ingest Data

Place your sales data Excel file in the `data/` folder as `sales.xlsx` (with a sheet named "Sales 2022 Onwards").

Then run the data ingestion script:

```bash
python src/data_pipeline.py
```

This will:
- Read the Excel file from `data/sales.xlsx`
- Transform and clean the data
- Upload it to your Supabase `sales_transactions` table in batches
- Show progress and confirm successful ingestion

**Note:** The script will prompt you if data already exists in the table.

### Step 6: Start the Backend Server

```bash
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Chat Endpoint:** http://localhost:8000/chat

**Backend is now running!** ✅

---

## Frontend Setup

### Prerequisites

- Node.js 16 or higher
- npm or yarn package manager

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Start Development Server

```bash
npm run dev
```

The frontend will be available at: **http://localhost:3000**

**Frontend is now running!** ✅

---

## Usage

1. Open your browser and go to http://localhost:3000
2. You'll see the Sales Analytics chat interface
3. Choose between two modes:
   - **Sales Data Analysis:** Ask questions about your sales data (e.g., "What are the top 5 brands by revenue?")
   - **Document Analysis:** Compare Purchase Orders with Proforma Invoices (e.g., "What are the differences between PO and PI?")
4. Type your question and press Enter or click Send
5. The AI will generate SQL, execute it, create charts (if applicable), and provide a natural language answer


---

## Project Structure

```
sales_project/
├── src/                    # Backend source code
│   ├── app.py             # FastAPI application & endpoints
│   ├── llm.py             # Gemini AI integration
│   ├── query.py           # SQL execution via Supabase
│   ├── models.py          # Database schema definitions
│   ├── database.py        # Supabase client setup
│   └── data_pipeline.py   # Data ingestion script
├── frontend/              # Next.js frontend
│   ├── app/              # Next.js 13+ app directory
│   ├── components/       # React components
│   ├── lib/              # Utility functions & API client
│   └── types/            # TypeScript type definitions
├── data/                 # Excel data files
│   └── sales.xlsx
├── pdf_data/             # Markdown versions of documents
│   ├── Purchase_Order_2025-12-12.md
│   └── Proforma_Invoice_2025-12-12.md
├── requirements.txt      # Python dependencies
├── setup_supabase_rpc.sql # Database setup script
└── README.md            # This file
```

---

## API Endpoints

### `POST /chat`

Main chat endpoint for querying sales data or analyzing documents.

**Request Body:**
```json
{
  "question": "What are the top 5 brands?",
  "stream": false,
  "document_mode": false
}
```

**Response (SQL Mode):**
```json
{
  "question": "What are the top 5 brands?",
  "generated_sql": "SELECT brand, SUM(value) as total_sales FROM sales_transactions GROUP BY brand ORDER BY total_sales DESC LIMIT 5",
  "data": [...],
  "answer": "Based on the data...",
  "chart_image": "base64_encoded_image",
  "status": "success"
}
```

**Response (Document Mode):**
```json
{
  "question": "Compare PO and PI",
  "answer": "The main differences are...",
  "status": "success",
  "mode": "document_analysis"
}
```

### Streaming Endpoint

Set `"stream": true` in the request to get real-time streaming responses with step-by-step progress updates.

---



## Technologies Used

**Backend:**
- FastAPI - Modern Python web framework
- Google Gemini AI - Natural language processing and SQL generation
- Supabase (PostgreSQL) - Database and real-time features
- Pandas - Data manipulation
- Matplotlib - Chart generation
- Uvicorn - ASGI server

**Frontend:**
- Next.js 14 - React framework
- TypeScript - Type-safe JavaScript
- Tailwind CSS - Utility-first CSS
- Shadcn/ui - UI component library

---

## License

This project is for internal use.

---



**Happy Analyzing! 📊🚀**

