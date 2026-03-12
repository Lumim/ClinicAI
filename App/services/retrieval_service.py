from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import Document, DocumentChunk
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem
from app.services.embedding_service import embed_text


def semantic_search(db: Session, payload: SearchRequest) -> SearchResponse:
    query_embedding = embed_text(payload.query)

    stmt: Select = (
        select(DocumentChunk, Document, DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"))
        .join(Document, Document.id == DocumentChunk.document_id)
    )

    if payload.specialty:
        stmt = stmt.where(Document.specialty == payload.specialty)

    if payload.document_ids:
        stmt = stmt.where(Document.id.in_(payload.document_ids))

    stmt = stmt.order_by(DocumentChunk.embedding.cosine_distance(query_embedding)).limit(payload.top_k)

    rows = db.execute(stmt).all()

    results: list[SearchResultItem] = []
    for chunk, document, distance in rows:
        similarity_score = 1.0 - float(distance) if distance is not None else 0.0
        results.append(
            SearchResultItem(
                chunk_id=chunk.id,
                document_id=document.id,
                title=document.title,
                content=chunk.content,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                similarity_score=similarity_score,
            )
        )

    return SearchResponse(
        query=payload.query,
        results=results,
        total_results=len(results),
    )


def retrieve_chunks_for_question(
    db: Session,
    question: str,
    top_k: int = 5,
    specialty: str | None = None,
    document_ids: list | None = None,
) -> list[dict]:
    payload = SearchRequest(
        query=question,
        specialty=specialty,
        top_k=top_k,
        document_ids=document_ids or [],
    )
    response = semantic_search(db=db, payload=payload)

    return [
        {
            "chunk_id": item.chunk_id,
            "document_id": item.document_id,
            "title": item.title,
            "content": item.content,
            "page_number": item.page_number,
            "section_title": item.section_title,
            "similarity_score": item.similarity_score,
        }
        for item in response.results
    ]