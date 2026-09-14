"""
Thin wrapper around Google Gemini (via LangChain) used to turn deterministic,
data-grounded analysis into natural-language narratives (weekly summaries,
risk descriptions, recommendation phrasing).

IMPORTANT: The LLM is NEVER the source of truth for risk/priority
*decisions* - all numbers, statuses and dependency relationships are
computed by the deterministic rule engine in app/agents/engine.py from the
actual project data. The LLM is only used to phrase that already-computed,
explainable output as readable prose. If no GOOGLE_API_KEY is configured,
a deterministic template-based narrator is used instead, so the system
remains fully functional without any external API key.
"""
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger("llm_service")

_llm = None
_llm_init_attempted = False


def _get_llm():
    global _llm, _llm_init_attempted
    if _llm_init_attempted:
        return _llm
    _llm_init_attempted = True
    if not settings.GOOGLE_API_KEY:
        logger.info("GOOGLE_API_KEY not set - using deterministic narrator fallback.")
        return None
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        _llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.2,
            max_retries=1,
        )
        logger.info("Gemini LLM initialized (%s).", settings.GEMINI_MODEL)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to initialize Gemini LLM: %s. Falling back.", exc)
        _llm = None
    return _llm


def is_llm_available() -> bool:
    return _get_llm() is not None


def extract_text_content(content) -> str:
    """Extract plain text from various response content shapes (str, list of dicts/blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(part.get("text", "") or "")
            elif hasattr(part, "text"):
                parts.append(str(part.text))
            else:
                parts.append(str(part))
        return "".join(parts)
    if isinstance(content, dict):
        return content.get("text", "") or str(content)
    return str(content)


def get_llm():
    return _get_llm()


def generate_narrative(prompt: str, fallback_text: str) -> str:
    """Generate a natural-language narrative from a grounded prompt.
    Falls back to `fallback_text` (already human-readable) if no LLM."""
    llm = _get_llm()
    if llm is None:
        return fallback_text
    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(
                content=(
                    "You are a project management reporting assistant. "
                    "You are given ALREADY-COMPUTED, factual project data "
                    "(risks, statuses, dependencies). Rephrase it into clear, "
                    "concise, professional project-management language. "
                    "Do NOT invent any fact, number, date, or task name that "
                    "is not present in the input. Do not add new risks."
                )
            ),
            HumanMessage(content=prompt),
        ]
        response = llm.invoke(messages)
        raw = response.content if hasattr(response, "content") else response
        text = extract_text_content(raw)
        return text.strip() or fallback_text
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM generation failed (%s); using fallback text.", exc)
        return fallback_text

