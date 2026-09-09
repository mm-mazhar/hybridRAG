import tempfile
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from api.deps import AppContext, get_ctx
from api.routes_documents import require_http_url
from api.schemas import IngestResponse, UrlIngestRequest, WebsiteIngestRequest
from processing.names import clean_table_name, domain_label
from processing.preprocessor import load_sitemap
from rag.indexer import index_docling_documents, index_source

router = APIRouter()

_PDF_MAGIC = b"%PDF"


def _http_ingest_error(exc: BaseException) -> HTTPException:
    if isinstance(exc, HTTPException):
        return exc
    if isinstance(exc, ValueError):
        return HTTPException(status_code=422, detail=str(exc))
    return HTTPException(
        status_code=422,
        detail=f"Could not index this source: {type(exc).__name__}: {exc}"[:280],
    )


def _index_path(
    ctx: AppContext,
    source_path: str,
    table_name: str,
    source_type: str,
    source_name: str,
) -> IngestResponse:
    try:
        table = index_source(
            db=ctx.db,
            table_name=table_name,
            source_path=source_path,
            max_tokens=ctx.settings.llm.max_tokens,
            embedder=ctx.embedder,
            mode=ctx.settings.vector_db.mode,
            source_name=source_name,
        )
    except Exception as exc:
        raise _http_ingest_error(exc) from exc
    row_count = table.count_rows()
    ctx.memory.upsert_document(
        document_id=table_name,
        source_type=source_type,
        source_name=source_name,
        row_count=row_count,
    )
    return IngestResponse(
        document_id=table_name,
        row_count=row_count,
        source_type=source_type,
        source_name=source_name,
    )


@router.post("/ingest/pdf", response_model=IngestResponse)
async def ingest_pdf(
    ctx: AppContext = Depends(get_ctx),
    file: UploadFile = File(...),
) -> IngestResponse:
    filename = file.filename or "upload.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    payload = await file.read()
    if len(payload) > ctx.settings.app.max_upload_bytes:
        raise HTTPException(status_code=413, detail="PDF exceeds the upload size limit.")
    if not payload.startswith(_PDF_MAGIC):
        raise HTTPException(status_code=400, detail="File does not look like a PDF.")

    table_name = f"pdf_{clean_table_name(filename)}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(payload)
        tmp_path = tmp.name
    try:
        return _index_path(
            ctx=ctx,
            source_path=tmp_path,
            table_name=table_name,
            source_type="pdf",
            source_name=filename,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/ingest/url", response_model=IngestResponse)
def ingest_url(
    body: UrlIngestRequest,
    ctx: AppContext = Depends(get_ctx),
) -> IngestResponse:
    require_http_url(body.url)
    host = urlparse(body.url).netloc
    label = domain_label(host, ctx.settings.ingest.common_tlds)
    table_name = f"url_{clean_table_name(label or host)}"
    return _index_path(
        ctx=ctx,
        source_path=body.url,
        table_name=table_name,
        source_type="url",
        source_name=body.url,
    )


@router.post("/ingest/website", response_model=IngestResponse)
def ingest_website(
    body: WebsiteIngestRequest,
    ctx: AppContext = Depends(get_ctx),
) -> IngestResponse:
    require_http_url(body.base_url)
    host = urlparse(body.base_url).netloc
    label = domain_label(host, ctx.settings.ingest.common_tlds)
    table_name = f"site_{clean_table_name(label or host)}"
    try:
        documents = load_sitemap(
            base_url=body.base_url,
            sitemap_filename=body.sitemap_filename,
        )
        if not documents:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No documents extracted from this site. Check the origin URL or sitemap name."
                ),
            )
        table = index_docling_documents(
            db=ctx.db,
            table_name=table_name,
            documents=documents,
            max_tokens=ctx.settings.llm.max_tokens,
            embedder=ctx.embedder,
            mode=ctx.settings.vector_db.mode,
            source_name=body.base_url,
        )
    except Exception as exc:
        raise _http_ingest_error(exc) from exc
    row_count = table.count_rows()
    ctx.memory.upsert_document(
        document_id=table_name,
        source_type="website",
        source_name=body.base_url,
        row_count=row_count,
    )
    return IngestResponse(
        document_id=table_name,
        row_count=row_count,
        source_type="website",
        source_name=body.base_url,
    )
