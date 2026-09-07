# """
# 4_search.py
# Created on Dec 17, 2024
# @ Author: Mazhar
# ""

import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.abspath(path=os.path.join(os.path.dirname(p=__file__), "../..")))

import lancedb
import pandas as pd
from lancedb.query import LanceQueryBuilder
from lancedb.table import Table

from configs import cfgs


def connect_to_database(db_uri: str) -> lancedb.DBConnection:
    """
    Connect to the LanceDB database.

    Args:
        db_uri: URI of the database

    Returns:
        lancedb.DBConnection: Database connection
    """
    return lancedb.connect(uri=db_uri)


def load_table(db: lancedb.DBConnection, table_name: str) -> Table:
    """
    Load a table from the database.

    Args:
        db: Database connection
        table_name: Name of the table to load

    Returns:
        Table: LanceDB table
    """
    return db.open_table(name=table_name)


def search_documents(table: Table, query: str, limit: int) -> pd.DataFrame:
    """
    Search documents in the table.

    Args:
        table: LanceDB table
        query: Search query
        limit: Maximum number of results to return

    Returns:
        pd.DataFrame: Search results as a pandas DataFrame
    """
    result: LanceQueryBuilder = table.search(query=query).limit(limit=limit)
    return result.to_pandas()


def main() -> None:
    """Main function to demonstrate usage."""
    # Connect to database
    db: lancedb.DBConnection = connect_to_database(db_uri=cfgs["VECTOR_DB"]["URI"])

    # Load table
    table: Table = load_table(db=db, table_name=cfgs["VECTOR_DB"]["TABLE_NAME"])

    # Search documents
    results: pd.DataFrame = search_documents(
        table=table, query=cfgs["QUERY"], limit=cfgs["VECTOR_DB"]["LIMIT"]
    )

    print(results.head(n=5))


if __name__ == "__main__":
    main()
