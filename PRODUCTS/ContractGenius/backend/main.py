"""
ContractGenius - AI-Powered Legal Contract Analyzer
Backend API using FastAPI
"""

import os
import io
import json
import uuid
import tempfile
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import openai
from dotenv import load_dotenv
import PyPDF2
import docx
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import fitz  # PyMuPDF for PDF annotation

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ContractGenius API",
    description="AI-Powered Legal Contract Analysis",
    version="1.0.0"
)

# CORS configuration for GitHub Pages frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your GitHub Pages domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# In-memory storage for contracts (use database in production)
contracts_db: Dict[str, Dict] = {}

# ==================== Pydantic Models ====================

class ContractAnalysis(BaseModel):
    id: str
    filename: str
    file_type: str
    upload_date: str
    text_content: str
    analysis: Dict[str, Any]
    risk_score: int
    key_terms: List[Dict]
    risks: List[Dict]
    obligations: List[Dict]
    unfair_clauses: List[Dict]
    hidden_fees: List[Dict]
    auto_renewals: List[Dict]
    plain_english_summary: str
    comparison_with_standard: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    contract_id: str
    message: str
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []

# ==================== Document Parsing ====================

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF parsing error: {str(e)}")

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc_file = io.BytesIO(file_content)
        doc = docx.Document(doc_file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"DOCX parsing error: {str(e)}")

def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file"""
    try:
        return file_content.decode('utf-8').strip()
    except UnicodeDecodeError:
        try:
            return file_content.decode('latin-1').strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Text parsing error: {str(e)}")

def extract_text(file_content: bytes, filename: str) -> str:
    """Route to appropriate text extraction based on file extension"""
    ext = filename.lower().split('.')[-1]
    
    if ext == 'pdf':
        return extract_text_from_pdf(file_content)
    elif ext == 'docx':
        return extract_text_from_docx(file_content)
    elif ext == 'txt':
        return extract_text_from_txt(file_content)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

# ==================== AI Analysis ====================

async def analyze_contract_with_ai(contract_text: str, filename: str) -> Dict:
    """Use OpenAI to analyze the contract comprehensively"""
    
    # Truncate if too long (GPT-4 has token limits)
    max_chars = 15000
    truncated_text = contract_text[:max_chars]
    if len(contract_text) > max_chars:
        truncated_text += "\n\n[Contract truncated for analysis...]"
    
    system_prompt = """You are an expert legal contract analyst with 20+ years of experience. 
Your task is to analyze legal contracts and provide comprehensive, actionable insights.

Provide your analysis in a structured JSON format with the following sections:

1. key_terms: Array of objects with "term", "section", "meaning", "importance" (high/medium/low)
2. risks: Array of objects with "risk", "severity" (critical/high/medium/low), "explanation", "recommendation"
3. obligations: Array of objects with "party", "obligation", "deadline", "consequences"
4. unfair_clauses: Array of objects with "clause", "why_unfair", "suggested_alternative"
5. hidden_fees: Array of objects with "fee", "amount", "location_in_contract", "impact"
6. auto_renewals: Array of objects with "clause_location", "renewal_terms", "cancellation_terms", "warning"
7. plain_english_summary: A 3-5 paragraph summary in plain language
8. comparison_with_standard: How this contract compares to industry standards (better/worse/similar) with explanation
9. risk_score: Integer 1-100 (1 = very safe, 100 = extremely risky)
10. overall_assessment: Brief executive summary

Be thorough, accurate, and practical. Flag anything concerning."""

    user_prompt = f"""Please analyze the following contract:

FILENAME: {filename}

CONTRACT TEXT:
{truncated_text}

