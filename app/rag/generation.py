from openai import OpenAI

from app.core.config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """You are a knowledge assistant. Answer only from the supplied context.
If the context is insufficient, say that there is not enough evidence in the knowledge base.
Do not invent policies, dates, people, systems, or procedures. Keep the answer concise and practical.
"""


def generate_answer(question: str, context_items: list[tuple[str, str]]) -> str:
    if not context_items:
        return "There is not enough evidence in the knowledge base to answer this question."
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    context = "\n\n".join(
        f"SOURCE: {document}\nCONTENT: {content}" for document, content in context_items
    )
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_chat_model,
        instructions=SYSTEM_PROMPT,
        input=f"QUESTION:\n{question}\n\nCONTEXT:\n{context}",
    )
    return response.output_text.strip()
