from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .parser import parse_document
from .linker import link_arguments
from typing import Dict, List
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
async def upload_document(file: UploadFile) -> Dict:
    """
    Process uploaded document using LlamaParse
    """
    try:
        parsed_content = await parse_document(file)
        return {"status": "success", "data": parsed_content}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/link")
async def link_documents(moving_brief: Dict, response_brief: Dict) -> Dict:
    """
    Link arguments between moving and response briefs
    """
    try:
        links = link_arguments(moving_brief, response_brief)
        return {"status": "success", "links": links}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
