import json
from typing import Dict, Any
from .openai_client import get_client, get_model
from .prompts import INJECTION_SYSTEM_PROMPT

SUSPICIOUS_PATTERNS = [
    "ignore previous instructions",
    "system message",
    "developer message",
    "act as",
    "override",
    "jailbreak",
]


def detect_authenticity(text: str, use_llm: bool = True) -> Dict[str, Any]:
    """
    Detect prompt injection attempts and suspicious content.

    Returns:
        {
            "is_suspicious": bool,
            "risk_score": float,
            "reason": str
        }
    """
    text_lower = text.lower()
    hits = sum(1 for p in SUSPICIOUS_PATTERNS if p in text_lower)
    base_risk = min(1.0, hits / 3)

    # No suspicious patterns → clean result
    if base_risk == 0:
        return {
            "is_suspicious": False,
            "risk_score": 0.0,
            "reason": ""
        }

    if use_llm:
        try:
            client = get_client()
            model = get_model()
        except ValueError:
            # LLM not configured → heuristic only
            return {
                "is_suspicious": True,
                "risk_score": base_risk,
                "reason": "Heuristic check only (LLM not configured)"
            }

        prompt = f"""
Text:
{text}

Return JSON ONLY:
{{
  "is_suspicious": true,
  "risk_score": 0.0,
  "reason": "short reason"
}}

Rules:
- risk_score must be between 0.0 and 1.0
- Be strict but fair
"""

        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {"role": "system", "content": INJECTION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        # Defensive cleanup for OpenRouter / free models
        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.strip("```").replace("json", "").strip()

        data = json.loads(raw)

        risk_score = max(base_risk, float(data.get("risk_score", 0.0)))

        return {
            "is_suspicious": bool(data.get("is_suspicious", True)),
            "risk_score": risk_score,
            "reason": data.get("reason", "")
        }

    # Heuristic-only fallback
    return {
        "is_suspicious": True,
        "risk_score": base_risk,
        "reason": "Heuristic check detected suspicious patterns"
    }
