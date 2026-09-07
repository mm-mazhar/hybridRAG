# """
# sidebar_handler.py
# Created on Dec 17, 2024
# @ Author: Mazhar
# """

import os
import tempfile
from collections.abc import Iterable
from urllib.parse import ParseResult, urlparse

import lancedb
import requests
import streamlit as st
from docling_core.types.doc.document import DoclingDocument
from lancedb.table import Table
from streamlit.runtime.uploaded_file_manager import UploadedFile

from configs import cfgs
from src.app.embedding import create_embeddings
from src.app.extraction import extract_from_sitemap, extract_html, extract_pdf
from utils.st_utils import clean_table_name, init_db, load_chat_history


def handle_existing_database() -> Table | None:
    """Handle the 'Use Existing Database' option in sidebar."""
    # Get the database path
    db_path: str = os.path.abspath(
        path=os.path.join(os.path.dirname(p=__file__), "../../../", cfgs["VECTOR_DB"]["URI"])
    )

    # Connect to database
    db: lancedb.DBConnection = lancedb.connect(uri=db_path)
    available_tables: Iterable[str] = db.table_names()

    if not available_tables:
        st.sidebar.warning(body="No tables found in the database.")
        return None

    selected_table: str = st.sidebar.selectbox(
        label="Select Table",
        options=available_tables,
        help="Choose which document table to query",
    )

    if selected_table:
        table: Table = init_db(db_uri=cfgs["VECTOR_DB"]["URI"], table_name=selected_table)
        st.sidebar.success(body=f"Connected to table: {selected_table}")
        return table
    return None


