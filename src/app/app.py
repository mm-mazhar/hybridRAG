# """
# app.py
# Created on Dec 17, 2024
# @ Author: Mazhar
# ""

import logging
import os
import sys

# Add project root directory to Python path
sys.path.append(os.path.abspath(path=os.path.join(os.path.dirname(p=__file__), "../../")))
import warnings

import streamlit as st
from dotenv import load_dotenv
from lancedb.table import Table
from openai import OpenAI
from utils.sidebar_handler import handle_sidebar
from utils.st_utils import (
    get_chat_response,
    get_context,
    load_chat_history,
    save_chat_history,
)

from configs import cfgs

# Configure logging to ignore specific warnings
logging.getLogger(name="streamlit.watcher.local_sources_watcher").setLevel(level=logging.ERROR)
warnings.filterwarnings(
    action="ignore",
    category=UserWarning,
    module="streamlit.watcher.local_sources_watcher",
)


# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()


def initialize_session() -> None:
    """Initialize session state variables if they do not exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "table" not in st.session_state:
        st.session_state.table = None
    if "table_name" not in st.session_state:
        st.session_state.table_name = None
    if "current_input_type" not in st.session_state:
        st.session_state.current_input_type = None


def main() -> None:
    """Main function to run the Streamlit chat application."""
    st.subheader(body="📚 A Document Q&A Application with LanceDB")

    # Ensure session state is initialized
    initialize_session()

    # Load sidebar for document selection
    table = handle_sidebar()

    # Ensure valid table is selected
    if not table:
        st.info(body="Please select or process a document to start chatting.")
        st.stop()

    # Store table in session state to persist across interactions
    if table.name == st.session_state.table_name:
        st.session_state.table = table
        st.session_state.table_name = table.name
        st.session_state.messages = load_chat_history(file_name=table.name)

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(name=message["role"]):
            st.markdown(body=message["content"])

    # Handle user input
    prompt: str | None = st.chat_input(placeholder="Ask a question about the document")
    if prompt:
        handle_chat_interaction(prompt=prompt, table=table)


def handle_chat_interaction(prompt: str, table: Table) -> None:
    """Handles user input, fetches context, and returns a response."""
    # Display user message
    with st.chat_message(name="user"):
        st.markdown(body=prompt)

    # Append user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_chat_history(file_name=table.name, messages=st.session_state.messages)

    # Retrieve relevant context
    with st.status(label="Searching document...", expanded=False):
        context: str = get_context(query=prompt, table=table)
        display_search_results(context=context)

    # Display assistant response
    with st.chat_message(name="assistant"):
        response: str = get_chat_response(
            client=client,
            model_name=cfgs["LLM"]["MODEL"],
            temperature=cfgs["LLM"]["TEMPERATURE"],
            messages=st.session_state.messages,
            context=context,
        )

    # Append assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    save_chat_history(file_name=table.name, messages=st.session_state.messages)


def display_search_results(context: str) -> None:
    """Formats and displays search results from the document."""
    st.markdown(
        """
        <style>
        .search-result {
            margin: 10px 0;
            padding: 10px;
            border-radius: 4px;
            background-color: #f0f2f6;
        }
        .search-result summary {
            cursor: pointer;
            color: #0f52ba;
            font-weight: 500;
        }
        .search-result summary:hover {
            color: #1e90ff;
        }
        .metadata {
            font-size: 0.9em;
            color: #666;
            font-style: italic;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.write("Found relevant sections:")
    for chunk in context.split(sep="\n\n"):
        parts: list[str] = chunk.split(sep="\n")
        text: str = parts[0]
        metadata: dict[str, str] = {
            line.split(sep=": ")[0]: line.split(sep=": ")[1] for line in parts[1:] if ": " in line
        }

        source: str = metadata.get("Source", "Unknown source")
        title: str = metadata.get("Title", "Untitled section")

        st.markdown(
            body=f"""
            <div class="search-result">
                <details>
                    <summary>{source}</summary>
                    <div class="metadata">Section: {title}</div>
                    <div style="margin-top: 8px;">{text}</div>
                </details>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()

# Usage
# uv run streamlit run src/app/app.py
