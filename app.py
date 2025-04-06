import streamlit as st
import requests
from pathlib import Path
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Legal Brief Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    # Main content area with two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Moving Brief")
        if moving_brief:
            with st.spinner("Processing moving brief..."):
                # TODO: Send to backend for processing
                pass
    
    with col2:
        st.header("Response Brief")
        if response_brief:
            with st.spinner("Processing response brief..."):
                # TODO: Send to backend for processing
                pass
    
    # Process button
    if moving_brief and response_brief:
        if st.button("Process Documents", type="primary"):
            with st.spinner("Analyzing documents and finding links..."):
                try:
                    # TODO: Send both documents to backend for processing
                    # TODO: Display results with interactive elements
                    pass
                except Exception as e:
                    st.error(f"Error processing documents: {str(e)}")

if __name__ == "__main__":
    main()
