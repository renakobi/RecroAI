import json
from typing import Dict, Any, Optional


def normalize_linkedin_profile(linkedin_data: Dict[str, Any]) -> str:
    """
    Normalize LinkedIn profile data into the same format as CSV uploads.
    
    Expected LinkedIn data structure (flexible):
    - name/fullName/firstName+lastName
    - education/educations (list or string)
    - experience/experiences/workExperience (list or string)
    - skills/skillSet (list or string)
    - summary/about/headline
    
    Returns: JSON string matching CSV format: {name, education, experience, skills, summary}
    """
    # Extract name
    name = (
        linkedin_data.get("name") or
        linkedin_data.get("fullName") or
        f"{linkedin_data.get('firstName', '')} {linkedin_data.get('lastName', '')}".strip() or
        linkedin_data.get("profileName") or
        ""
    )
    
    # Extract education
    education_raw = linkedin_data.get("education") or linkedin_data.get("educations")
    if isinstance(education_raw, list):
        # Format list of education entries
        education_parts = []
        for edu in education_raw:
            if isinstance(edu, dict):
                parts = []
                if edu.get("school") or edu.get("schoolName"):
                    parts.append(edu.get("school") or edu.get("schoolName"))
                if edu.get("degree") or edu.get("degreeName"):
                    parts.append(edu.get("degree") or edu.get("degreeName"))
                if edu.get("fieldOfStudy"):
                    parts.append(edu.get("fieldOfStudy"))
                if edu.get("startDate") or edu.get("endDate"):
                    date_range = f"{edu.get('startDate', '')} - {edu.get('endDate', '')}"
                    parts.append(date_range.strip(" -"))
                education_parts.append(", ".join(filter(None, parts)))
            else:
                education_parts.append(str(edu))
        education = "; ".join(education_parts)
    elif isinstance(education_raw, str):
        education = education_raw
    else:
        education = ""
    
    # Extract experience
    experience_raw = (
        linkedin_data.get("experience") or
        linkedin_data.get("experiences") or
        linkedin_data.get("workExperience") or
        linkedin_data.get("positions")
    )
    if isinstance(experience_raw, list):
        # Format list of experience entries
        experience_parts = []
        for exp in experience_raw:
            if isinstance(exp, dict):
                parts = []
                if exp.get("title") or exp.get("position"):
                    parts.append(exp.get("title") or exp.get("position"))
                if exp.get("company") or exp.get("companyName"):
                    parts.append(f"at {exp.get('company') or exp.get('companyName')}")
                if exp.get("description"):
                    parts.append(f"- {exp.get('description')}")
                if exp.get("startDate") or exp.get("endDate"):
                    date_range = f"({exp.get('startDate', '')} - {exp.get('endDate', 'Present')})"
                    parts.append(date_range.strip("()"))
                experience_parts.append(" ".join(filter(None, parts)))
            else:
                experience_parts.append(str(exp))
        experience = "; ".join(experience_parts)
    elif isinstance(experience_raw, str):
        experience = experience_raw
    else:
        experience = ""
    
    # Extract skills
    skills_raw = (
        linkedin_data.get("skills") or
        linkedin_data.get("skillSet") or
        linkedin_data.get("competencies")
    )
    if isinstance(skills_raw, list):
        skills = ", ".join([str(skill) if not isinstance(skill, dict) else skill.get("name", str(skill)) for skill in skills_raw])
    elif isinstance(skills_raw, str):
        skills = skills_raw
    else:
        skills = ""
    
    # Extract summary
    summary = (
        linkedin_data.get("summary") or
        linkedin_data.get("about") or
        linkedin_data.get("headline") or
        linkedin_data.get("bio") or
        ""
    )
    
    # Create normalized profile matching CSV format
    normalized_profile = {
        "name": name.strip(),
        "education": education.strip(),
        "experience": experience.strip(),
        "skills": skills.strip(),
        "summary": summary.strip()
    }
    
    return json.dumps(normalized_profile, ensure_ascii=False)


def create_candidate_from_linkedin(
    linkedin_data: Dict[str, Any],
    company_id: int,
    linkedin_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a candidate data dictionary from LinkedIn profile data.
    
    Returns: Dictionary ready to be used for creating a Candidate model instance.
    """
    # Normalize the profile
    raw_profile = normalize_linkedin_profile(linkedin_data)
    
    # Extract basic info
    name = (
        linkedin_data.get("name") or
        linkedin_data.get("fullName") or
        f"{linkedin_data.get('firstName', '')} {linkedin_data.get('lastName', '')}".strip() or
        linkedin_data.get("profileName") or
        None
    )
    
    email = (
        linkedin_data.get("email") or
        linkedin_data.get("contactEmail") or
        None
    )
    
    # Use provided linkedin_id or extract from data
    external_id = linkedin_id or linkedin_data.get("id") or linkedin_data.get("linkedinId") or linkedin_data.get("profileId")
    
    # Store parsed profile JSON (original LinkedIn data structure)
    parsed_profile_json = linkedin_data
    
    return {
        "company_id": company_id,
        "name": name.strip() if name else None,
        "email": email.strip() if email else None,
        "raw_profile": raw_profile,
        "parsed_profile_json": parsed_profile_json,
        "source": "linkedin",
        "external_id": str(external_id) if external_id else None
    }