Provide a complete JSON analysis following the format specified."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=4000
        )
        
        # Parse the JSON response
        analysis_text = response.choices[0].message.content
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in analysis_text:
            json_str = analysis_text.split("```json")[1].split("```")[0].strip()
        elif "```" in analysis_text:
            json_str = analysis_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = analysis_text.strip()
        
        analysis = json.loads(json_str)
        return analysis
        
    except json.JSONDecodeError as e:
        # Fallback if JSON parsing fails
        return {
            "key_terms": [],
            "risks": [{"risk": "Analysis parsing error", "severity": "medium", "explanation": str(e), "recommendation": "Please try again"}],
            "obligations": [],
            "unfair_clauses": [],
            "hidden_fees": [],
            "auto_renewals": [],
            "plain_english_summary": "Analysis completed but parsing encountered an error. Please review the contract manually.",
            "comparison_with_standard": "Unable to compare due to parsing error.",
            "risk_score": 50,
            "overall_assessment": "Analysis completed with errors. Please review manually."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis error: {str(e)}")

# ==================== API Endpoints ====================

@app.get("/")
async def root():
    return {"message": "ContractGenius API", "version": "1.0.0", "status": "operational"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    """Upload and analyze a contract"""
    
    # Validate file
    allowed_extensions = {'.pdf', '.docx', '.txt'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Read file content
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")
    
    # Extract text
    contract_text = extract_text(content, file.filename)
    
    if not contract_text or len(contract_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Could not extract meaningful text from document")
    
    # Generate contract ID
    contract_id = str(uuid.uuid4())
    
    # Perform AI analysis
    analysis = await analyze_contract_with_ai(contract_text, file.filename)
    
    # Store contract data
    contract_data = {
        "id": contract_id,
        "filename": file.filename,
        "file_type": file_ext,
        "upload_date": datetime.now().isoformat(),
        "text_content": contract_text,
        "analysis": analysis,
        "risk_score": analysis.get("risk_score", 50),
        "key_terms": analysis.get("key_terms", []),
        "risks": analysis.get("risks", []),
        "obligations": analysis.get("obligations", []),
        "unfair_clauses": analysis.get("unfair_clauses", []),
        "hidden_fees": analysis.get("hidden_fees", []),
        "auto_renewals": analysis.get("auto_renewals", []),
        "plain_english_summary": analysis.get("plain_english_summary", ""),
        "comparison_with_standard": analysis.get("comparison_with_standard", ""),
        "overall_assessment": analysis.get("overall_assessment", "")
    }
    
    contracts_db[contract_id] = contract_data
    
    # Return analysis (exclude full text for response size)
    response_data = {k: v for k, v in contract_data.items() if k != "text_content"}
    return response_data

@app.get("/api/contracts/{contract_id}")
async def get_contract(contract_id: str):
    """Get contract analysis by ID"""
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = contracts_db[contract_id]
    response_data = {k: v for k, v in contract.items() if k != "text_content"}
    return response_data

@app.get("/api/contracts/{contract_id}/full")
async def get_contract_full(contract_id: str):
    """Get full contract data including text content"""
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    return contracts_db[contract_id]

@app.post("/api/chat")
async def chat_with_contract(chat_request: ChatRequest):
    """Chat with the AI about a specific contract"""
    
    contract_id = chat_request.contract_id
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = contracts_db[contract_id]
    contract_text = contract["text_content"][:8000]  # Limit context
    
    # Build conversation history
    messages = [
        {"role": "system", "content": f"""You are a legal assistant helping answer questions about a contract. 
Use the following contract information to answer questions accurately and helpfully.
Be concise but thorough. If you're unsure about something, say so.

CONTRACT: {contract['filename']}
KEY TERMS: {json.dumps(contract['key_terms'])}
RISKS: {json.dumps(contract['risks'])}
OBLIGATIONS: {json.dumps(contract['obligations'])}
UNFAIR CLAUSES: {json.dumps(contract['unfair_clauses'])}
HIDDEN FEES: {json.dumps(contract['hidden_fees'])}
AUTO RENEWALS: {json.dumps(contract['auto_renewals'])}

CONTRACT EXCERPT:
{contract_text}"""}
    ]
    
    # Add conversation history
    for msg in chat_request.history[-5:]:  # Keep last 5 messages for context
        messages.append({"role": msg.role, "content": msg.content})
    
    # Add current message
    messages.append({"role": "user", "content": chat_request.message})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3,
            max_tokens=1500
        )
        
        return ChatResponse(
            response=response.choices[0].message.content,
            sources=[f"Contract: {contract['filename']}"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/api/contracts/{contract_id}/export/pdf")
async def export_annotated_pdf(contract_id: str):
    """Export annotated PDF report"""
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = contracts_db[contract_id]
    
    # Create PDF report
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a365d')
    )
    story.append(Paragraph("Contract Analysis Report", title_style))
    story.append(Spacer(1, 20))
    
    # Contract info
    story.append(Paragraph(f"<b>Contract:</b> {contract['filename']}", styles['Normal']))
    story.append(Paragraph(f"<b>Analysis Date:</b> {contract['upload_date']}", styles['Normal']))
    story.append(Paragraph(f"<b>Risk Score:</b> {contract['risk_score']}/100", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Risk Score Color
    risk_color = colors.green if contract['risk_score'] < 30 else colors.orange if contract['risk_score'] < 70 else colors.red
    
    # Overall Assessment
    story.append(Paragraph("Overall Assessment", styles['Heading2']))
    story.append(Paragraph(contract['overall_assessment'], styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Plain English Summary
    story.append(Paragraph("Plain English Summary", styles['Heading2']))
    story.append(Paragraph(contract['plain_english_summary'], styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Key Terms
    if contract['key_terms']:
        story.append(Paragraph("Key Terms", styles['Heading2']))
        for term in contract['key_terms']:
            story.append(Paragraph(f"<b>{term.get('term', 'N/A')}</b> ({term.get('importance', 'medium')})", styles['Normal']))
            story.append(Paragraph(f"Meaning: {term.get('meaning', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 10))
        story.append(Spacer(1, 10))
    
    # Risks
    if contract['risks']:
        story.append(Paragraph("Identified Risks", styles['Heading2']))
        for risk in contract['risks']:
            story.append(Paragraph(f"<b>{risk.get('risk', 'N/A')}</b> - Severity: {risk.get('severity', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Explanation: {risk.get('explanation', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Recommendation: {risk.get('recommendation', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 10))
        story.append(Spacer(1, 10))
    
    # Unfair Clauses
    if contract['unfair_clauses']:
        story.append(Paragraph("Unfair Clauses", styles['Heading2']))
        for clause in contract['unfair_clauses']:
            story.append(Paragraph(f"<b>Clause:</b> {clause.get('clause', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Why it's unfair: {clause.get('why_unfair', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Suggested alternative: {clause.get('suggested_alternative', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 10))
        story.append(Spacer(1, 10))
    
    # Hidden Fees
    if contract['hidden_fees']:
        story.append(Paragraph("Hidden Fees", styles['Heading2']))
        for fee in contract['hidden_fees']:
            story.append(Paragraph(f"<b>{fee.get('fee', 'N/A')}</b>: {fee.get('amount', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Location: {fee.get('location_in_contract', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Impact: {fee.get('impact', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 10))
        story.append(Spacer(1, 10))
    
    # Auto Renewals
    if contract['auto_renewals']:
        story.append(Paragraph("Auto-Renewal Clauses", styles['Heading2']))
        for renewal in contract['auto_renewals']:
            story.append(Paragraph(f"<b>Location:</b> {renewal.get('clause_location', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Terms: {renewal.get('renewal_terms', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Cancellation: {renewal.get('cancellation_terms', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"<font color='red'>Warning: {renewal.get('warning', 'N/A')}</font>", styles['Normal']))
            story.append(Spacer(1, 10))
        story.append(Spacer(1, 10))
    
    # Comparison
    story.append(Paragraph("Comparison with Industry Standards", styles['Heading2']))
    story.append(Paragraph(contract['comparison_with_standard'], styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 40))
    story.append(Paragraph("Generated by ContractGenius - AI-Powered Legal Contract Analysis", styles['Italic']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=contract_analysis_{contract_id}.pdf"}
    )

@app.get("/api/contracts/{contract_id}/export/json")
async def export_json(contract_id: str):
    """Export analysis as JSON"""
    if contract_id not in contracts_db:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = contracts_db[contract_id]
    response_data = {k: v for k, v in contract.items() if k != "text_content"}
    
    return response_data

@app.get("/api/contracts")
async def list_contracts():
    """List all analyzed contracts"""
    contracts_list = []
    for contract_id, contract in contracts_db.items():
        contracts_list.append({
            "id": contract_id,
            "filename": contract["filename"],
            "upload_date": contract["upload_date"],
            "risk_score": contract["risk_score"]
        })
    return contracts_list

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))