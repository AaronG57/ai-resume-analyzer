# app.py
import streamlit as st
from utils.resume_parser import parse_resume, clean_text
from utils.job_matcher import compute_match_score
from utils.ai_feedback import get_ai_feedback
import io

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.title("🧠 AI Resume Analyzer")
st.write("Upload your resume (PDF or DOCX) and paste a job description to get a fit score and feedback.")

with st.sidebar:
    st.header("How to use")
    st.markdown("""
    1. Upload a resume (PDF or DOCX).  
    2. Paste the job description text.  
    3. (Optional) Set OPENAI_API_KEY in environment to get AI feedback.  
    4. Click Analyze.
    """)
    st.markdown("**Tip:** Add a sample job to `sample_job.txt` for quick testing.")

uploaded_file = st.file_uploader("Upload resume (PDF / DOCX / TXT)", type=["pdf", "docx", "txt"])
job_desc = st.text_area("Paste job description (or leave blank to use sample)", height=200)

col1, col2 = st.columns([1, 3])

with col1:
    candidate_name = st.text_input("Candidate name (optional)")
    analyze_btn = st.button("Analyze resume")

with col2:
    st.info("Results will appear here after analysis.")

# Load sample job if user left blank and sample exists
if not job_desc:
    try:
        with open("sample_job.txt", "r", encoding="utf-8") as f:
            job_desc = f.read()
    except Exception:
        job_desc = ""

def safe_read_uploaded(u):
    try:
        return u.read()
    except:
        return None

if analyze_btn:
    if not uploaded_file:
        st.error("Please upload a resume file first.")
    elif not job_desc:
        st.error("Please paste a job description or create sample_job.txt.")
    else:
        st.info("Parsing resume...")
        # Rewind file-like if needed
        bytes_data = safe_read_uploaded(uploaded_file)
        # We need to pass a file-like again to parser; create BytesIO
        import io
        file_like = io.BytesIO(bytes_data)
        # filename matters for extension detection
        filename = uploaded_file.name
        resume_text = parse_resume(file_like, filename)
        if not resume_text:
            st.error("Could not extract text from the resume. Try another file.")
        else:
            st.success("Resume parsed.")
            st.subheader("Resume excerpt")
            st.write(resume_text[:2000] + ("..." if len(resume_text) > 2000 else ""))

            st.subheader("Job description excerpt")
            st.write(job_desc[:2000] + ("..." if len(job_desc) > 2000 else ""))

            st.subheader("Match score")
            score = compute_match_score(resume_text, job_desc)
            st.progress(min(100, int(score)))
            st.metric("Fit score", f"{score} / 100")

            st.subheader("AI feedback & suggestions")
            with st.spinner("Generating feedback... (OpenAI key required for advanced feedback)"):
                feedback = get_ai_feedback(resume_text, job_desc, candidate_name=candidate_name)
            # feedback may be dict or text
            if isinstance(feedback, dict):
                st.markdown("**Summary**")
                st.write(feedback.get("summary", ""))
                st.markdown("**Top suggestions**")
                suggestions = feedback.get("suggestions", [])
                for s in suggestions:
                    st.write("- " + s)
                st.markdown("**Headline suggestion**")
                st.info(feedback.get("headline", ""))
            else:
                st.write(feedback)
