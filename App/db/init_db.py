from app.db.base import Base
from app.db.models import AnswerLog, Document, DocumentChunk, Feedback, QueryLog, RetrievalLog
from app.db.session import engine


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()