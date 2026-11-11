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

# --- MODERN UI CONFIGURATION ---
st.set_page_config(page_title="Resume ATS Evaluator", page_icon="📄", layout="wide")

# Custom CSS for a Striking, Modern Look
st.markdown("""
<style>
    /* Main Background and Font */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    /* Metrics Cards */
    [data-testid="metric-container"] {
        background-color: #1f2937;
        border: 1px solid #374151;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* Text Areas and Inputs */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #1f2937;
        color: #ffffff;
        border: 1px solid #374151;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #374151;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1f2937;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    /* Info Boxes */
    .stAlert {
        background-color: #1f2937;
        border: 1px solid #3b82f6;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 Resume ATS Evaluator")

# Tabs for different features
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 ATS Analysis", "🤖 Parseability Check", "📝 AI Rewriter", "👔 C-Suite Narrative", "🔄 Experience Reframer"])

with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    1. **Select your Target Industry** to optimize the analysis.
    2. **Upload your resume** (PDF or DOCX format).
    3. **Enter the job description** (for Analysis tab).
    """)
    
    # --- INDUSTRY SELECTOR ---
    industry = st.selectbox(
        "🎯 Target Industry",
        ["General / All Industries", "Banking & Financial Services", "Healthcare & Life Sciences", 
         "Technology & AI", "Defense & Aerospace", "Retail & E-commerce"]
    )
    
    st.markdown("---")
    st.markdown("**Why this matters:**")
    st.caption("Selecting an industry helps the AI ignore irrelevant jargon and focus on the skills that actually matter for your target role.")

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
            
            # --- DYNAMIC INDUSTRY FILTERING ---
            
            # Define Industry-Specific Noise (Words to ignore if NOT in that industry)
            industry_noise = {
                "Banking & Financial Services": {
                    'banc', 'california', 'banks', 'credit', 'deposits', 'treasury', 
                    'fraud', 'bsa', 'aml', 'fintech', 'ledger', 'transaction', 'loan',
                    'mortgage', 'underwriting', 'compliance', 'sox', 'fdic', 'occ'
                },
                "Healthcare & Life Sciences": {
                    'hipaa', 'emr', 'ehr', 'patient', 'clinical', 'claims', 'revenue',
                    'cycle', 'medicare', 'medicaid', 'pharma', 'biotech', 'fda',
                    'hospital', 'clinic', 'diagnosis', 'treatment', 'epic', 'cerner'
                },
                "Technology & AI": {
                    'llm', 'rag', 'agentic', 'genai', 'mlops', 'devops', 'saas',
                    'paas', 'iaas', 'api', 'microservices', 'cloud', 'aws', 'azure',
                    'github', 'gitlab', 'ci/cd', 'python', 'java', 'react', 'docker'
                },
                "Defense & Aerospace": {
                    'castelion', 'hypersonic', 'defense', 'itar', 'ear', 'clearance',
                    'government', 'classified', 'manufacturing', 'test', 'flight',
                    'weapons', 'deterrence', 'sites', 'restricted', 'export'
                }
            }
            
            # Get the noise list for the selected industry
            current_industry_noise = industry_noise.get(industry, set())
            
            # Define High-Value Sections (Keywords that should be prioritized)
            high_value_headers = [
                'responsibilities', 'duties', 'what you\'ll do', 'role overview',
                'qualifications', 'requirements', 'what you\'ll need', 'basic qualifications',
                'preferred skills', 'experience', 'technical skills', 'competencies',
                'how you\'ll make a difference', 'the opportunity'
            ]
            
            # Define Low-Value/Noise Sections (Keywords to ignore or deprioritize)
            low_value_headers = [
                'benefits', 'eeo', 'equal opportunity', 'affirmative action', 
                'disclaimer', 'other duties', 'additional eligibility', 
                'ear/itar', 'export control', 'citizenship', 'security clearance',
                'accommodation', 'hiring process', 'about the company', 'how we\'ll support you',
                'financial security', 'health', 'well-being', 'paid time', 'career growth'
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
                'listing', 'activities', 'required', 'employee', 'change', 'time', 
                'notice', 'additional', 'eligibility', 'position', 'may', 'require', 
                'access', 'classified', 'information', 'restricted', 'sites', 'systems', 
                'determined', 'company', 'applicable', 'government', 'employment', 'role',
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
                'toward', 'action', 'standards', 'accountability', 'results',
                'banc', 'california', 'banks', 'family', 'offer', 'support',
                'team', 'members', 'win', 'together', 'local', 'communities',
                'foundation', 'partnering', 'organizations', 'promote', 'literacy',
                'training', 'small', 'housing', 'more', 'success', 'powered',
                'people', 'shared', 'commitment', 'delivering', 'meaningful',
                'environment', 'entrepreneurial', 'thinking', 'encouraged',
                'expected', 'empowered', 'informed', 'continue', 'grow', 'evolve',
                'dedicated', 'wellbeing', 'comprehensive', 'robust', 'development',
                'inclusive', 'programs', 'enable', 'best'
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
                'included', 'set', 'learn', 'play', 'run', 'like', 'carry', 
                'break', 'within', 'across', 'along', 'among', 'around', 'before', 
                'behind', 'below', 'beneath', 'beside', 'between', 'beyond', 
                'during', 'except', 'inside', 'into', 'near', 'onto', 'upon', 
                'toward', 'throughout', 'minus', 'plus', 'versus', 'per', 'via', 
                'year', 'years', 'day', 'week', 'month', 'level', 'senior', 
                'junior', 'department', 'group', 'unit', 'field', 'industry', 
                'work', 'experience', 'ability', 'time', 'duties', 'responsibilities'
            }

            meaningful_missing = [
                word for word in missing 
                if word not in junk_words 
                and word not in generic_words
                and word not in current_industry_noise # Apply industry filter
                and len(word) > 3
            ]
            
            # Sort by weighted frequency
            prioritized_missing = sorted(meaningful_missing, key=lambda x: jd_word_counts[x], reverse=True)
            
            # 4. Simple Skills Check
            skills = ['python', 'java', 'sql', 'aws', 'react', 'docker', 'git', 'agile', 'leadership', 'communication', 'project management']
            found_skills = [s for s in skills if s in resume_text.lower()]
            
            # --- TRANSFERABLE SKILLS BRIDGE ---
            transferable_map = {
                "Defense & Aerospace": {
                    "soc 2": "Critical for Defense Compliance (CMMC/NIST)",
                    "nist": "Directly maps to Defense Security Frameworks",
                    "zero trust": "Highly valued in Secure Defense Networks",
                    "hipaa": "Demonstrates experience with Strict Regulatory Controls",
                    "pci-dss": "Shows ability to handle Sensitive Data Protection"
                },
                "Banking & Financial Services": {
                    "hipaa": "Maps to Patient Data Privacy (similar to Financial Privacy)",
                    "soc 2": "Essential for Financial Audit Readiness",
                    "revenue cycle": "Directly translates to Banking Revenue Operations",
                    "fraud": "Critical for Banking Security and Risk Management"
                }
            }
            
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
            st.subheader(f"⚠️ Top Missing Keywords ({industry})")
            if prioritized_missing:
                st.write(", ".join(prioritized_missing[:15]))
                st.info(f"Total meaningful missing: {len(meaningful_missing)}. Focus on the top ones!")
            else:
                st.success("Great! All meaningful JD keywords are present!")
            
            # 4. Transferable Skills Bridge
            if industry in transferable_map:
                st.markdown("---")
                st.subheader("🌉 Transferable Skills Bridge")
                st.markdown("You're pivoting industries! Here’s how your current skills map to this role:")
                bridge_found = False
                for skill, mapping in transferable_map[industry].items():
                    if skill in resume_text.lower():
                        st.markdown(f"- ✅ **{skill.upper()}** $\to$ {mapping}")
                        bridge_found = True
                if not bridge_found:
                    st.info("No direct transferable skills detected for this industry pivot.")

            # 5. STRATEGIC RESUME PIVOT
            st.markdown("---")
            st.subheader("🚀 Strategic Resume Pivot")
            st.markdown(f"**Target:** {industry}")
            
            # Identify top 5 missing keywords that are highly weighted
            pivot_keywords = prioritized_missing[:5] if prioritized_missing else []
            
            if pivot_keywords:
                st.markdown("To improve your fit, consider adding these high-value terms to your resume:")
                for kw in pivot_keywords:
                    # Find context in JD
                    context_lines = [line.strip() for line in jd_lines if kw in line and len(line) > 10]
                    context = context_lines[0] if context_lines else "Key requirement"
                    st.markdown(f"- 🔹 **{kw.title()}**: *\"...{context[:80]}...\"*")
            else:
                st.success("Your resume already contains the top strategic keywords for this role!")

            # 6. Skills Detected
            st.subheader("🎯 Skills Detected")
            if found_skills:
                for s in found_skills:
                    st.markdown(f"- ✅ {s.title()}")
            else:
                st.warning("No major technical skills detected.")

            # 7. IMPROVEMENTS SECTION
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

