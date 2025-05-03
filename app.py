import datetime
import uuid

import streamlit as st
import requests
from pathlib import Path
import json
import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Legal Brief Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)
def save_file_to_supabase(file, doc_type, metadata=None):
    """Save uploaded file to Supabase storage"""
    try:

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = str(uuid.uuid4())[:8]
        file_extension = Path(file.name).suffix
        storage_path = f"legal_briefs/{doc_type}/{timestamp}_{file_id}{file_extension}"

        response = supabase.storage.from_("documents").upload(
            path=storage_path,
            file=file.getvalue(),
            file_options={"content-type": file.type}
        )

        file_url = supabase.storage.from_("documents").get_public_url(storage_path)

        file_record = {
            "filename": file.name,
            "doc_type": doc_type,
            "storage_path": storage_path,
            "file_url": file_url,
            "upload_date": datetime.datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        db_response = supabase.table("documents").insert(file_record).execute()

        st.success(f"✅ {doc_type.title()} saved to Supabase")
        return file_url

    except Exception as e:
        st.error(f"Error saving file to Supabase: {str(e)}")
        return None
def process_document(file, doc_type):
    """Send document to backend for processing and save to Supabase"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{BACKEND_URL}/upload", files=files)

        if response.status_code != 200:
            error_detail = response.json().get('detail', 'Unknown error')
            st.error(f"Error processing {doc_type}: {error_detail}")
            return None

        result_data = response.json().get('data')

        save_file_to_supabase(file, doc_type, metadata={
            "processed_at": datetime.datetime.now().isoformat(),
            "content_summary": result_data.get("summary", ""),
            "headings_count": len(result_data.get("headings", [])),
        })

        return result_data
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None

def link_documents(moving_brief_data, response_brief_data):
    """Send processed documents to backend for linking"""
    try:
        payload = {
            "moving_brief": moving_brief_data,
            "response_brief": response_brief_data
        }

        response = requests.post(
            f"{BACKEND_URL}/link",
            json=payload
        )

        if response.status_code != 200:
            error_detail = response.json().get('detail', 'Unknown error')
            st.error(f"Error linking documents: {error_detail}")
            return None

        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None

def display_linked_arguments(links_data):
    """Display the linked arguments in two columns"""
    if not links_data or "links" not in links_data:
        st.error("No links found between the documents")
        return

    for link in links_data["links"]:
        cols = st.columns(2)

        with cols[0]:
            st.markdown("### Moving Brief")
            st.markdown(f"**{link['moving_brief_heading']}**")

        with cols[1]:
            st.markdown("### Response Brief")
            st.markdown(f"**{link['response_brief_heading']}**")

        st.markdown("#### Link Details")
        st.markdown(f"Similarity Score: {link['similarity_score']:.2f}")
        st.markdown("**Explanation:**")
        st.markdown(link["explanation"])
        st.divider()

def main():
    st.title("Legal Brief Analysis")

    with st.sidebar:
        st.header("Document Upload")
        moving_brief = st.file_uploader("Upload Moving Brief", type=["pdf", "docx"])
        response_brief = st.file_uploader("Upload Response Brief", type=["pdf", "docx"])

        st.divider()
        st.header("Demo Documents")
        if st.button("Load Demo Briefs"):

            pass

    if moving_brief and response_brief:
        if st.button("Process Documents", type="primary"):
            with st.spinner("Processing documents..."):

                st.info(f"Processing moving brief: {moving_brief.name}")
                moving_brief_data = process_document(moving_brief, "moving brief")
                if not moving_brief_data:
                    return

                st.info(f"Processing response brief: {response_brief.name}")
                response_brief_data = process_document(response_brief, "response brief")
                if not response_brief_data:
                    return

                with st.spinner("Analyzing arguments and finding links..."):
                    st.info("Finding semantic links between arguments...")
                    links_data = link_documents(moving_brief_data, response_brief_data)
                    if links_data:
                        st.success("Analysis complete!")
                        display_linked_arguments(links_data)
    else:
        st.info("Please upload both briefs to begin analysis")

    st.divider()
    st.header("Saved Documents")
    if st.button("View Saved Briefs"):
        with st.spinner("Loading saved documents..."):
            try:
                response = supabase.table("documents").select("*").order("upload_date", desc=True).limit(10).execute()
                documents = response.data

                if documents:
                    for doc in documents:
                        st.markdown(f"**{doc['filename']}** ({doc['doc_type']})")
                        st.markdown(f"Uploaded: {doc['upload_date'][:10]}")
                        if st.button("Load", key=f"load_{doc['id']}"):

                            st.info(f"Loading {doc['filename']}...")
                else:
                    st.info("No saved documents found")
            except Exception as e:
                st.error(f"Error retrieving saved documents: {str(e)}")

if __name__ == "__main__":
    main()
