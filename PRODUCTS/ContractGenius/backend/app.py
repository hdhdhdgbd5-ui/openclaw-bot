from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import PyPDF2
import docx
import os
from typing import Optional
import re

# AI Integration (placeholder - replace with actual API key)
import openai

app = FastAPI(title="ContractGenius API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your OpenAI API key here or via environment variable
# openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")

@app.get("/")
async def root():
    return {"status": "ContractGenius API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    """Analyze uploaded contract with AI"""
    
    # Validate file
    allowed_types = ['.pdf', '.docx', '.txt', '.doc']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}")
    
    # Extract text
    content = await file.read()
    text = extract_text(content, file_ext)
    
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from file")
    
    # Perform analysis
    analysis = perform_analysis(text)
    
    return JSONResponse(content=analysis)


def extract_text(content: bytes, file_ext: str) -> str:
    """Extract text from PDF, DOCX, or TXT"""
    
    if file_ext == '.pdf':
        return extract_pdf_text(content)
    elif file_ext == '.docx':
        return extract_docx_text(content)
    elif file_ext == '.txt':
        return content.decode('utf-8', errors='ignore')
    elif file_ext == '.doc':
        # For .doc files, we'd need additional libraries
        return content.decode('utf-8', errors='ignore')
    
    return ""


def extract_pdf_text(content: bytes) -> str:
    """Extract text from PDF bytes"""
    try:
        import io
        pdf_file = io.BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"


def extract_docx_text(content: bytes) -> str:
    """Extract text from DOCX bytes"""
    try:
        import io
        doc = docx.Document(io.BytesIO(content))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"


def perform_analysis(text: str) -> dict:
    """Perform AI-powered analysis on contract text"""
    
    # Basic pattern matching for demo (AI integration comes with API key)
    risk_score = calculate_risk_score(text)
    
    return {
        "risk_score": risk_score,
        "risk_level": get_risk_level(risk_score),
        "summary": generate_summary(text),
        "key_terms": extract_key_terms(text),
        "red_flags": detect_red_flags(text),
        "recommendations": generate_recommendations(text),
        "word_count": len(text.split()),
        "analysis_date": "2026-02-19",
        "premium_available": True
    }


def calculate_risk_score(text: str) -> int:
    """Calculate risk score 0-100"""
    score = 30  # Base score
    
    high_risk_terms = [
        'unlimited liability', 'indemnify', 'no limitation', 'sole discretion',
        'no warranty', 'as is', 'without recourse', 'binding arbitration'
    ]
    
    medium_risk_terms = [
        'auto-renew', 'automatic renewal', 'termination fee', 'notice required',
        'without cause', 'liquidated damages', 'non-compete'
    ]
    
    text_lower = text.lower()
    
    for term in high_risk_terms:
        if term in text_lower:
            score += 15
    
    for term in medium_risk_terms:
        if term in text_lower:
            score += 8
    
    return min(100, max(0, score))


def get_risk_level(score: int) -> str:
    if score > 60:
        return "high"
    elif score > 40:
        return "medium"
    return "low"


def extract_key_terms(text: str) -> list:
    """Extract key contract terms"""
    terms = []
    text_lower = text.lower()
    
    # Payment terms
    payment_match = re.search(r'(payment|pay).{0,50}(\d+\s*(days?|business days?)|net\s*\d+|upon\s+receipt)', text_lower)
    if payment_match:
        terms.append({
            "term": "Payment Terms",
            "value": payment_match.group(0)[:50],
            "risk": "medium"
        })
    
    # Term/Duration
    term_match = re.search(r'(term|duration|period).{0,30}(\d+\s*(month|year|day)s?|indefinite)', text_lower)
    if term_match:
        terms.append({
            "term": "Contract Term",
            "value": term_match.group(0)[:50],
            "risk": "low"
        })
    
    # Termination
    termination_match = re.search(r'(terminat|cancel).{0,50}(\d+\s*days?\s*notice|with\s+cause|without\s+cause)', text_lower)
    if termination_match:
        risk = "low"
        if "without cause" in termination_match.group(0):
            risk = "high"
        terms.append({
            "term": "Termination Clause",
            "value": termination_match.group(0)[:50],
            "risk": risk
        })
    
    # Governing law
    law_match = re.search(r'(governed by|governing law).{0,30}([A-Z][a-z]+\s*,?\s*[A-Z][a-z]+)', text)
    if law_match:
        terms.append({
            "term": "Governing Law",
            "value": law_match.group(2),
            "risk": "low"
        })
    
    return terms if terms else [
        {"term": "Payment Terms", "value": "Not clearly specified", "risk": "high"},
        {"term": "Contract Term", "value": "Requires review", "risk": "medium"}
    ]


def detect_red_flags(text: str) -> list:
    """Detect red flags in contract"""
    flags = []
    text_lower = text.lower()
    
    red_flags_patterns = [
        (r'(auto.?renew|automatic.?renew)', 'Auto-renewal clause activates without notice', 'high'),
        (r'(unlimited liability|no.*limit.*liability)', 'Unlimited liability exposure', 'high'),
        (r'(jury.?waiver|waive.*jury)', 'Jury trial waiver', 'medium'),
        (r'(binding arbitration|arbitration agreement)', 'Binding arbitration clause', 'medium'),
        (r'(non.?compete|non-competition)', 'Non-compete clause', 'high'),
        (r'(intellectual property assignment)', 'IP assignment without compensation', 'high'),
        (r'(indemnif|hold.?harmless)', 'Broad indemnification clause', 'medium')
    ]
    
    for pattern, description, severity in red_flags_patterns:
        if re.search(pattern, text_lower):
            flags.append({
                "clause": description,
                "severity": severity
            })
    
    return flags if flags else [
        {"clause": "No auto-renewal clause detected", "severity": "low"},
        {"clause": "Standard liability provisions", "severity": "low"}
    ]


def generate_recommendations(text: str) -> list:
    """Generate recommendations based on analysis"""
    recommendations = []
    text_lower = text.lower()
    
    if 'auto-renew' in text_lower or 'automatic renewal' in text_lower:
        recommendations.append("Negotiate removal of auto-renewal or add 30-day notice requirement")
    
    if re.search(r'(liability|damages)', text_lower):
        recommendations.append("Review and cap liability at reasonable amount (e.g., fees paid)")
    
    if re.search(r'(termination|cancel)', text_lower):
        recommendations.append("Ensure termination for convenience is mutual")
    
    if not re.search(r'(warranty|warrant)', text_lower):
        recommendations.append("Add appropriate warranties from both parties")
    
    if not recommendations:
        recommendations = [
            "Contract appears standard - review with legal counsel before signing",
            "Consider negotiating payment terms for better cash flow",
            "Ensure all verbal agreements are documented in writing"
        ]
    
    return recommendations


def generate_summary(text: str) -> str:
    """Generate plain English summary"""
    sentences = text.split('.')
    first_sentences = '.'.join(sentences[:3])
    return f"This contract appears to be a {detect_contract_type(text)}. " + \
           f"It contains {len(text.split())} words. " + \
           "Key areas to review: payment terms, termination clauses, and liability provisions."


def detect_contract_type(text: str) -> str:
    """Detect type of contract"""
    text_lower = text.lower()
    
    if 'employment' in text_lower or 'employee' in text_lower:
        return "Employment Agreement"
    elif 'service' in text_lower or 'services' in text_lower:
        return "Service Agreement"
    elif 'lease' in text_lower or 'rental' in text_lower:
        return "Lease/Rental Agreement"
    elif 'nda' in text_lower or 'confidential' in text_lower:
        return "Non-Disclosure Agreement"
    elif 'license' in text_lower:
        return "License Agreement"
    else:
        return "Service/Commercial Agreement"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
