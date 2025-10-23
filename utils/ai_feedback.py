# utils/ai_feedback.py
import os
import json
from openai import OpenAI

# -----------------------------------------------------------
# Main AI feedback function
# -----------------------------------------------------------
def get_ai_feedback(resume_text, job_description, candidate_name=None, max_tokens=450):
    """
    Uses OpenAI's new API client (openai>=1.0.0) to generate resume feedback.
    If no API key is found, falls back to simple rule-based feedback.
    """

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return _rule_based_feedback(resume_text, job_description)

    client = OpenAI(api_key=api_key)

    system_prompt = (
        "You are a helpful, concise career coach specialized in tech resumes. "
        "Given the candidate's resume text and a job description, produce:\n"
        "1) Short summary (1–3 lines) of resume strengths for this job.\n"
        "2) Top 5 specific suggestions to improve the resume for this job (bullet list).\n"
        "3) A short rewritten 1–2 line resume headline suggestion.\n"
        "Return JSON with keys: summary, suggestions (list), headline."
    )

    user_prompt = (
        f"Resume text:\n'''{resume_text[:3000]}'''\n\n"
        f"Job description:\n'''{job_description[:3000]}'''\n\n"
        f"Candidate name: {candidate_name or 'N/A'}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4o" if available in your account
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=max_tokens,
        )

        text = response.choices[0].message.content

        # Try to parse JSON if model returns it
        try:
            parsed = json.loads(text)
            return parsed
        except Exception:
            # If it's just plain text, return in a dict
            return {"summary": text, "suggestions": [], "headline": ""}

    except Exception as e:
        # In case of OpenAI API error
        return {
            "summary": f"OpenAI API error: {e}",
            "suggestions": [],
            "headline": "",
        }

# -----------------------------------------------------------
# Fallback rule-based feedback (no API key)
# -----------------------------------------------------------
def _rule_based_feedback(resume_text, job_description):
    jd = job_description.lower()
    r = resume_text.lower()
    suggestions = []

    if "python" in jd and "python" not in r:
        suggestions.append("Add 'Python' prominently if you have experience with it.")
    if "machine learning" in jd and "machine" not in r:
        suggestions.append("Mention machine learning projects or coursework.")
    if "sql" in jd and "sql" not in r:
        suggestions.append("Include experience with SQL databases.")
    if len(r.split()) < 200:
        suggestions.append("Add more detail about your projects and achievements.")
    if "github" not in r:
        suggestions.append("Add your GitHub link to highlight your coding work.")
    if not suggestions:
        suggestions.append("Resume seems relevant—add measurable results for stronger impact.")

    summary = "Basic rule-based feedback (no API key detected)."
    headline = "Aspiring AI/Software Engineer eager to apply technical and analytical skills."

    return {"summary": summary, "suggestions": suggestions[:5], "headline": headline}