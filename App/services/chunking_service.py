from typing import Any


def chunk_documents(
    parsed_pages: list[dict[str, Any]],
    chunk_size: int = 1200,
    chunk_overlap: int = 200,
) -> list[dict]:
    """
    Character-based chunking for MVP.
    Later you can replace this with tokenizer-based chunking.
    """
    chunks: list[dict] = []

    for page in parsed_pages:
        text = page["text"]
        page_number = page.get("page_number")
        section_title = page.get("section_title")

        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "chunk_index": chunk_index,
                        "page_number": page_number,
                        "section_title": section_title,
                        "content": chunk_text,
                        "token_count": estimate_token_count(chunk_text),
                    }
                )

            if end >= len(text):
                break

            start += chunk_size - chunk_overlap
            chunk_index += 1

    return chunks


def estimate_token_count(text: str) -> int:
    """
    Rough token estimate for MVP.
    """
    return max(1, len(text) // 4)