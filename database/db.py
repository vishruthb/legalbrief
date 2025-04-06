from supabase import create_client
import os
from dotenv import load_dotenv
from typing import Dict, List
import json
from datetime import datetime

load_dotenv()

class Database:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found")
        
        self.client = create_client(supabase_url, supabase_key)

    def store_brief(self, brief_content: Dict, document_type: str) -> str:
        """
        Store parsed brief in the database
        """
        data = {
            "document_type": document_type,
            "parsed_content": json.dumps(brief_content),
            "upload_timestamp": datetime.utcnow().isoformat()
        }
        
        result = self.client.table("briefs").insert(data).execute()
        return result.data[0]["brief_id"]

    def store_links(self, links: List[Dict], brief_pair_id: str) -> None:
        """
        Store argument links in the database
        """
        for link in links:
            data = {
                "brief_pair_id": brief_pair_id,
                "moving_brief_heading": link["moving_brief_heading"],
                "response_brief_heading": link["response_brief_heading"],
                "similarity_score": link["similarity_score"],
                "explanation": link["explanation"]
            }
            self.client.table("links").insert(data).execute()

    def get_demo_briefs(self) -> Dict:
        """
        Retrieve demo brief pair from the database
        """
        result = self.client.table("briefs").select("*").eq("is_demo", True).execute()
        if not result.data:
            raise ValueError("No demo briefs found")
        
        demo_briefs = {
            "moving_brief": None,
            "response_brief": None
        }
        
        for brief in result.data:
            if brief["document_type"] == "moving":
                demo_briefs["moving_brief"] = json.loads(brief["parsed_content"])
            elif brief["document_type"] == "response":
                demo_briefs["response_brief"] = json.loads(brief["parsed_content"])
        
        return demo_briefs
