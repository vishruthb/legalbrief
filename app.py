import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.card import card
import datetime
import uuid
import requests
from pathlib import Path
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# API endpoints
BACKEND_URL = "http://127.0.0.1:8000"

# Set page config
st.set_page_config(
    page_title="Legal Brief Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }
    .stButton button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        background-color: #4F46E5;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #4338CA;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .document-card {
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .document-card:hover {
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        transform: translateY(-4px);
    }
    .nav-link {
        display: block;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        text-decoration: none;
        transition: background-color 0.2s;
    }
    .nav-link:hover {
        background-color: rgba(79, 70, 229, 0.1);
    }
    .nav-link.active {
        background-color: rgba(79, 70, 229, 0.2);
        color: #4F46E5;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Save file function (unchanged)
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

        # Save file to Supabase with processing metadata
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
# Improved display for linked arguments
def display_linked_arguments(links_data):
    """Display the linked arguments with improved UI"""
    if not links_data or "links" not in links_data:
        st.error("No links found between the documents")
        return

    for i, link in enumerate(links_data["links"]):
        with st.container():
            st.markdown(f"<div class='document-card'>", unsafe_allow_html=True)

            cols = st.columns(2)
            # Moving brief argument
            with cols[0]:
                st.markdown(f"#### Moving Brief")
                st.markdown(f"**{link['moving_brief_heading']}**")

            # Response brief argument
            with cols[1]:
                st.markdown(f"#### Response Brief")
                st.markdown(f"**{link['response_brief_heading']}**")

            # Explanation and similarity score
            st.markdown(f"**Similarity: {link['similarity_score']:.2f}**")
            st.markdown(f"*{link['explanation']}*")
            st.markdown("</div>", unsafe_allow_html=True)

# Main app with navigation
def main():
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x60?text=LegalBrief", width=150)
        st.markdown("### Navigation")

        page = st.radio("", ["Upload & Analyze", "Document Library"],
                        label_visibility="collapsed")

        st.divider()

        if page == "Upload & Analyze":
            st.markdown("### Document Upload")
            moving_brief = st.file_uploader("Upload Moving Brief", type=["pdf", "docx"])
            response_brief = st.file_uploader("Upload Response Brief", type=["pdf", "docx"])

            st.divider()
            st.markdown("### Demo Documents")
            if st.button("Load Demo Briefs"):
                # TODO: Load demo documents
                pass

    # Main content based on selected page
    if page == "Upload & Analyze":
        colored_header(
            label="Legal Brief Analysis",
            description="Upload and analyze legal briefs to find semantic connections",
            color_name="violet-70"
        )

        if moving_brief and response_brief:
            if st.button("Process Documents", type="primary", use_container_width=True):
                st.markdown("---")
                with st.status("Processing documents...") as status:
                    # Process moving brief
                    st.write(f"Processing moving brief: {moving_brief.name}")
                    moving_brief_data = process_document(moving_brief, "moving brief")
                    if not moving_brief_data:
                        status.update(label="Error processing moving brief", state="error")
                        return

                    # Process response brief
                    st.write(f"Processing response brief: {response_brief.name}")
                    response_brief_data = process_document(response_brief, "response brief")
                    if not response_brief_data:
                        status.update(label="Error processing response brief", state="error")
                        return

                    # Link the documents
                    st.write("Finding semantic links between arguments...")
                    links_data = link_documents(moving_brief_data, response_brief_data)
                    if links_data:
                        status.update(label="Analysis complete!", state="complete")
                        display_linked_arguments(links_data)
                    else:
                        status.update(label="Error linking documents", state="error")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div class='document-card'>
                    <h3>📄 Moving Brief</h3>
                    <p>Upload a moving brief to begin analysis</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div class='document-card'>
                    <h3>📄 Response Brief</h3>
                    <p>Upload a response brief to compare</p>
                </div>
                """, unsafe_allow_html=True)

            st.info("Please upload both briefs to begin analysis")

    elif page == "Document Library":
        colored_header(
            label="Document Library",
            description="View and manage your previously uploaded documents",
            color_name="blue-70"
        )

        # Filters
        col1, col2 = st.columns([1, 3])
        with col1:
            doc_type_filter = st.selectbox("Document Type",
                                           ["All", "Moving Brief", "Response Brief"])
        with col2:
            search_query = st.text_input("Search documents", placeholder="Enter filename...")

        # Get documents from Supabase
        try:
            query = supabase.table("documents").select("*").order("upload_date", desc=True)

            if doc_type_filter != "All":
                query = query.eq("doc_type", doc_type_filter.lower())

            response = query.execute()
            documents = response.data

            if not documents:
                st.info("No documents found. Upload some documents first!")
            else:
                st.markdown(f"### Found {len(documents)} documents")

                # Display documents in a grid
                cols = st.columns(3)
                for i, doc in enumerate(documents):
                    with cols[i % 3]:
                        with st.container():
                            st.markdown(f"<div class='document-card'>", unsafe_allow_html=True)
                            st.markdown(f"#### {doc['filename']}")
                            st.markdown(f"**Type:** {doc['doc_type'].title()}")
                            st.markdown(f"**Uploaded:** {doc['upload_date'][:10]}")

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("View", key=f"view_{doc['id']}"):
                                    st.markdown(f"[Open document]({doc['file_url']})")
                            with col2:
                                if st.button("Analyze", key=f"analyze_{doc['id']}"):
                                    st.info("Feature coming soon!")
                            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error retrieving documents: {str(e)}")

if __name__ == "__main__":
    main()