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

# Tabs for different features
tab1, tab2 = st.tabs(["📊 ATS Analysis", "🤖 ATS Parseability Check"])

with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    1. **Upload your resume** (PDF or DOCX format)
    2. **Enter the job description** (for Analysis tab)
    3. **Explore the tabs** to see your score and how robots read your file.
    """)

# --- TAB 1: ATS ANALYSIS ---
with tab1:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📤 Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose your resume file", 
            type=['pdf', 'docx'],
            help="Supported formats: PDF, DOCX",
            key="analysis_upload"
        )
        
        st.subheader("💼 Job Description")
        job_description = st.text_area(
            "Paste the job description here:",
            height=300,
            placeholder="Enter the full job description...",
            key="jd_input"
        )
        
        # Buttons Row
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            analyze_button = st.button("🚀 Analyze Resume", use_container_width=True)
        with col_btn2:
            reset_button = st.button("🔄 Reset", use_container_width=True)

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
            
            # --- SECTION-BASED WEIGHTING & SMART FILTERING ---
            
            # Define High-Value Sections (Keywords that should be prioritized)
            high_value_headers = [
                'responsibilities', 'duties', 'what you\'ll do', 'role overview',
                'qualifications', 'requirements', 'what you\'ll need', 'basic qualifications',
                'preferred skills', 'experience', 'technical skills', 'competencies'
            ]
            
            # Define Low-Value/Noise Sections (Keywords to ignore or deprioritize)
            low_value_headers = [
                'benefits', 'eeo', 'equal opportunity', 'affirmative action', 
                'disclaimer', 'other duties', 'additional eligibility', 
                'ear/itar', 'export control', 'citizenship', 'security clearance',
                'accommodation', 'hiring process', 'about the company'
            ]

            # Split JD into lines to find sections
            jd_lines = job_description.lower().split('\n')
            
            current_section_weight = 1.0
            weighted_jd_tokens = []
            
            for line in jd_lines:
                line_stripped = line.strip()
                
                # Check if line is a header
                is_high_value = any(header in line_stripped for header in high_value_headers)
                is_low_value = any(header in line_stripped for header in low_value_headers)
                
                if is_high_value:
                    current_section_weight = 3.0 # Boost weight for responsibilities/quals
                elif is_low_value:
                    current_section_weight = 0.1 # Deprioritize legal/HR fluff
                elif line_stripped.endswith(':') or (len(line_stripped.split()) < 5 and line_stripped.isupper()):
                    # Generic header detection
                    current_section_weight = 1.0
                
                # Add tokens from this line with their weight
                line_tokens = clean(line)
                weighted_jd_tokens.extend(line_tokens * int(current_section_weight * 10)) # Multiply frequency by weight

            jd_word_counts = Counter(weighted_jd_tokens)
            
            # Filter Logic: Keep only words that are NOT in the junk lists
            junk_words = {
                'please', 'note', 'designed', 'cover', 'contain', 'comprehensive',
                'listing', 'activities', 'duties', 'responsibilities', 'required',
                'employee', 'change', 'time', 'notice', 'additional', 'eligibility',
                'requirements', 'position', 'may', 'require', 'access', 'classified',
                'information', 'restricted', 'sites', 'systems', 'determined',
                'company', 'applicable', 'government', 'employment', 'role',
                'contingent', 'upon', 'ability', 'obtain', 'maintain', 'security',
                'clearance', 'other', 'authorization', 'satisfy', 'citizenship',
                'imposed', 'law', 'regulation', 'executive', 'order', 'contract',
                'notified', 'when', 'such', 'affirmative', 'action', 'eeo',
                'statement', 'equal', 'opportunity', 'employer', 'committed',
                'providing', 'opportunities', 'applicants', 'employees', 'without',
                'regard', 'race', 'color', 'religion', 'sex', 'sexual', 'orientation',
                'gender', 'identity', 'national', 'origin', 'age', 'disability',
                'genetic', 'protected', 'veteran', 'status', 'characteristic',
                'fostering', 'workplace', 'where', 'decisions', 'based',
                'qualifications', 'business', 'needs', 'perform', 'essential',
                'functions', 'reasonable', 'accommodation', 'requests',
                'considered', 'individual', 'basis', 'handled', 'accordance',
                'ear', 'itar', 'export', 'controlled', 'hiring', 'contractor',
                'licensing', 'bureau', 'industry', 'directorate', 'defense',
                'trade', 'controls', 'benefits', 'package', 'refer', 'bottom',
                'careers', 'page', 'details', 'castelion', 'hypersonic',
                'weapons', 'speed', 'scale', 'restore', 'american', 'deterrence',
                'achieving', 'exceptional', 'engineering', 'rapid', 'testing',
                'manufacturing', 'capacity', 'supported', 'secure', 'reliable',
                'infrastructure', 'keep', 'pace', 'hands', 'on', 'leadership',
                'troubleshooting', 'critical', 'outage', 'challenging', 'network',
                'architecture', 'recruiting', 'making', 'high', 'impact',
                'investment', 'combines', 'judgment', 'relentless', 'bias',
                'toward', 'action', 'standards', 'accountability', 'results'
            }

            generic_words = {
                'build', 'lead', 'manage', 'support', 'ensure', 'develop',
                'create', 'provide', 'maintain', 'handle', 'process', 'service',
                'client', 'customer', 'project', 'program', 'plan', 'strategy',
                'goal', 'objectives', 'success', 'growth', 'operations',
                'functions', 'use', 'using', 'used', 'make', 'made', 'get',
                'got', 'go', 'went', 'see', 'saw', 'know', 'knew', 'think',
                'thought', 'want', 'wanted', 'need', 'needed', 'help', 'helped',
                'take', 'took', 'give', 'gave', 'find', 'found', 'tell', 'told',
                'ask', 'asked', 'try', 'tried', 'leave', 'left', 'call', 'called',
                'move', 'moved', 'live', 'lived', 'believe', 'hold', 'bring',
                'brought', 'happen', 'write', 'wrote', 'sit', 'sat', 'stand',
                'stood', 'lose', 'lost', 'pay', 'paid', 'meet', 'met', 'include',
                'included', 'continue', 'set', 'learn', 'change', 'play', 'run',
                'like', 'carry', 'break', 'within', 'across', 'along', 'among',
                'around', 'before', 'behind', 'below', 'beneath', 'beside',
                'between', 'beyond', 'during', 'except', 'inside', 'into', 'near',
                'onto', 'upon', 'toward', 'throughout', 'minus', 'plus', 'versus',
                'per', 'via', 'year', 'years', 'day', 'week', 'month', 'level',
                'senior', 'junior', 'department', 'group', 'unit', 'field',
                'industry', 'team', 'work', 'experience', 'ability', 'time'
            }

            meaningful_missing = [
                word for word in missing 
                if word not in junk_words 
                and word not in generic_words
                and len(word) > 3
            ]
            
            # Sort by weighted frequency
            prioritized_missing = sorted(meaningful_missing, key=lambda x: jd_word_counts[x], reverse=True)
            
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
            st.subheader("⚠️ Top Missing Keywords (Weighted)")
            if prioritized_missing:
                st.write(", ".join(prioritized_missing[:15]))
                st.info(f"Total meaningful missing: {len(meaningful_missing)}. Focus on the top ones!")
            else:
                st.success("Great! All meaningful JD keywords are present!")
            
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
                improvements.append("🔴 **Critical:** Your keyword match is low. Try to naturally incorporate more terms from the Job Description.")
            
            if len(meaningful_missing) > 15:
                improvements.append("🟡 **Volume:** You are missing over 15 meaningful keywords. Review the list above.")
            
            if len(found_skills) < 3:
                improvements.append("🟡 **Skills Gap:** The system didn't detect many standard technical skills. Ensure your tech stack is clearly listed.")
            
            if len(resume_text.split()) < 300:
                improvements.append("🟡 **Length:** Your resume seems quite short. Consider adding more detail about your achievements.")
            
            if match_score >= 80:
                improvements.append("🟢 **Strong Match:** Your resume is well-optimized! Just double-check for any specific certifications.")
                
            if not improvements:
                improvements.append("✅ **Good Start:** Continue refining your bullet points to focus on results and metrics.")

            for imp in improvements:
                st.markdown(f"- {imp}")

        elif not uploaded_file or not job_description:
            st.info("Please upload a resume and paste a Job Description to start.")
        elif not analyze_button:
            st.info("Click the 'Analyze Resume' button to see results.")

# --- TAB 2: ATS PARSEABILITY CHECK ---
with tab2:
    st.subheader("🤖 How the ATS Robot Sees Your Resume")
    st.markdown("Applicant Tracking Systems strip away all formatting, colors, and images. Use this tool to ensure your contact info and headers are still readable.")
    
    col_parse1, col_parse2 = st.columns([1, 1])
    
    with col_parse1:
        parse_file = st.file_uploader("Upload resume to check parsing", type=['pdf', 'docx'], key="parse_upload")
        
        if parse_file:
            def get_raw_text(file):
                if file.type == "application/pdf":
                    reader = PyPDF2.PdfReader(file)
                    return "".join([page.extract_text() for page in reader.pages])
                else:
                    doc = docx.Document(file)
                    return "\n".join([p.text for p in doc.paragraphs])
            
            raw_text = get_raw_text(parse_file)
            
            # Basic Parsing Checks
            has_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text))
            has_phone = bool(re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', raw_text))
            
            st.markdown("### ✅ Parsing Status")
            if has_email:
                st.success("✅ Email Address Detected")
            else:
                st.error("❌ Email Address Missing or Unreadable")
                
            if has_phone:
                st.success("✅ Phone Number Detected")
            else:
                st.error("❌ Phone Number Missing or Unreadable")

    with col_parse2:
        if parse_file:
            st.markdown("### 📝 Raw Text Output")
            st.markdown("*This is exactly what the ATS database will store:*")
            st.code(raw_text[:1000] + "...", language="text") # Show first 1000 chars
            
            st.info("💡 **Tip:** If your name or contact info is missing from the text above, move it out of headers/footers or tables.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | [View on GitHub](https://github.com/alexnubla/Resume-Analyzer)")