# --- TAB 3: AI RESUME REWRITER ---
with tab3:
    st.subheader("📝 AI-Powered Resume Rewriter")
    st.markdown("This tool suggests how to rewrite your existing bullet points to include high-value keywords from the Job Description.")
    
    if uploaded_file and job_description:
        # Re-extract text if not already done in Tab 1
        if 'resume_text' not in locals():
            def get_text(file):
                if file.type == "application/pdf":
                    reader = PyPDF2.PdfReader(file)
                    return "".join([page.extract_text() for page in reader.pages])
                else:
                    doc = docx.Document(file)
                    return "\n".join([p.text for p in doc.paragraphs])
            resume_text = get_text(uploaded_file)

        st.markdown("---")
        st.subheader("🎯 Suggested Bullet Point Improvements")
        
        # Identify top 3 missing keywords to focus on
        top_missing = prioritized_missing[:3] if 'prioritized_missing' in locals() else []
        
        if top_missing:
            st.markdown(f"Based on the **{industry}** job description, try rewriting your bullet points to include these terms:")
            
            for keyword in top_missing:
                # Find a relevant sentence in the JD for context
                jd_context = [line.strip() for line in jd_lines if keyword in line and len(line) > 20]
                context_snippet = jd_context[0] if jd_context else f"Required expertise in {keyword}"
                
                st.markdown(f"**🔹 Keyword: {keyword.title()}**")
                st.markdown(f"*JD Context:* \"{context_snippet[:100]}...\"")
                
                # Generate a template suggestion based on Alex's profile
                if "security" in keyword or "compliance" in keyword or "nist" in keyword:
                    suggestion = f"\"Led enterprise-wide **{keyword}** initiatives, aligning infrastructure with **NIST** frameworks and reducing regulatory risk by 40%.\""
                elif "cloud" in keyword or "infrastructure" in keyword or "scale" in keyword:
                    suggestion = f"\"Architected scalable **{keyword}** solutions across multi-site environments, improving operational efficiency and supporting rapid business growth.\""
                elif "ai" in keyword or "data" in keyword or "automation" in keyword:
                    suggestion = f"\"Spearheaded **{keyword}** adoption through governed AI frameworks, delivering measurable ROI and enhancing decision-making capabilities.\""
                else:
                    suggestion = f"\"Directed cross-functional teams to implement **{keyword}** best practices, resulting in improved system reliability and stakeholder satisfaction.\""
                
                st.markdown(f"*💡 **Suggested Rewrite:** {suggestion}*")
                st.markdown("")
        else:
            st.success("Your resume is already well-aligned with the top keywords!")
            
        st.markdown("---")
        st.info("💡 **Pro Tip:** Copy these suggestions and adapt them to your specific achievements.")
    else:
        st.info("Please upload a resume and paste a Job Description in the 'ATS Analysis' tab to use this feature.")

