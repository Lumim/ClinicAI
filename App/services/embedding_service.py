from openai import OpenAI

from app.core.config import get_settings
from app.core.exceptions import EmbeddingError

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)


def embed_text(text: str) -> list[float]:
    try:
        response = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text,
        )
        return response.data[0].embedding
    except Exception as exc:
        raise EmbeddingError(f"Failed to generate embedding: {exc}") from exc


def embed_texts(texts: list[str]) -> list[list[float]]:
    try:
        response = client.embeddings.create(
            model=settings.openai_embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]
    except Exception as exc:
        raise EmbeddingError(f"Failed to generate embeddings: {exc}") from exc