def handle_pdf_upload() -> Table | None:
    """Handle the 'Upload PDF' option in sidebar."""
    uploaded_file: UploadedFile | None = st.sidebar.file_uploader(label="Upload PDF", type="pdf")
    if not uploaded_file:
        return None

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path: str = tmp_file.name

    if not st.sidebar.button(label="Process PDF"):
        return None

    with st.spinner(text="Processing PDF..."):
        markdown_content, _ = extract_pdf(pdf_path=tmp_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as md_file:
            md_file.write(markdown_content.encode())
            md_path: str = md_file.name

        table_name: str = f"pdf_{clean_table_name(name=uploaded_file.name)}"
        table: Table = create_embeddings(
            source_path=md_path,
            max_tokens=cfgs["LLM"]["MAX_TOKENS"],
            db_path=cfgs["VECTOR_DB"]["URI"],
            table_name=table_name,
            llm_provider=cfgs["LLM"]["PROVIDER"],
            embed_model=cfgs["EMBEDDINGS"]["MODEL"],
            mode="overwrite",
        )
        load_chat_history(file_name=table.name)
        st.sidebar.success(body=f"PDF processed successfully! Table name: {table_name}")
        return table


def handle_url_input() -> Table | None:
    """Handle the 'Enter URL' option in sidebar."""
    url: str = st.sidebar.text_input(label="Enter URL (e.g., https://www.ribalta.pt)")

    if not url or not st.sidebar.button(label="Process URL"):
        return None

    # Validate URL format
    parsed_url: ParseResult = urlparse(url=url)
    if not parsed_url.scheme or not parsed_url.netloc:
        st.sidebar.error(
            body="Invalid URL. Please enter a valid website URL (e.g., https://www.ribalta.pt)."
        )
        return None

    # Check if the URL is reachable
    try:
        response: requests.Response = requests.head(
            url=url, timeout=5
        )  # Use HEAD request to check existence
        if response.status_code >= 400:
            st.sidebar.error(
                body=(
                    f"URL is not accessible (Status Code: {response.status_code}). "
                    "Please check the link."
                )
            )
            return None
    except requests.RequestException:
        st.sidebar.error(
            body="Could not reach the website. Please check your internet connection or the URL."
        )
        return None

    with st.spinner(text="Processing URL..."):
        domain: str = parsed_url.netloc
        if domain.startswith("www."):
            domain = domain[4:]

        for tld in cfgs["COMMON_TLDS"]:
            if domain.endswith(tld):
                domain = domain[: -len(tld)]
                break

        table_name: str = f"url_{clean_table_name(name=domain)}"
        markdown_content: str = extract_html(html_path=url)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as tmp_file:
            tmp_file.write(markdown_content.encode())
            tmp_path: str = tmp_file.name

        table: Table = create_embeddings(
            source_path=tmp_path,
            max_tokens=cfgs["LLM"]["MAX_TOKENS"],
            db_path=cfgs["VECTOR_DB"]["URI"],
            table_name=table_name,
            llm_provider=cfgs["LLM"]["PROVIDER"],
            embed_model=cfgs["EMBEDDINGS"]["MODEL"],
            mode="overwrite",
        )
        load_chat_history(file_name=table.name)
        st.sidebar.success(body=f"URL processed successfully! Table name: {table_name}")
        return table


def handle_website_extraction() -> Table | None:
    """Handle the 'Extract Website' option in sidebar."""
    base_url: str = st.sidebar.text_input(
        label="Enter Website Base URL (e.g., https://www.ribalta.pt)"
    )
    sitemap_filename: str = st.sidebar.text_input(label="Sitemap Filename", value="sitemap.xml")

    if not base_url or not st.sidebar.button(label="Process Website"):
        return None

    # Ensure URL validity
    parsed_url: ParseResult = urlparse(base_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        st.sidebar.error(
            body="Invalid URL. Please enter a valid website URL (e.g., https://www.ribalta.pt)."
        )
        return None

    # Construct full sitemap URL
    sitemap_url: str = f"{base_url.rstrip('/')}/{sitemap_filename}"

    # Check if sitemap.xml exists
    try:
        response: requests.Response = requests.head(sitemap_url, timeout=5)
        if response.status_code != 200:
            st.sidebar.error(
                body=(
                    f"No sitemap found at {sitemap_url}. "
                    "Please check the URL or enter the correct sitemap filename."
                )
            )
            return None
    except requests.RequestException:
        st.sidebar.error(body=f"Could not reach {sitemap_url}. Please check the website URL.")
        return None

    with st.spinner(text="Processing Website..."):
        domain: str = parsed_url.netloc
        if domain.startswith("www."):
            domain = domain[4:]

        for tld in cfgs["COMMON_TLDS"]:
            if domain.endswith(tld):
                domain = domain[: -len(tld)]
                break

        table_name: str = f"site_{clean_table_name(name=domain)}"
        docs: list[DoclingDocument] = extract_from_sitemap(
            base_url=base_url, sitemap_filename=sitemap_filename
        )
        combined_content: str = "\n\n".join([doc.export_to_markdown() for doc in docs])

        with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as tmp_file:
            tmp_file.write(combined_content.encode())
            tmp_path: str = tmp_file.name

        table: Table = create_embeddings(
            source_path=tmp_path,
            max_tokens=cfgs["LLM"]["MAX_TOKENS"],
            db_path=cfgs["VECTOR_DB"]["URI"],
            table_name=table_name,
            llm_provider=cfgs["LLM"]["PROVIDER"],
            embed_model=cfgs["EMBEDDINGS"]["MODEL"],
            mode="overwrite",
        )
        load_chat_history(file_name=table.name)
        st.sidebar.success(body=f"Website processed successfully! Table name: {table_name}")
        return table


def handle_sidebar() -> Table | None:
    """Main function to handle all sidebar interactions."""
    st.sidebar.header(body="Document Input")

    # Ensure session state variables exist
    if "current_input_type" not in st.session_state:
        st.session_state.current_input_type = None
    if "table_name" not in st.session_state:
        st.session_state.table_name = None
    if "table" not in st.session_state:
        st.session_state.table = None  # Persist table reference

    input_type: str = st.sidebar.selectbox(
        label="Select Input Type",
        options=["Use Existing Database", "Upload PDF", "Enter URL", "Extract Website"],
    )

    # Reset table ONLY if the input type changes
    if input_type != st.session_state.current_input_type:
        st.session_state.current_input_type = input_type
        st.session_state.table_name = None
        st.session_state.table = None
        st.rerun()  # Ensure Streamlit updates the UI

    table: Table | None = None
    if input_type == "Use Existing Database":
        table = handle_existing_database()
    elif input_type == "Upload PDF":
        table = handle_pdf_upload()
    elif input_type == "Enter URL":
        table = handle_url_input()
    elif input_type == "Extract Website":
        table = handle_website_extraction()

    # Save table in session state only if it's valid
    if table and table.name:
        st.session_state.table = table
        st.session_state.table_name = table.name

    return st.session_state.table  # Ensure table reference is returned
