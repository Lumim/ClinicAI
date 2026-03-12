from sqlalchemy.orm import Session

from app.db.models import DocumentChunk
from app.schemas.document import DocumentIndexResponse
from app.services.chunking_service import chunk_documents
from app.services.document_service import get_document_by_id, update_document_status
from app.services.embedding_service import embed_texts
from app.services.parser_service import parse_document


def index_document_by_id(db: Session, document_id: str) -> DocumentIndexResponse:
    document = get_document_by_id(db=db, document_id=document_id)
    if not document:
        raise ValueError("Document not found")

    parsed_pages = parse_document(document.file_path)
    update_document_status(db=db, document=document, status="parsed")

    chunks = chunk_documents(parsed_pages=parsed_pages)
    if not chunks:
        raise ValueError("No content found to index")

    embeddings = embed_texts([chunk["content"] for chunk in chunks])

    db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()

    chunk_rows: list[DocumentChunk] = []
    for chunk, embedding in zip(chunks, embeddings, strict=False):
        row = DocumentChunk(
            document_id=document.id,
            chunk_index=chunk["chunk_index"],
            page_number=chunk["page_number"],
            section_title=chunk["section_title"],
            content=chunk["content"],
            token_count=chunk["token_count"],
            embedding=embedding,
        )
        chunk_rows.append(row)

    db.add_all(chunk_rows)
    db.commit()

    update_document_status(db=db, document=document, status="indexed")

    return DocumentIndexResponse(
        document_id=document.id,
        status="indexed",
        chunks_created=len(chunk_rows),
    )