"""Index a local file into LanceDB using config/model_config.yaml."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.llm_client import create_embedding_client  # noqa: E402
from core.settings import get_settings  # noqa: E402
from processing.names import clean_table_name  # noqa: E402
from rag.embedder import Embedder  # noqa: E402
from rag.indexer import index_source  # noqa: E402
from rag.vector_store import connect  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build LanceDB embeddings for a source file or URL."
    )
    parser.add_argument("source", help="Local path or http(s) URL")
    parser.add_argument("--table", default="", help="LanceDB table name")
    args = parser.parse_args()

    settings = get_settings()
    table_name = args.table or f"src_{clean_table_name(Path(args.source).name)}"
    embedder = Embedder.from_settings(settings, create_embedding_client(settings))
    table = index_source(
        db=connect(settings.vector_db_path),
        table_name=table_name,
        source_path=args.source,
        max_tokens=settings.llm.max_tokens,
        embedder=embedder,
        mode=settings.vector_db.mode,
    )
    print(f"Indexed {table.count_rows()} chunks into {table_name}")


if __name__ == "__main__":
    main()
