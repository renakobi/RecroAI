REQUIRED_CATEGORY_KEYS = {
    "skills_score",
    "experience_score",
    "education_score",
    "company_match_score",
}

def validate_scoring_payload(data: dict):
    if "category_scores" not in data:
        raise ValueError("Missing category_scores")

    if "total_score" not in data:
        raise ValueError("Missing total_score")

    if "explanation" not in data:
        raise ValueError("Missing explanation")

    scores = data["category_scores"]

    if set(scores.keys()) != REQUIRED_CATEGORY_KEYS:
        raise ValueError("Invalid category_scores keys")

    for k, v in scores.items():
        if not isinstance(v, (int, float)) or not 0 <= v <= 100:
            raise ValueError(f"{k} must be between 0 and 100")

    if not isinstance(data["total_score"], (int, float)) or not 0 <= data["total_score"] <= 100:
        raise ValueError("total_score must be between 0 and 100")
