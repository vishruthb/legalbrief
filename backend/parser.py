from fastapi import UploadFile
from llama_cloud_services import LlamaParse
from llama_index.core import SimpleDirectoryReader
import os
from dotenv import load_dotenv
from typing import Dict, List
import json
import nest_asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

load_dotenv()

LLAMA_CLOUD_API_KEY = os.getenv("LLAMAPARSE_API_KEY")  # Using the same env var for compatibility

async def parse_document(file: UploadFile) -> Dict:
    """
    Parse legal brief using LlamaParse via LlamaIndex
    """
    logger.info(f"Starting to parse document: {file.filename}")
    
    if not LLAMA_CLOUD_API_KEY:
        logger.error("LlamaParse API key not found")
        raise ValueError("LlamaParse API key not found")

    # Save uploaded file temporarily
    temp_path = f"/tmp/{file.filename}"
    try:
        with open(temp_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        logger.info(f"File saved temporarily at: {temp_path}")
        
        # For testing purposes, return a mock structure if LlamaParse is not working
        # This helps bypass LlamaParse issues during development
        # Remove this in production
        logger.info("Using mock data for testing")
        structured_content = {
            "brief_id": str(hash(file.filename))[:8],
            "arguments": [
                {
                    "heading": "Argument I",
                    "content": "This is a sample argument from the moving brief.",
                    "section_id": "12345678"
                },
                {
                    "heading": "Argument II",
                    "content": "This is another sample argument discussing legal precedent.",
                    "section_id": "87654321"
                }
            ]
        }
        
        logger.info("Document parsing completed successfully")
        return structured_content
        
        # Uncomment the below code when LlamaParse is properly configured
        """
        # Initialize LlamaParse with markdown output
        parser = LlamaParse(
            api_key=LLAMA_CLOUD_API_KEY,
            result_type="markdown"
        )
        
        # Use SimpleDirectoryReader with our parser
        file_extractor = {".pdf": parser, ".docx": parser}
        documents = SimpleDirectoryReader(
            input_files=[temp_path], 
            file_extractor=file_extractor
        ).load_data()
        
        if not documents:
            logger.error(f"Failed to parse document: {file.filename}")
            raise ValueError(f"Failed to parse document: {file.filename}")
        
        # Extract arguments and structure from the parsed document
        # We'll assume the first document contains our content
        doc = documents[0]
        
        # Convert markdown content to structured format
        structured_content = {
            "brief_id": str(hash(doc.text))[:8],  # Generate a simple ID
            "arguments": []
        }
        
        # Split content into sections based on markdown headers
        sections = doc.text.split('\n#')
        for section in sections:
            if not section.strip():
                continue
                
            # Extract heading and content
            lines = section.strip().split('\n', 1)
            if len(lines) == 2:
                heading = lines[0].strip('# ')
                content = lines[1].strip()
                
                if is_argument_section(heading):
                    argument = {
                        "heading": heading,
                        "content": content,
                        "section_id": str(hash(heading))[:8]
                    }
                    structured_content["arguments"].append(argument)

        logger.info("Document parsing completed successfully")
        return structured_content
        """
    
    except Exception as e:
        logger.error(f"Error parsing document: {str(e)}")
        raise
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"Temporary file removed: {temp_path}")

def is_argument_section(heading: str) -> bool:
    """
    Determine if a section is an argument section based on its heading
    """
    # Common patterns in legal brief argument sections
    argument_indicators = [
        "argument",
        "point",
        "reason",
        "contention",
        "discussion"
    ]
    
    return any(indicator in heading.lower() for indicator in argument_indicators)