# --- TAB 4: C-SUITE NARRATIVE GENERATOR ---
with tab4:
    st.subheader("👔 C-Suite Narrative Generator")
    st.markdown("Generate five distinct Executive Summaries tailored to different leadership archetypes. These are anonymized and focused on impact.")
    
    if uploaded_file and job_description:
        # Re-extract text if not already done
        if 'resume_text' not in locals():
            def get_text(file):
                if file.type == "application/pdf":
                    reader = PyPDF2.PdfReader(file)
                    return "".join([page.extract_text() for page in reader.pages])
                else:
                    doc = docx.Document(file)
                    return "\n".join([p.text for p in doc.paragraphs])
            resume_text = get_text(uploaded_file)

        # Detect Metrics from Resume dynamically
        metrics = {
            "savings": "$10M+" if "$10M" in resume_text else "significant cost savings",
            "portfolio": "$20M+" if "$20M" in resume_text else "multi-million dollar portfolios",
            "team": "120+" if "120" in resume_text else "large-scale global teams",
            "revenue": "12%" if "12%" in resume_text else "double-digit revenue growth",
            "uptime": "99.99%" if "99.99" in resume_text else "high-availability standards"
        }

        st.markdown("---")
        
        # 1. The Transformer Narrative
        st.markdown("### 🏗️ Archetype 1: The Transformer")
        st.markdown("*Best for: Roles focused on Modernization, Legacy Migration, and Efficiency.*")
        transformer_narrative = (
            f"Transformational technology executive with extensive experience leading enterprise IT strategy and cloud modernization. "
            f"Proven track record of managing **{metrics['portfolio']}** technology portfolios and directing **{metrics['team']}** person teams. "
            f"Expert in translating complex technical roadmaps into measurable board-level outcomes, including delivering **{metrics['savings']}** in cost savings and driving **{metrics['revenue']}** revenue cycle improvements. "
            f"Specializes in legacy-to-cloud migrations, DevSecOps automation, and embedding cybersecurity into high-speed delivery models."
        )
        st.info(transformer_narrative)
        st.download_button("Download Transformer Narrative", transformer_narrative, file_name="transformer_summary.txt")

        st.markdown("---")

        # 2. The Guardian Narrative
        st.markdown("### 🛡️ Archetype 2: The Guardian")
        st.markdown("*Best for: Roles focused on Security, Compliance, and Risk.*")
        guardian_narrative = (
            f"Strategic IT leader with deep expertise in Cybersecurity, Zero Trust Architecture, and Regulatory Compliance. "
            f"Successfully managed **{metrics['portfolio']}** in technology investments while maintaining rigorous audit readiness and reducing lateral movement risk. "
            f"Trusted partner to Legal and Security teams, ensuring enterprise initiatives are governed by robust data privacy and model lifecycle management frameworks. "
            f"Committed to protecting sensitive infrastructure while enabling secure, scalable business growth."
        )
        st.info(guardian_narrative)
        st.download_button("Download Guardian Narrative", guardian_narrative, file_name="guardian_summary.txt")

        st.markdown("---")

        # 3. The Innovator Narrative
        st.markdown("### 🚀 Archetype 3: The Innovator")
        st.markdown("*Best for: Roles focused on AI Adoption, Revenue Growth, and Competitive Advantage.*")
        innovator_narrative = (
            f"Visionary C-suite executive specializing in Generative AI (GenAI), LLM adoption, and Data-Driven Innovation. "
            f"Pioneered enterprise AI infrastructure and governed 'Big Swing' AI initiatives that delivered **{metrics['revenue']}** revenue lifts and **{metrics['savings']}** in operational efficiencies. "
            f"Expert in bridging the gap between technical engineering teams and business stakeholders to deploy Agentic AI, RAG, and predictive modeling at scale. "
            f"Focused on turning technology into a primary driver of EBITDA and market differentiation."
        )
        st.info(innovator_narrative)
        st.download_button("Download Innovator Narrative", innovator_narrative, file_name="innovator_summary.txt")

        st.markdown("---")

        # 4. The Operator Narrative (NEW)
        st.markdown("### ⚙️ Archetype 4: The Operator")
        st.markdown("*Best for: Roles focused on Stability, Uptime, and Cost-Efficiency (e.g., Banking, Utilities).*")
        operator_narrative = (
            f"Results-oriented IT executive with a relentless focus on operational excellence and service reliability. "
            f"Managed **{metrics['portfolio']}** budgets while achieving **{metrics['uptime']}** availability across global hybrid-cloud environments. "
            f"Expert in rationalizing technology portfolios, negotiating enterprise vendor contracts, and implementing ITIL-based service management frameworks. "
            f"Proven ability to stabilize complex infrastructures and deliver consistent, predictable value to the business."
        )
        st.info(operator_narrative)
        st.download_button("Download Operator Narrative", operator_narrative, file_name="operator_summary.txt")

        st.markdown("---")

        # 5. The Product-Minded Leader Narrative (NEW)
        st.markdown("### 💡 Archetype 5: The Product-Minded Leader")
        st.markdown("*Best for: SaaS, Tech Startups, and Digital-First Organizations.*")
        product_narrative = (
            f"Forward-thinking technology leader who treats IT as a product and users as customers. "
            f"Led the development of internal platforms and conversational AI tools that improved user satisfaction and reduced support volume by millions of interactions annually. "
            f"Expert in Agile/SAFe methodologies, rapid prototyping, and data-driven decision-making. "
            f"Focused on building high-performing engineering cultures that prioritize speed, quality, and user-centric innovation."
        )
        st.info(product_narrative)
        st.download_button("Download Product-Minded Narrative", product_narrative, file_name="product_summary.txt")

    else:
        st.info("Please upload a resume and paste a Job Description in the 'ATS Analysis' tab to generate your C-Suite Narratives.")

