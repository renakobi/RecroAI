import json
from typing import Dict, Any

from .openai_client import get_client, get_model
from .prompts import SCORING_SYSTEM_PROMPT
from .llm_validation import validate_scoring_payload


def score_candidate(job_criteria: dict, candidate_profile: str) -> Dict[str, Any]:
    """
    Score a candidate against job criteria using LLM.
    
    Returns:
        {
            "category_scores": {
                "skills_score": int,
                "experience_score": int,
                "education_score": int,
                "company_match_score": int
            },
            "total_score": int,
            "explanation": str
        }
    """
    try:
        client = get_client()
    except ValueError as e:
        raise ValueError(f"Cannot score candidate: {str(e)}")
    model = get_model()

    user_prompt = f"""
Job criteria (JSON):
{json.dumps(job_criteria, ensure_ascii=False)}

Candidate profile:
{candidate_profile}

Return JSON EXACTLY:
{{
  "category_scores": {{
    "skills_score": 0,
    "experience_score": 0,
    "education_score": 0,
    "company_match_score": 0
  }},
  "total_score": 0,
  "explanation": "short neutral explanation"
}}

Rules:
- All scores are integers from 0 to 100
- Do not assume missing information
- Penalize vague or inflated claims
"""

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SCORING_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw = response.choices[0].message.content.strip()
    
    # Defensive cleanup for OpenRouter / free models (may return markdown code blocks)
    if raw.startswith("```"):
        raw = raw.strip("```").replace("json", "").strip()
    if raw.startswith("`"):
        raw = raw.strip("`").strip()

    data = json.loads(raw)
    validate_scoring_payload(data)
    return data
