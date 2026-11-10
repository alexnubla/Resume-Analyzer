import streamlit as st
import PyPDF2
import docx
import re
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter

# Download NLTK data quietly if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

st.set_page_config(page_title="Resume ATS Evaluator", page_icon="📄", layout="wide")

st.title("📄 Resume ATS Evaluator")
st.markdown("### Evaluate your resume against a job description")

with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    1. **Upload your resume** (PDF or DOCX format)
    2. **Enter the job description** you're targeting
    3. **Click 'Analyze'** to get your ATS score and recommendations
    """)
    
    st.markdown("---")
    st.markdown("**Features:**")
    st.markdown("- ✅ Keyword matching")
    st.markdown("- ✅ Rejection probability")
    st.markdown("- ✅ Actionable improvements")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose your resume file", 
        type=['pdf', 'docx'],
        help="Supported formats: PDF, DOCX"
    )
    
    st.subheader("💼 Job Description")
    job_description = st.text_area(
        "Paste the job description here:",
        height=300,
        placeholder="Enter the full job description...",
        help="The more detailed the job description, the better the analysis"
    )
    
    # Buttons Row
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        analyze_button = st.button("🚀 Analyze Resume", use_container_width=True)
    with col_btn2:
        reset_button = st.button("🔄 Reset", use_container_width=True)

    # Handle Reset
    if reset_button:
        st.session_state.clear()
        st.rerun()

with col2:
    st.subheader("📊 Analysis Results")
    
    if analyze_button and uploaded_file and job_description:
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
        
        # --- PRIORITIZE MISSING KEYWORDS BY FREQUENCY ---
        jd_word_counts = Counter(clean(job_description))
        prioritized_missing = sorted(missing, key=lambda x: jd_word_counts[x], reverse=True)
        
        # 4. Simple Skills Check
        skills = ['python', 'java', 'sql', 'aws', 'react', 'docker', 'git', 'agile', 'leadership', 'communication', 'project management']
        found_skills = [s for s in skills if s in resume_text.lower()]
        
        # --- DISPLAY RESULTS ---
        
        # 1. Match Score & Rejection Probability
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Keyword Match Score", f"{match_score:.1f}%")
            st.progress(match_score / 100)
        
        with col_b:
            # Calculate Rejection Probability (Inverse of match score, capped at 95%)
            rejection_prob = max(0, min(95, 100 - match_score - 10)) 
            st.metric("Est. Rejection Risk", f"{rejection_prob:.1f}%")
            if rejection_prob > 70:
                st.error("⚠️ High Risk")
            elif rejection_prob > 40:
                st.warning("⚠️ Moderate Risk")
            else:
                st.success("✅ Low Risk")

        st.markdown("---")

        # 2. Found Keywords
        st.subheader("✅ Found Keywords")
        if common:
            st.write(", ".join(sorted(list(common))[:20]))
        else:
            st.warning("No matching keywords found.")
        
        # 3. Missing Keywords
        st.subheader("⚠️ Top Missing Keywords")
        if prioritized_missing:
            st.write(", ".join(prioritized_missing[:15]))
            st.info(f"Total missing: {len(missing)}. Focus on the top ones!")
        else:
            st.success("Great! All JD keywords are present!")
        
        # 4. Skills Detected
        st.subheader("🎯 Skills Detected")
        if found_skills:
            for s in found_skills:
                st.markdown(f"- ✅ {s.title()}")
        else:
            st.warning("No major technical skills detected.")

        # 5. IMPROVEMENTS SECTION
        st.markdown("---")
        st.subheader("💡 How to Improve Your Resume")
        improvements = []
        
        if match_score < 50:
            improvements.append("🔴 **Critical:** Your keyword match is low. Try to naturally incorporate more terms from the Job Description into your 'Skills' and 'Experience' sections.")
        
        if len(missing) > 20:
            improvements.append("🟡 **Volume:** You are missing over 20 keywords. Review the 'Top Missing Keywords' list above and add the most relevant ones.")
        
        if len(found_skills) < 3:
            improvements.append("🟡 **Skills Gap:** The system didn't detect many standard technical skills. Ensure your tech stack is clearly listed in a dedicated 'Skills' section.")
        
        if len(resume_text.split()) < 300:
            improvements.append("🟡 **Length:** Your resume seems quite short. Consider adding more detail about your achievements and responsibilities.")
        
        if match_score >= 80:
            improvements.append("🟢 **Strong Match:** Your resume is well-optimized! Just double-check for any specific certifications mentioned in the JD.")
            
        if not improvements:
            improvements.append("✅ **Good Start:** Continue refining your bullet points to focus on results and metrics.")

        for imp in improvements:
            st.markdown(f"- {imp}")

    elif not uploaded_file or not job_description:
        st.info("Please upload a resume and paste a Job Description to start.")
    elif not analyze_button:
        st.info("Click the 'Analyze Resume' button to see results.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | [View on GitHub](https://github.com/alexnubla/Resume-Analyzer)")