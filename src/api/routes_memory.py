from fastapi import APIRouter, Depends, HTTPException, Query

from api.deps import AppContext, get_ctx
from api.schemas import MemorySaveRequest

router = APIRouter()


@router.get("/memory")
def load_memory(
    ctx: AppContext = Depends(get_ctx),
    document_id: str = Query(min_length=1, max_length=200),
) -> dict[str, object]:
    return {"document_id": document_id, "messages": ctx.memory.load_messages(document_id)}


@router.post("/memory")
def save_memory(body: MemorySaveRequest, ctx: AppContext = Depends(get_ctx)) -> dict[str, str]:
    if not body.document_id.strip():
        raise HTTPException(status_code=400, detail="document_id is required.")
    ctx.memory.save_messages(document_id=body.document_id, messages=body.messages)
    return {"status": "saved"}
