from sqlalchemy.orm import Session

from app.db.models import Document


def create_document_record(
    db: Session,
    title: str,
    source_name: str,
    source_type: str,
    specialty: str,
    version_label: str,
    file_path: str,
    publication_date=None,
) -> Document:
    document = Document(
        title=title,
        source_name=source_name,
        source_type=source_type,
        specialty=specialty,
        version_label=version_label,
        publication_date=publication_date,
        file_path=file_path,
        status="uploaded",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def get_document_by_id(db: Session, document_id: str) -> Document | None:
    return db.query(Document).filter(Document.id == document_id).first()


def list_documents(db: Session) -> list[Document]:
    return db.query(Document).order_by(Document.created_at.desc()).all()


def update_document_status(db: Session, document: Document, status: str) -> Document:
    document.status = status
    db.add(document)
    db.commit()
    db.refresh(document)
    return document