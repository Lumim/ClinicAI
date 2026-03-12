from openai import OpenAI

from app.core.config import get_settings
from app.core.exceptions import LLMGenerationError

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)


SYSTEM_PROMPT = """You are a clinical knowledge assistant for doctors.
Use only the retrieved document context provided.
If the answer is not supported by the context, say that the available documents do not provide enough evidence.
Do not invent facts.
Do not provide autonomous diagnosis or unsupported treatment recommendations.
Cite sources in a concise way using the provided document titles and page/section metadata.
"""


def build_context(chunks: list[dict]) -> str:
    context_parts: list[str] = []

    for idx, chunk in enumerate(chunks, start=1):
        title = chunk.get("title", "Unknown document")
        page_number = chunk.get("page_number")
        section_title = chunk.get("section_title")
        content = chunk.get("content", "")

        meta = f"[Source {idx}] Title: {title}"
        if page_number is not None:
            meta += f" | Page: {page_number}"
        if section_title:
            meta += f" | Section: {section_title}"

        context_parts.append(f"{meta}\n{content}")

    return "\n\n".join(context_parts)


def generate_grounded_answer(question: str, chunks: list[dict]) -> tuple[str, bool]:
    if not chunks:
        return (
            "I cannot provide a source-supported answer because no relevant indexed documents were found.",
            True,
        )

    context = build_context(chunks)

    user_prompt = f"""Question:
{question}

Retrieved context:
{context}

Instructions:
- Answer only from the retrieved context.
- If the answer is incomplete or unsupported, say so clearly.
- Keep the answer concise and clinically neutral.
- Do not claim certainty beyond the provided evidence.
"""

    try:
        response = client.chat.completions.create(
            model=settings.openai_chat_model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        answer = response.choices[0].message.content.strip()

        refused = "do not provide enough evidence" in answer.lower() or "cannot provide" in answer.lower()

        return answer, refused
    except Exception as exc:
        raise LLMGenerationError(f"Failed to generate answer: {exc}") from exc