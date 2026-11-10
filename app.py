import streamlit as st
import PyPDF2
import docx
import re
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

st.set_page_config(page_title="Resume ATS Evaluator", page_icon="📄", layout="wide")

st.title("📄 Resume ATS Evaluator (Lite)")
st.markdown("### Evaluate your resume against a job description")

with st.sidebar:
    st.header("Instructions")
    st.markdown("1. Upload resume (PDF/DOCX)\n2. Paste Job Description\n3. Click Analyze")

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("Choose your resume", type=['pdf', 'docx'])
    job_description = st.text_area("Paste Job Description:", height=300)

with col2:
    if uploaded_file and job_description:
        # 1. Extract Text
        def get_text(file):
            if file.type == "application/pdf":
                reader = PyPDF2.PdfReader(file)
                return "".join([page.extract_text() for page in reader.pages])
            else:
                doc = docx.Document(file)
                return "\n".join([p.text for p in doc.paragraphs])
        
        resume_text = get_text(uploaded_file)
        
        # 2. Clean and Tokenize
        def clean(text):
            text = text.lower()
            text = re.sub(r'[^a-z\s]', '', text)
            tokens = word_tokenize(text)
            stop_words = set(nltk.corpus.stopwords.words('english'))
            return [t for t in tokens if t not in stop_words and len(t) > 2]

        res_tokens = set(clean(resume_text))
        jd_tokens = set(clean(job_description))
        
        # 3. Calculate Match
        common = res_tokens.intersection(jd_tokens)
        missing = jd_tokens - res_tokens
        
        match_score = (len(common) / len(jd_tokens)) * 100 if jd_tokens else 0
        
        # 4. Simple Skills Check
        skills = ['python', 'java', 'sql', 'aws', 'react', 'docker', 'git', 'agile']
        found_skills = [s for s in skills if s in resume_text.lower()]
        
        # Display Results
        st.metric("Keyword Match Score", f"{match_score:.1f}%")
        st.progress(match_score / 100)
        
        st.subheader("✅ Found Keywords")
        st.write(", ".join(sorted(list(common))[:15]))
        
        st.subheader("⚠️ Missing Keywords")
        if missing:
            st.write(", ".join(sorted(list(missing))[:15]))
        
        st.subheader("🎯 Skills Detected")
        if found_skills:
            for s in found_skills:
                st.markdown(f"- {s.title()}")
        else:
            st.warning("No major technical skills detected.")
            
    else:
        st.info("Upload a resume and paste a JD to start.")