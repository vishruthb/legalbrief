import streamlit as st
import requests
from pathlib import Path
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API endpoints
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Legal Brief Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

def process_document(file, doc_type):
    """Send document to backend for processing"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{BACKEND_URL}/upload", files=files)
        
        if response.status_code != 200:
            error_detail = response.json().get('detail', 'Unknown error')
            st.error(f"Error processing {doc_type}: {error_detail}")
            return None
            
        return response.json().get('data')
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
        
        # Moving brief argument
        with cols[0]:
            st.markdown("### Moving Brief")
            st.markdown(f"**{link['moving_brief_heading']}**")
            
        # Response brief argument
        with cols[1]:
            st.markdown("### Response Brief")
            st.markdown(f"**{link['response_brief_heading']}**")
            
        # Explanation and similarity score
        st.markdown("#### Link Details")
        st.markdown(f"Similarity Score: {link['similarity_score']:.2f}")
        st.markdown("**Explanation:**")
        st.markdown(link["explanation"])
        st.divider()

def main():
    st.title("Legal Brief Analysis")
    
    # Sidebar for file upload and controls
    with st.sidebar:
        st.header("Document Upload")
        moving_brief = st.file_uploader("Upload Moving Brief", type=["pdf", "docx"])
        response_brief = st.file_uploader("Upload Response Brief", type=["pdf", "docx"])
        
        st.divider()
        st.header("Demo Documents")
        if st.button("Load Demo Briefs"):
            # TODO: Load demo documents from database
            pass
    
    # Main content area
    if moving_brief and response_brief:
        if st.button("Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                # Process moving brief
                st.info(f"Processing moving brief: {moving_brief.name}")
                moving_brief_data = process_document(moving_brief, "moving brief")
                if not moving_brief_data:
                    return
                
                # Process response brief
                st.info(f"Processing response brief: {response_brief.name}")
                response_brief_data = process_document(response_brief, "response brief")
                if not response_brief_data:
                    return
                
                # Link the documents
                with st.spinner("Analyzing arguments and finding links..."):
                    st.info("Finding semantic links between arguments...")
                    links_data = link_documents(moving_brief_data, response_brief_data)
                    if links_data:
                        st.success("Analysis complete!")
                        display_linked_arguments(links_data)
    else:
        st.info("Please upload both briefs to begin analysis")

if __name__ == "__main__":
    main()
