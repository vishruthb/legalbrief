from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from .parser import parse_document
from .linker import link_arguments
from typing import Dict, List, Any
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> Dict:
    """
    Process uploaded document using LlamaParse
    """
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
            
        # Check file extension
        filename = file.filename.lower()
        if not (filename.endswith('.pdf') or filename.endswith('.docx')):
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
            
        parsed_content = await parse_document(file)
        return {"status": "success", "data": parsed_content}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/link")
async def link_documents(payload: Dict[str, Any]) -> Dict:
    """
    Link arguments between moving and response briefs
    """
    try:
        if "moving_brief" not in payload or "response_brief" not in payload:
            raise HTTPException(status_code=400, detail="Both moving_brief and response_brief are required")
            
        moving_brief = payload["moving_brief"]
        response_brief = payload["response_brief"]
        
        links = link_arguments(moving_brief, response_brief)
        return {"status": "success", "links": links}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
