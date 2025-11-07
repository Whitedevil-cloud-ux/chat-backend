import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is not set in the environment!")

client = Groq(api_key=api_key)
MODEL = "groq/compound"


def _chat(messages, temperature=0.4, max_tokens=200):
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def detect_intent(user_text: str) -> str:
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    'Classify this message as exactly one word: "chat", "summary", or "knowledge". '
                    'No explanation. No punctuation. Only one of these three words.'
                ),
            },
            {"role": "user", "content": user_text},
        ]
        resp = _chat(messages, temperature=0, max_tokens=1)
        return resp.choices[0].message.content.strip().lower()
    except Exception:
        return "chat"


def generate_summary(user_prompt: str) -> str:
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You summarize text into 1–3 sentences. No bullets. No headings. Plain text only."
                ),
            },
            {"role": "user", "content": user_prompt},
        ]
        resp = _chat(messages, temperature=0.3, max_tokens=180)
        return resp.choices[0].message.content.strip()
    except Exception:
        return "Sorry, I couldn't generate a summary."


def answer_knowledge_question(user_prompt: str) -> str:
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You answer factual questions in 1–2 sentences. No bullets. No reasoning. Plain text only."
                ),
            },
            {"role": "user", "content": user_prompt},
        ]
        resp = _chat(messages, temperature=0.4, max_tokens=120)
        return resp.choices[0].message.content.strip()
    except Exception:
        return "I couldn't find a direct answer."


def generate_followup_questions(context: str) -> list[str]:
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "Generate exactly two short follow-up questions. No bullets. No explanation. One per line."
                ),
            },
            {"role": "user", "content": f"Reply: {context}"},
        ]
        resp = _chat(messages, temperature=0.5, max_tokens=80)
        raw = resp.choices[0].message.content.strip()
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        return lines[:2]
    except Exception:
        return []
