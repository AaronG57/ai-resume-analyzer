import streamlit as st
from gpt4all import GPT4All
import PyPDF2
import re

# -----------------------------
# App setup
# -----------------------------
st.set_page_config(page_title="AI Resume Analyzer (Offline)", page_icon="🧠", layout="wide")

st.title("🧠 AI Resume & Job Match Analyzer (Offline GPT4All)")
st.write("Upload your resume, paste a job description, and get offline AI feedback & match analysis!")

# -----------------------------
# Initialize the model
# -----------------------------
@st.cache_resource
def load_model():
    model_name = "mistral-7b-instruct-v0.1.Q4_0.gguf"  # Official GPT4All model name
    return GPT4All(model_name)

model = load_model()

# -----------------------------
# Local AI generation function
# -----------------------------
def generate_text(prompt, max_tokens=300):
    system_prompt = (
        "You are a professional resume screening assistant. "
        "Evaluate resumes vs job descriptions. Output match %, strengths, improvements."
    )

    final_prompt = f"""
System: {system_prompt}

User: {prompt}

Assistant:
"""

    with model.chat_session():
        response = model.generate(final_prompt, max_tokens=max_tokens, temp=0.6)

    return response.strip() if response.strip() else "⚠️ No response — try shorter text."

# -----------------------------
# Helper: Extract text from PDF
# -----------------------------
def extract_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    else:
        text = file.read().decode("utf-8")
    return text

# -----------------------------
# Streamlit interface
# -----------------------------
st.subheader("📄 Upload Your Resume")
uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

st.subheader("💼 Job Description")
job_description = st.text_area("Paste the job description here:", height=200)

if uploaded_file is not None:
    resume_text = extract_text(uploaded_file)
    st.success("✅ Resume loaded successfully!")
    st.text_area("Resume Preview", resume_text[:2000], height=200)

    if st.button("🔍 Analyze Match"):
        if not job_description.strip():
            st.warning("Please paste a job description first.")
        else:
            with st.spinner("Analyzing resume vs job description..."):
                prompt = f"""
Compare the following resume and job description and provide:

1. Match percentage (0–100%)
2. Strengths
3. Improvements to increase match

Resume:
{resume_text[:2000]}

Job Description:
{job_description[:1500]}
"""

                analysis = generate_text(prompt, max_tokens=350)

            score_match = re.search(r"(\d{1,3})\s*%", analysis)
            score = int(score_match.group(1)) if score_match else None

            st.metric("Match Score", f"{score}%" if score else "N/A")

            st.write("### 🧠 AI Feedback:")
            st.info(analysis)

else:
    st.warning("Please upload your resume to begin.")

st.markdown("---")
st.caption("🔒 Powered by GPT4All — 100% offline, no OpenAI cost.")