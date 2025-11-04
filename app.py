import streamlit as st
from groq import Groq
import PyPDF2
import re
import os
from dotenv import load_dotenv

load_dotenv()
# Streamlit config
st.set_page_config(page_title="AI Resume Analyzer", page_icon="🧠", layout="wide")
st.title("🧠 AI Resume & Job Match Analyzer (Groq — Cloud Fast)")
st.write("Upload your resume, paste a job description, and get AI match score & feedback!")

# Get API Key from Streamlit Secrets
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# PDF text extractor
def extract_text(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# AI function
def analyze_resume(resume, job):
    prompt = f"""
You are a professional HR hiring AI. Compare this resume to the job description.

1. Give a match score (0-100%)
2. List top strengths
3. List weaknesses
4. Suggest resume improvements
5. Suggest keywords missing from resume

Resume:
{resume[:3000]}

Job Description:
{job[:2000]}

Return in clean bullet format.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=500
    )

    return response.choices[0].message.content

# Upload resume
uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

# Job Description Input
job_description = st.text_area("Paste the job description here:", height=200)

if uploaded_file and job_description.strip():
    resume_text = extract_text(uploaded_file)
    st.success("✅ Resume uploaded!")
    st.text_area("Resume Preview", resume_text[:1500])

    if st.button("🔍 Analyze Match"):
        with st.spinner("Analyzing with AI..."):
            result = analyze_resume(resume_text, job_description)

        # Extract score
        match = re.search(r"(\d{2,3})\s*%", result)
        score = match.group(1) if match else "N/A"

        st.metric("Match Score", f"{score}%")
        st.write("### 💡 AI Feedback")
        st.info(result)

else:
    st.warning("Upload your resume and paste job description to continue.")

st.caption("Powered by Groq + Mixtral — lightning-fast job matching 🚀")