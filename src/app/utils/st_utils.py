# """
# st_utils.py
# Created on Dec 17, 2024
# @ Author: Mazhar
# ""

import json
import os
from typing import Any

import lancedb
import numpy as np
import streamlit as st
from lancedb.table import Table
from openai import Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk


# Initialize LanceDB connection
@st.cache_resource
def init_db(db_uri: str, table_name: str) -> Table:
    """Initialize database connection.

    Returns:
        LanceDB table object
    """
    # Ensure the database directory exists
    db_path: str = os.path.abspath(
        path=os.path.join(os.path.dirname(p=__file__), "../../../", db_uri)
    )
    os.makedirs(name=db_path, exist_ok=True)

    # Connect to the database
    db: lancedb.DBConnection = lancedb.connect(uri=db_path)
    return db.open_table(name=table_name)


def get_context(query: str, table, num_results: int = 3) -> str:
    """Search the database for relevant context.

    Args:
        query: User's question
        table: LanceDB table object
        num_results: Number of results to return

    Returns:
        str: Concatenated context from relevant chunks with source information
    """
    results: Any = table.search(query).limit(num_results).to_pandas()
    contexts: list[str] = []

    for _, row in results.iterrows():
        # Extract metadata
        filename: Any = row["metadata"]["filename"]
        page_numbers: Any = row["metadata"]["page_numbers"]
        title: Any = row["metadata"]["title"]

        # Build source citation
        source_parts: list[Any] = []
        if filename:
            source_parts.append(filename)
        # Check if page_numbers exists and is not empty
        if isinstance(page_numbers, (list, np.ndarray)) and len(page_numbers) > 0:
            page_str = ", ".join(str(p) for p in page_numbers)
            source_parts.append(f"p. {page_str}")

        source: str = f"\nSource: {' - '.join(source_parts)}"
        if title:
            source += f"\nTitle: {title}"

        contexts.append(f"{row['text']}{source}")

    return "\n\n".join(contexts)


def get_chat_response(
    client,
    model_name: str,
    messages: list[dict[str, str]],
    temperature: float,
    context: str,
) -> str:
    """Get streaming response from OpenAI API.

    Args:
        messages: Chat history
        context: Retrieved context from database

    Returns:
        str: Model's response
    """
    system_prompt: str = f"""You are a helpful assistant that answers questions from given context.
    Use only the information from the context to answer questions. If you're unsure or the context
    doesn't contain the relevant information, say so.
    
    Context:
    {context}
    """

    messages_with_context: list[Any] = [
        {"role": "system", "content": system_prompt},
        *messages,
    ]

    # Create the streaming response
    stream: Stream[ChatCompletionChunk] = client.chat.completions.create(
        model=model_name,
        messages=messages_with_context,
        temperature=temperature,
        stream=True,
    )

    # Use Streamlit's built-in streaming capability
    response: str = "".join(st.write_stream(stream=stream))
    return response


# Load chat history
def load_chat_history(file_name: str = "") -> list[dict[str, str]]:
    """Load chat history for specific table.

    Args:
        table_name: Name of the table to load history for

    Returns:
        List[Dict[str, str]]: Chat history for the table
    """
    # Create chat histories directory if it doesn't exist
    history_dir: str = os.path.join(os.path.dirname(p=__file__), "../../../", "chat_histories")
    os.makedirs(name=history_dir, exist_ok=True)

    # Create table-specific history file path
    history_file: str = os.path.join(
        history_dir, f"{clean_table_name(name=file_name)}_history.json"
    )

    if not os.path.exists(path=history_file):
        # Create an empty file if it doesn't exist
        open(history_file, "w").close()  # 'w' mode creates the file if it's missing

    try:
        with open(file=history_file) as f:
            return json.load(fp=f)
    except json.JSONDecodeError:
        # Handle case where the file is empty or contains invalid JSON
        return []  # Return empty list


# Save chat history
def save_chat_history(file_name: str = "", messages: list[dict[str, str]] | None = None) -> None:
    """Save chat history for specific table.

    Args:
        file_name: Name of the file to save history for
        messages: Chat messages to save
    """
    if messages is None:
        messages = []

    # Create chat histories directory if it doesn't exist
    history_dir: str = os.path.join(os.path.dirname(p=__file__), "../../../", "chat_histories")
    os.makedirs(name=history_dir, exist_ok=True)

    # Create table-specific history file path
    history_file: str = os.path.join(
        history_dir, f"{clean_table_name(name=file_name)}_history.json"
    )

    with open(file=history_file, mode="w") as f:
        json.dump(obj=messages, fp=f)


def clean_table_name(name: str) -> str:
    """Clean and format table name.

    Args:
        name: Raw table name

    Returns:
        str: Cleaned table name
    """
    # Remove special characters and spaces, replace with underscore
    cleaned: str = "".join(c if c.isalnum() else "_" for c in name)
    # Remove multiple consecutive underscores
    cleaned = "_".join(filter(None, cleaned.split(sep="_")))
    # Convert to lowercase
    return cleaned.lower()
