# utils/ai_feedback.py
import os
import openai
import json

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

def _openai_available():
    return OPENAI_KEY is not None and OPENAI_KEY.strip() != ""

def get_ai_feedback(resume_text, job_description, candidate_name=None, max_tokens=450):
    """
    If an OpenAI API key is provided via OPENAI_API_KEY env var, use Chat API to get
    feedback and tailored suggestions. If not, return a simpler rule-based summary.
    """
    if _openai_available():
        openai.api_key = OPENAI_KEY
        system_prompt = (
            "You are a helpful, concise career coach specialized in tech resumes. "
            "Given the candidate's resume text and a job description, produce:\n"
            "1) Short summary (1-3 lines) of resume strengths for this job.\n"
            "2) Top 5 specific suggestions to improve the resume for this job (bullet list).\n"
            "3) A short rewritten 1-2 line resume headline suggestion.\n"
            "Return JSON with keys: summary, suggestions (list), headline."
        )

        user_prompt = (
            f"Resume text:\n'''{resume_text[:3000]}'''\n\n"
            f"Job description:\n'''{job_description[:3000]}'''\n\n"
            f"Candidate name: {candidate_name or 'N/A'}"
        )

        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini" if hasattr(openai, "ChatCompletion") else "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=max_tokens,
                n=1,
            )
            text = resp["choices"][0]["message"]["content"]
            # Try to parse JSON if returned; otherwise return raw text
            try:
                parsed = json.loads(text)
                return parsed
            except Exception:
                return {"summary": text, "suggestions": [], "headline": ""}
        except Exception as e:
            # API failure
            return {"summary": f"OpenAI API error: {e}", "suggestions": [], "headline": ""}
    else:
        # rule-based fallback
        return _rule_based_feedback(resume_text, job_description)

def _rule_based_feedback(resume_text, job_description):
    # very simple heuristics
    jd = job_description.lower()
    r = resume_text.lower()
    suggestions = []
    if "python" in jd and "python" not in r:
        suggestions.append("Add 'Python' prominently if you have it—mention projects or libraries.")
    if "c#" in jd and "c#" not in r:
        suggestions.append("Add C# experience (projects, frameworks) if applicable.")
    if "machine learning" in jd and "machine" not in r:
        suggestions.append("Mention any ML coursework or projects (datasets, models, tools).")
    if len(r.split()) < 200:
        suggestions.append("Expand your work/project descriptions with metrics and short bullet points.")
    if "github" not in r:
        suggestions.append("Add your GitHub link and mention 1-2 project repos (with URLs).")
    if not suggestions:
        suggestions.append("Resume looks reasonably relevant—add quantifiable achievements (numbers).")

    summary = "Automated heuristic summary: shows basic skills; needs tailoring to the job description."
    headline = "Candidate with programming and AI coursework — eager to contribute to engineering teams."

    return {"summary": summary, "suggestions": suggestions[:5], "headline": headline}
