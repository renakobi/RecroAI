import json
import os
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, ValidationError, Field
import httpx
from ..config import settings


class CategoryScore(BaseModel):
    """Individual category score"""
    score: float = Field(ge=0.0, le=100.0, description="Score from 0 to 100")
    reasoning: str = Field(min_length=10, description="Reasoning for this score")


class ScoringResponse(BaseModel):
    """Strict JSON structure for LLM scoring response"""
    total_score: float = Field(ge=0.0, le=100.0, description="Overall score from 0 to 100")
    category_scores: Dict[str, CategoryScore] = Field(
        description="Dictionary of category names to scores"
    )
    explanation: str = Field(
        min_length=50,
        description="Detailed explanation of the scoring (minimum 50 characters)"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="List of candidate strengths"
    )
    weaknesses: List[str] = Field(
        default_factory=list,
        description="List of candidate weaknesses"
    )


class LLMScoringService:
    """Service for scoring candidates using LLM with strict JSON output"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") or (getattr(settings, 'OPENAI_API_KEY', None) if hasattr(settings, 'OPENAI_API_KEY') else None)
        self.api_base = os.getenv("OPENAI_API_BASE") or getattr(settings, 'OPENAI_API_BASE', 'https://api.openai.com/v1')
        self.model = os.getenv("LLM_MODEL") or getattr(settings, 'LLM_MODEL', 'gpt-4o-mini')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment variable or config")
    
    def _create_scoring_prompt(self, job_criteria: Dict[str, Any], candidate_profile: str) -> str:
        """Create a prompt that forces structured JSON output"""
        prompt = f"""You are a technical recruiter evaluating a candidate against a job posting.

JOB CRITERIA:
{json.dumps(job_criteria, indent=2)}

CANDIDATE PROFILE:
{candidate_profile}

Evaluate the candidate and provide a structured assessment. You MUST respond with valid JSON only, following this exact structure:
{{
  "total_score": <float between 0-100>,
  "category_scores": {{
    "<category_name>": {{
      "score": <float between 0-100>,
      "reasoning": "<detailed reasoning>"
    }},
    ...
  }},
  "explanation": "<comprehensive explanation, minimum 50 characters>",
  "strengths": ["<strength1>", "<strength2>", ...],
  "weaknesses": ["<weakness1>", "<weakness2>", ...]
}}

Categories to evaluate (create scores for each):
- Technical Skills: Match between candidate skills and job requirements
- Experience: Relevance and depth of work experience
- Education: Educational background alignment
- Cultural Fit: Based on profile summary and overall fit

IMPORTANT:
- Return ONLY valid JSON, no markdown, no code blocks, no additional text
- All scores must be floats between 0 and 100
- Explanation must be at least 50 characters
- Each category must have a score and reasoning
- Be specific and detailed in your reasoning

JSON Response:"""
        return prompt
    
    async def score_candidate(
        self,
        job_criteria: Dict[str, Any],
        candidate_profile: str
    ) -> ScoringResponse:
        """
        Score a candidate against job criteria using LLM.
        
        Returns validated ScoringResponse with structured scores.
        Raises ValueError if JSON is invalid or doesn't match schema.
        """
        prompt = self._create_scoring_prompt(job_criteria, candidate_profile)
        
        # Call LLM API with JSON mode
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a technical recruiter. Always respond with valid JSON only, no markdown, no code blocks, no additional text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"}  # Force JSON output
            }
            
            try:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Parse and validate JSON
                try:
                    # Remove any markdown code blocks if present
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.startswith("```"):
                        content = content[3:]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                    
                    json_data = json.loads(content)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON response from LLM: {str(e)}\nResponse: {content[:500]}")
                
                # Validate against Pydantic schema
                try:
                    scoring_response = ScoringResponse(**json_data)
                except ValidationError as e:
                    raise ValueError(f"JSON response doesn't match schema: {str(e)}\nJSON: {json.dumps(json_data, indent=2)}")
                
                return scoring_response
                
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if e.response else str(e)
                raise ValueError(f"LLM API error: {e.response.status_code} - {error_detail}")
            except httpx.RequestError as e:
                raise ValueError(f"LLM API request failed: {str(e)}")
    
    def score_candidate_sync(
        self,
        job_criteria: Dict[str, Any],
        candidate_profile: str
    ) -> ScoringResponse:
        """
        Synchronous version using httpx sync client.
        Use this if you're not in an async context.
        """
        import httpx as sync_httpx
        
        prompt = self._create_scoring_prompt(job_criteria, candidate_profile)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a technical recruiter. Always respond with valid JSON only, no markdown, no code blocks, no additional text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        
        with sync_httpx.Client(timeout=60.0) as client:
            try:
                response = client.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Parse and validate JSON
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                json_data = json.loads(content)
                
                # Validate against Pydantic schema
                scoring_response = ScoringResponse(**json_data)
                return scoring_response
                
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON response from LLM: {str(e)}\nResponse: {content[:500]}")
            except ValidationError as e:
                raise ValueError(f"JSON response doesn't match schema: {str(e)}\nJSON: {json.dumps(json_data, indent=2)}")
            except sync_httpx.HTTPStatusError as e:
                error_detail = e.response.text if e.response else str(e)
                raise ValueError(f"LLM API error: {e.response.status_code} - {error_detail}")
            except sync_httpx.RequestError as e:
                raise ValueError(f"LLM API request failed: {str(e)}")


# Singleton instance
_scoring_service: Optional[LLMScoringService] = None


def get_scoring_service() -> LLMScoringService:
    """Get or create scoring service instance"""
    global _scoring_service
    if _scoring_service is None:
        _scoring_service = LLMScoringService()
    return _scoring_service

