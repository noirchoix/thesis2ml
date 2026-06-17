from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.services.agents import list_runs, run_analysis
from app.services.chemistry_knowledge import ALGORITHM_FAMILIES, CHEMISTRY_DATASET_CATEGORIES
from app.services.documents import get_document, ingest_upload, list_documents
from app.services.retrieval import retrieve

router = APIRouter()


class QueryRequest(BaseModel):
    document_id: str
    query: str = Field(min_length=3)
    top_k: int = 8


class AnalysisRequest(BaseModel):
    document_id: str
    query: str = "Find practical ML, product, and commercialization pathways for this chemistry thesis."
    mode: str = "full"


@router.get("/health")
def health() -> dict:
    return {"ok": True, "service": "thesis2ml-chemistry"}


@router.get("/v1/chemistry/datasets")
def chemistry_datasets() -> dict:
    return {"categories": CHEMISTRY_DATASET_CATEGORIES, "algorithm_families": ALGORITHM_FAMILIES}


@router.post("/v1/documents/upload")
async def upload_document(
    file: Annotated[UploadFile, File()],
    field: Annotated[str, Form()] = "chemistry",
) -> dict:
    suffix = (file.filename or "").lower().rsplit(".", 1)[-1]
    if suffix not in {"pdf", "txt", "md"}:
        raise HTTPException(status_code=400, detail="Upload PDF, TXT, or MD thesis files.")
    return {"document": await ingest_upload(file, field)}


@router.get("/v1/documents")
def documents() -> dict:
    return {"documents": list_documents()}


@router.get("/v1/documents/{document_id}")
def document_detail(document_id: str) -> dict:
    document = get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document": document, "runs": list_runs(document_id)}


@router.post("/v1/query")
async def query_document(request: QueryRequest) -> dict:
    document = get_document(request.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    chunks, trace = await retrieve(request.document_id, request.query, request.top_k)
    return {"chunks": chunks, "trace": trace}


@router.post("/v1/analyze")
async def analyze_document(request: AnalysisRequest) -> dict:
    try:
        return await run_analysis(request.document_id, request.query, request.mode)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/v1/runs")
def runs() -> dict:
    return {"runs": list_runs()}
