# src/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from .llm import generate_sql, generate_final_answer, generate_final_answer_stream, generate_sql_stream, needs_chart, generate_chart_image, analyze_documents_stream, analyze_documents
from .query import execute_sql
import json
import base64
import os
from pathlib import Path

app = FastAPI(title="Sales Analytics API", description="AI-powered sales data query API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class ChatRequest(BaseModel):
    question: str
    stream: bool = False
    document_mode: bool = False


def load_md_documents():
    """Load Purchase Order and Proforma Invoice markdown documents"""
    # Get the project root directory (parent of src)
    project_root = Path(__file__).parent.parent
    pdf_data_dir = project_root / "pdf_data"
    
    po_path = pdf_data_dir / "Purchase_Order_2025-12-12.md"
    pi_path = pdf_data_dir / "Proforma_Invoice_2025-12-12.md"
    
    try:
        with open(po_path, 'r', encoding='utf-8') as f:
            po_content = f.read()
        with open(pi_path, 'r', encoding='utf-8') as f:
            pi_content = f.read()
        return po_content, pi_content
    except Exception as e:
        raise Exception(f"Failed to load MD documents: {str(e)}")


@app.get("/")
def root():
    return {"message": "Sales Analytics API is running", "endpoints": ["/chat", "/chat/stream", "/docs"]}

@app.post("/chat")
def chat(request: ChatRequest):
    """
    Chat endpoint that takes a natural language question.
    Routes to either SQL analysis (sales data) or document analysis (PO/PI comparison).
    """
    try:
        # DOCUMENT MODE: Analyze Purchase Orders and Proforma Invoices
        if request.document_mode:
            po_content, pi_content = load_md_documents()
            
            if request.stream:
                # Streaming document analysis
                def generate():
                    try:
                        yield f"data: {json.dumps({'type': 'status', 'step': 'generating_answer', 'message': 'Analyzing documents...'})}\n\n"
                        
                        for chunk in analyze_documents_stream(request.question, po_content, pi_content):
                            yield f"data: {json.dumps({'type': 'answer_chunk', 'content': chunk})}\n\n"
                        
                        yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    except Exception as e:
                        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
                
                return StreamingResponse(
                    generate(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Accel-Buffering": "no",
                    }
                )
            else:
                # Non-streaming document analysis
                answer = analyze_documents(request.question, po_content, pi_content)
                return {
                    "question": request.question,
                    "answer": answer,
                    "status": "success",
                    "mode": "document_analysis"
                }
        
        # SQL MODE: Original sales data analysis
        if request.stream:
            # Return streaming response with step-by-step flow
            def generate():
                try:
                    # Step 1: Generate SQL (streaming)
                    yield f"data: {json.dumps({'type': 'status', 'step': 'generating_sql', 'message': 'Generating SQL query...'})}\n\n"
                    
                    sql = ""
                    for chunk in generate_sql_stream(request.question):
                        sql += chunk
                        # Clean chunk before sending (remove markdown markers)
                        clean_chunk = chunk.replace("```sql", "").replace("```", "")
                        if clean_chunk:
                            yield f"data: {json.dumps({'type': 'sql_chunk', 'content': clean_chunk})}\n\n"
                    
                    # Final cleanup of SQL
                    sql = sql.strip().replace("```sql", "").replace("```", "").strip()
                    if sql.endswith(";"):
                        sql = sql[:-1]
                    
                    # Send complete SQL
                    yield f"data: {json.dumps({'type': 'sql_complete', 'sql': sql})}\n\n"
                    
                    # Step 2: Execute SQL
                    yield f"data: {json.dumps({'type': 'status', 'step': 'executing_sql', 'message': 'Executing SQL query...'})}\n\n"
                    try:
                        data = execute_sql(sql)
                        if data is None:
                            data = []
                        yield f"data: {json.dumps({'type': 'sql_result', 'data': data, 'data_count': len(data) if isinstance(data, list) else 0})}\n\n"
                        
                        # Step 3: Check if chart is needed
                        if needs_chart(request.question):
                            yield f"data: {json.dumps({'type': 'status', 'step': 'generating_chart', 'message': 'Generating chart...'})}\n\n"
                            try:
                                chart_bytes = generate_chart_image(request.question, sql, data)
                                # Convert image bytes to base64 for transmission
                                chart_base64 = base64.b64encode(chart_bytes).decode('utf-8')
                                yield f"data: {json.dumps({'type': 'chart_image', 'image': chart_base64})}\n\n"
                            except Exception as chart_error:
                                print(f"Chart generation failed: {chart_error}")
                                yield f"data: {json.dumps({'type': 'chart_error', 'error': str(chart_error)})}\n\n"
                        
                        # Step 4: Generate final answer (streaming)
                        yield f"data: {json.dumps({'type': 'status', 'step': 'generating_answer', 'message': 'Generating answer...'})}\n\n"
                        
                        for chunk in generate_final_answer_stream(request.question, sql, data):
                            yield f"data: {json.dumps({'type': 'answer_chunk', 'content': chunk})}\n\n"
                    except Exception as sql_error:
                        # If SQL execution fails, still try to generate an explanation
                        error_msg = str(sql_error)
                        yield f"data: {json.dumps({'type': 'sql_error', 'error': error_msg})}\n\n"
                        
                        # Generate answer explaining the error
                        yield f"data: {json.dumps({'type': 'status', 'step': 'generating_answer', 'message': 'Generating answer...'})}\n\n"
                        try:
                            for chunk in generate_final_answer_stream(request.question, sql, []):
                                yield f"data: {json.dumps({'type': 'answer_chunk', 'content': chunk})}\n\n"
                        except Exception as answer_error:
                            yield f"data: {json.dumps({'type': 'answer_chunk', 'content': f'SQL execution failed: {error_msg}'})}\n\n"
                    
                    # Send completion
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                }
            )
        else:
            # Non-streaming response
            sql = generate_sql(request.question)
            data = execute_sql(sql)
            answer = generate_final_answer(request.question, sql, data)
            
            # Check if chart is needed
            chart_base64 = None
            if needs_chart(request.question):
                try:
                    chart_bytes = generate_chart_image(request.question, sql, data)
                    chart_base64 = base64.b64encode(chart_bytes).decode('utf-8')
                except Exception as chart_error:
                    print(f"Chart generation failed: {chart_error}")
            
            return {
                "question": request.question,
                "generated_sql": sql,
                "data": data,
                "answer": answer,
                "chart_image": chart_base64,
                "status": "success"
            }
    except Exception as e:
        return {
            "question": request.question,
            "error": str(e),
            "status": "error"
        }
