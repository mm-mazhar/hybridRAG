from pathlib import Path

import lancedb
from lancedb.table import Table


def connect(uri: Path | str) -> lancedb.DBConnection:
    """Open (and create) a local LanceDB directory."""
    path = Path(uri)
    path.mkdir(parents=True, exist_ok=True)
    return lancedb.connect(uri=str(path))


def list_tables(db: lancedb.DBConnection) -> list[str]:
    return list(db.table_names())


def open_table(db: lancedb.DBConnection, name: str) -> Table:
    return db.open_table(name=name)


def drop_table(db: lancedb.DBConnection, name: str) -> None:
    db.drop_table(name=name)
