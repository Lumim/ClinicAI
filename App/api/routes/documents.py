from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.utils import generate_storage_filename, validate_file_extension
from app.schemas.document import DocumentIndexResponse, DocumentListResponse, DocumentResponse
from app.services.document_service import create_document_record, list_documents
from app.services.indexing_service import index_document_by_id

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    source_name: str = Form(...),
    source_type: str = Form(...),
    specialty: str = Form(...),
    version_label: str = Form(...),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    try:
        validate_file_extension(file.filename)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    storage_filename = generate_storage_filename(file.filename)
    upload_dir = Path("data/raw")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / storage_filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    document = create_document_record(
        db=db,
        title=title,
        source_name=source_name,
        source_type=source_type,
        specialty=specialty,
        version_label=version_label,
        file_path=str(file_path),
    )
    return document


@router.post("/{document_id}/index", response_model=DocumentIndexResponse)
def index_document(
    document_id: str,
    db: Session = Depends(get_db),
) -> DocumentIndexResponse:
    try:
        result = index_document_by_id(db=db, document_id=document_id)
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index document: {exc}",
        ) from exc


@router.get("", response_model=DocumentListResponse)
def get_documents(db: Session = Depends(get_db)) -> DocumentListResponse:
    documents = list_documents(db=db)
    return DocumentListResponse(documents=documents)