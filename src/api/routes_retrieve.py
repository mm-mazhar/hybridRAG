from fastapi import APIRouter, Depends, HTTPException

from api.deps import AppContext, get_ctx
from api.schemas import ChunkOut, RetrieveRequest, RetrieveResponse
from inference.inference_engine import retrieve_for_query
from rag.vector_store import list_tables, open_table

router = APIRouter()


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve(body: RetrieveRequest, ctx: AppContext = Depends(get_ctx)) -> RetrieveResponse:
    if body.document_id not in list_tables(ctx.db):
        raise HTTPException(status_code=404, detail="Document index not found.")
    table = open_table(ctx.db, body.document_id)
    limit = body.limit or ctx.settings.vector_db.limit
    bundle = retrieve_for_query(
        table=table,
        embedder=ctx.embedder,
        query=body.query,
        limit=limit,
        settings=ctx.settings,
    )
    return RetrieveResponse(
        chunks=[
            ChunkOut(
                text=hit.text,
                filename=hit.filename,
                page_numbers=hit.page_numbers,
                title=hit.title,
                source=hit.source,
            )
            for hit in bundle.hits
        ],
        hybrid=bundle.trace.hybrid,
        fts=bundle.trace.fts,
        multi_query=bundle.trace.multi_query,
        queries=bundle.trace.queries,
    )