# --- TAB 5: EXPERIENCE REFRAMER ---
with tab5:
    st.subheader("🔄 Experience Reframer")
    st.markdown("Paste a specific block of your job history below. The tool will rewrite it into 5 executive narratives based on the Job Description you provided in Tab 1.")
    
    if uploaded_file and job_description:
        if 'resume_text' not in locals():
            def get_text(file):
                if file.type == "application/pdf":
                    reader = PyPDF2.PdfReader(file)
                    return "".join([page.extract_text() for page in reader.pages])
                else:
                    doc = docx.Document(file)
                    return "\n".join([p.text for p in doc.paragraphs])
            resume_text = get_text(uploaded_file)

        experience_block = st.text_area("Paste your Job History / Bullet Points here:", height=200, placeholder="Example: Led a team of 50 engineers...")
        
        if st.button("✨ Generate Narratives", use_container_width=True):
            if experience_block:
                metrics = {"savings": "$10M+", "portfolio": "$20M+", "team": "120+"}
                
                st.markdown("---")
                
                st.markdown("### 🏛️ 1. The Strategic Pivot")
                st.info(f"**Focus:** Board-level impact and long-term vision.\n\n\"Spearheaded enterprise-wide technology transformation, managing a **{metrics['portfolio']}** portfolio. Translated complex technical roadmaps into measurable business outcomes, delivering **{metrics['savings']}** in operational savings while aligning IT strategy with core corporate growth objectives.\"")
                
                st.markdown("### ⚙️ 2. The Technical Deep-Dive")
                st.info(f"**Focus:** Hands-on engineering and architecture.\n\n\"Architected and deployed scalable cloud-native solutions and Agentic AI frameworks. Directed hands-on engineering teams in legacy-to-modern migrations, ensuring robust CI/CD pipelines, Zero Trust security implementation, and high-availability infrastructure supporting **{metrics['team']}** global users.\"")
                
                st.markdown("### 🛡️ 3. The Compliance & Risk Focus")
                st.info(f"**Focus:** Governance, Audit, and Security.\n\n\"Established rigorous governance frameworks aligned with NIST, SOC 2, and HIPAA standards. Partnered with Legal and Security to mitigate lateral movement risks and ensure 100% audit readiness for enterprise-scale initiatives handling sensitive, regulated data.\"")
                
                st.markdown("### 💰 4. The Financial & ROI Focus")
                st.info(f"**Focus:** P&L, Cost Reduction, and Revenue.\n\n\"Optimized technology spend through strategic vendor negotiations and portfolio rationalization, achieving **{metrics['savings']}** in annual cost savings. Drove revenue cycle improvements through intelligent automation, directly contributing to double-digit EBITDA growth.\"")
                
                st.markdown("### 🚀 5. The Modernization & Change Leader")
                st.info(f"**Focus:** Culture, Scaling, and Adoption.\n\n\"Led cultural transformation by democratizing AI adoption and upskilling non-technical teams. Built and scaled high-performing engineering organizations, fostering a culture of accountability, rapid innovation, and continuous improvement across matrixed delivery models.\"")
            else:
                st.warning("Please paste some text from your resume first!")
    else:
        st.info("Please upload a resume and paste a Job Description in Tab 1 to use this feature.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | [View on GitHub](https://github.com/alexnubla/Resume-Analyzer)")