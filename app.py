import streamlit as st
import PyPDF2
import docx
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
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

# --- HELPER FUNCTIONS (Defined Globally for All Tabs) ---
def get_text(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return "".join([page.extract_text() for page in reader.pages])
    else:
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

def clean(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = word_tokenize(text)
    stop_words = set(nltk.corpus.stopwords.words('english'))
    return [t for t in tokens if t not in stop_words and len(t) > 2]

# --- MODERN UI CONFIGURATION ---
st.set_page_config(page_title="Resume Evaluator", page_icon="📄", layout="wide")

# Custom CSS for a Clean, Professional, Card-Based Look
st.markdown("""
<style>
    /* Main Background - Clean Light Theme */
    .stApp {
        background-color: #f8f9fa;
        color: #1a202c;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Headers - Bold and Dark */
    h1, h2, h3 {
        color: #1a202c !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Sidebar - Clean White with Subtle Border */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: #1a202c !important;
    }
    
    /* Metric Cards - White with Shadow (The "Card" Look) */
    [data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Buttons - Primary Brand Color (Deep Blue/Purple) */
    .stButton > button {
        background-color: #4f46e5; /* Indigo-600 */
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        background-color: #4338ca; /* Indigo-700 */
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Text Areas and Inputs - Clean White Fields */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #ffffff;
        color: #1a202c;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 12px;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #4f46e5;
        box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
    }
    
    /* Tabs - Underlined Style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 0px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #64748b;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        border-bottom: 3px solid #4f46e5;
        color: #4f46e5 !important;
        font-weight: 700;
    }
    
    /* Info/Alert Boxes - Soft Backgrounds */
    .stAlert {
        background-color: #eff6ff; /* Blue-50 */
        border: 1px solid #bfdbfe; /* Blue-200 */
        color: #1e40af; /* Blue-800 */
        border-radius: 8px;
    }
    
    /* Download Buttons - Secondary Style */
    .stDownloadButton > button {
        background-color: #ffffff;
        color: #4f46e5;
        border: 1px solid #4f46e5;
        border-radius: 8px;
        font-weight: 600;
    }
    .stDownloadButton > button:hover {
        background-color: #eff6ff;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 Resume Evaluator")

# Tabs for different features
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 ATS Analysis", "🤖 ATS AI Parser", "📝 AI Rewriter", "👔 C-Suite Narrative", "🔄 Experience Reframing"])

with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("""
    1. **Select Target Industry**
    2. **Upload Resume**
    3. **Paste Job Description**
    """)
    
    # --- INDUSTRY SELECTOR ---
    industry = st.selectbox(
        "🎯 Target Industry",
        ["General / All Industries", "Banking & Financial Services", "Healthcare & Life Sciences", 
         "Technology & AI", "Defense & Aerospace", "Retail & E-commerce", 
         "Entertainment & Media", "Consulting & Professional Services"]
    )
    
    st.markdown("---")
    st.caption("Built for modern executives pivoting industries.")

# --- TAB 1: ATS ANALYSIS ---
with tab1:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📤 Upload Resume")
        uploaded_file = st.file_uploader("Choose your resume file", type=['pdf', 'docx'], key="analysis_upload")
        
        st.subheader("💼 Job Description")
        job_description = st.text_area("Paste the job description here, then select 🎯 Target Industry on the left:", height=300, placeholder="Enter the full job description...", key="jd_input")
        
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
            resume_text = get_text(uploaded_file)
            
            res_tokens = set(clean(resume_text))
            jd_tokens = set(clean(job_description))
            
            common = res_tokens.intersection(jd_tokens)
            missing = jd_tokens - res_tokens
            match_score = (len(common) / len(jd_tokens)) * 100 if jd_tokens else 0
            
            # --- DYNAMIC FILTERING LOGIC ---
            industry_noise = {
                "Banking & Financial Services": {'banc', 'california', 'banks', 'credit', 'deposits', 'treasury', 'fraud', 'bsa', 'aml'},
                "Healthcare & Life Sciences": {'hipaa', 'emr', 'ehr', 'patient', 'clinical', 'claims', 'revenue', 'cycle'},
                "Technology & AI": {'llm', 'rag', 'agentic', 'genai', 'mlops', 'devops', 'saas', 'api'},
                "Defense & Aerospace": {'castelion', 'hypersonic', 'defense', 'itar', 'ear', 'clearance', 'government'},
                "Entertainment & Media": {'streaming', 'content', 'media', 'entertainment', 'studio', 'production', 'broadcast', 'subscription', 'viewer', 'audience', 'netflix', 'disney', 'warner'},
                "Consulting & Professional Services": {'consulting', 'client', 'engagement', 'deliverable', 'billable', 'practice', 'partner', 'manager', 'associate', 'firm', 'mckinsey', 'deloitte', 'accenture'}
            }
            current_industry_noise = industry_noise.get(industry, set())
            
            junk_words = {
                'please', 'note', 'designed', 'cover', 'contain', 'comprehensive', 'listing', 'activities', 'required', 'employee', 'change', 'time', 
                'notice', 'additional', 'eligibility', 'position', 'may', 'require', 'access', 'classified', 'information', 'restricted', 'sites', 'systems', 
                'determined', 'company', 'applicable', 'government', 'employment', 'role', 'contingent', 'upon', 'ability', 'obtain', 'maintain', 'security',
                'clearance', 'other', 'authorization', 'satisfy', 'citizenship', 'imposed', 'law', 'regulation', 'executive', 'order', 'contract',
                'notified', 'when', 'such', 'affirmative', 'action', 'eeo', 'statement', 'equal', 'opportunity', 'employer', 'committed',
                'providing', 'opportunities', 'applicants', 'employees', 'without', 'regard', 'race', 'color', 'religion', 'sex', 'sexual', 'orientation',
                'gender', 'identity', 'national', 'origin', 'age', 'disability', 'genetic', 'protected', 'veteran', 'status', 'characteristic',
                'fostering', 'workplace', 'where', 'decisions', 'based', 'qualifications', 'business', 'needs', 'perform', 'essential',
                'functions', 'reasonable', 'accommodation', 'requests', 'considered', 'individual', 'basis', 'handled', 'accordance',
                'ear', 'itar', 'export', 'controlled', 'hiring', 'contractor', 'licensing', 'bureau', 'industry', 'directorate', 'defense',
                'trade', 'controls', 'benefits', 'package', 'refer', 'bottom', 'careers', 'page', 'details', 'castelion', 'hypersonic',
                'weapons', 'speed', 'scale', 'restore', 'american', 'deterrence', 'achieving', 'exceptional', 'engineering', 'rapid', 'testing',
                'manufacturing', 'capacity', 'supported', 'secure', 'reliable', 'infrastructure', 'keep', 'pace', 'hands', 'on', 'leadership',
                'troubleshooting', 'critical', 'outage', 'challenging', 'network', 'architecture', 'recruiting', 'making', 'high', 'impact',
                'investment', 'combines', 'judgment', 'relentless', 'bias', 'toward', 'action', 'standards', 'accountability', 'results',
                'banc', 'california', 'banks', 'family', 'offer', 'support', 'team', 'members', 'win', 'together', 'local', 'communities',
                'foundation', 'partnering', 'organizations', 'promote', 'literacy', 'training', 'small', 'housing', 'more', 'success', 'powered',
                'people', 'shared', 'commitment', 'delivering', 'meaningful', 'environment', 'entrepreneurial', 'thinking', 'encouraged',
                'expected', 'empowered', 'informed', 'continue', 'grow', 'evolve', 'dedicated', 'wellbeing', 'comprehensive', 'robust', 'development',
                'inclusive', 'programs', 'enable', 'best'
            }

            generic_words = {
                'build', 'lead', 'manage', 'support', 'ensure', 'develop', 'create', 'provide', 'maintain', 'handle', 'process', 'service',
                'client', 'customer', 'project', 'program', 'plan', 'strategy', 'goal', 'objectives', 'success', 'growth', 'operations',
                'functions', 'use', 'using', 'used', 'make', 'made', 'get', 'got', 'go', 'went', 'see', 'saw', 'know', 'knew', 'think',
                'thought', 'want', 'wanted', 'need', 'needed', 'help', 'helped', 'take', 'took', 'give', 'gave', 'find', 'found', 'tell', 'told',
                'ask', 'asked', 'try', 'tried', 'leave', 'left', 'call', 'called', 'move', 'moved', 'live', 'lived', 'believe', 'hold', 'bring',
                'brought', 'happen', 'write', 'wrote', 'sit', 'sat', 'stand', 'stood', 'lose', 'lost', 'pay', 'paid', 'meet', 'met', 'include',
                'included', 'set', 'learn', 'play', 'run', 'like', 'carry', 'break', 'within', 'across', 'along', 'among', 'around', 'before', 
                'behind', 'below', 'beneath', 'beside', 'between', 'beyond', 'during', 'except', 'inside', 'into', 'near', 'onto', 'upon', 
                'toward', 'throughout', 'minus', 'plus', 'versus', 'per', 'via', 'year', 'years', 'day', 'week', 'month', 'level', 'senior', 
                'junior', 'department', 'group', 'unit', 'field', 'industry', 'work', 'experience', 'ability', 'time', 'duties', 'responsibilities'
            }

            meaningful_missing = [
                word for word in missing 
                if word not in junk_words 
                and word not in generic_words
                and word not in current_industry_noise
                and len(word) > 3
            ]
            
            jd_word_counts = Counter(clean(job_description))
            prioritized_missing = sorted(meaningful_missing, key=lambda x: jd_word_counts[x], reverse=True)
            
            # --- NEW SCORES: FORMATTING, COMPLETENESS, READABILITY ---
            
            # 1. Formatting Score (Simple heuristic: check for clean lines vs complex tables)
            formatting_score = 90 # Default high
            if len(resume_text.split('\n')) < 10: formatting_score -= 20 # Too few lines
            if re.search(r'\|.*\|.*\|', resume_text): formatting_score -= 15 # Contains markdown tables
            
            # 2. Completeness Score (Check for key sections)
            completeness_score = 0
            key_sections = ['experience', 'education', 'skills', 'contact', 'summary']
            for section in key_sections:
                if section in resume_text.lower():
                    completeness_score += 20
            
            # 3. Readability Score (Based on sentence length)
            sentences = sent_tokenize(resume_text)
            avg_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
            readability_score = max(0, 100 - (avg_len - 15) * 2) # Penalize very long sentences

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
                if rejection_prob > 70: st.error("⚠️ High Risk")
                elif rejection_prob > 40: st.warning("⚠️ Moderate Risk")
                else: st.success("✅ Low Risk")

            # New Scores Row
            col_c, col_d, col_e = st.columns(3)
            with col_c:
                st.metric("Formatting Score", f"{formatting_score}/100")
            with col_d:
                st.metric("Completeness Score", f"{completeness_score}/100")
            with col_e:
                st.metric("Readability Score", f"{readability_score:.1f}/100")

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
                    jd_lines = job_description.lower().split('\n')
                    context_lines = [line.strip() for line in jd_lines if kw in line and len(line) > 10]
                    context = context_lines[0] if context_lines else "Key requirement"
                    st.markdown(f"- 🔹 **{kw.title()}**: *\"...{context[:80]}...\"*")
            else:
                st.success("Your resume already contains the top strategic keywords for this role!")

            # 6. RISK REDUCTION PLAN (REPLACES IMPROVEMENTS SECTION)
            st.markdown("---")
            st.subheader("📉 Risk Reduction Plan")
            
            target_risk = max(0, rejection_prob * 0.66) # Aim to reduce risk by 1/3
            
            st.markdown(f"**Current Risk:** {rejection_prob:.1f}% | **Target Risk:** {target_risk:.1f}%")
            st.markdown("Follow these 5 steps to significantly lower your rejection probability:")

            recommendations = []
            
            # 1. Critical Keyword Gap (Highest Impact)
            if prioritized_missing:
                top_3 = ", ".join(prioritized_missing[:3])
                recommendations.append(f"**1. Inject Top 3 Missing Keywords:** The ATS is filtering you out because it can't find **{top_3}**. Add these exact terms to your 'Skills' section and weave them into 2-3 bullet points in your most recent role.")
            else:
                recommendations.append("**1. Keyword Density Check:** Your keyword match is strong, but ensure you aren't 'keyword stuffing'. Keep density natural (2-3% of total text).")

            # 2. Quantifiable Impact (High Impact)
            if not re.search(r'\d+%', resume_text) and not re.search(r'\$[\d,]+M', resume_text):
                recommendations.append("**2. Add Hard Metrics:** Your resume lacks quantified results ($ or %). ATS algorithms prioritize candidates who prove ROI. Add at least 3 metrics (e.g., 'Reduced costs by 15%' or 'Managed $10M budget').")
            else:
                recommendations.append("**2. Amplify Existing Metrics:** You have good metrics, but move them to the **first line** of your bullet points. Example: '**$10M Savings:** Led initiative...' instead of burying it at the end.")

            # 3. Section Completeness (Medium Impact)
            if completeness_score < 80:
                missing_secs = [s for s in ['Summary', 'Skills', 'Education'] if s.lower() not in resume_text.lower()]
                recommendations.append(f"**3. Complete Missing Sections:** The ATS cannot score you fully without a **{', '.join(missing_secs)}** section. Add these immediately to boost your Completeness Score.")
            else:
                recommendations.append("**3. Optimize Section Headers:** Ensure your headers are standard (e.g., use 'Professional Experience' instead of 'My Journey'). Standard headers help the ATS parse your timeline correctly.")

            # 4. Seniority/Leadership Signal (Medium Impact)
            if 'lead' not in resume_text.lower() and 'manage' not in resume_text.lower() and 'direct' not in resume_text.lower():
                recommendations.append("**4. Strengthen Leadership Verbs:** For executive roles, the ATS looks for leadership signals. Replace passive verbs with active leadership terms like 'Directed,' 'Orchestrated,' or 'Spearheaded.'")
            else:
                recommendations.append("**4. Highlight Governance & Strategy:** For senior roles, ensure you mention 'Strategy,' 'Governance,' or 'Roadmap' in your summary. This signals executive-level thinking to the parser.")

            # 5. Formatting/Parseability (Low but Critical Impact)
            if formatting_score < 80:
                recommendations.append("**5. Simplify Formatting:** Your Formatting Score is low. Remove complex tables, text boxes, or graphics from your header. Use a clean, single-column layout to ensure the ATS reads your contact info correctly.")
            else:
                recommendations.append("**5. Verify Contact Info Parsing:** Go to the 'ATS AI Parser' tab. If your Name or Email is missing from the raw text, move them out of headers/footers and into the main body text.")

            for i, rec in enumerate(recommendations):
                st.markdown(f"> {rec}")

        elif not uploaded_file or not job_description:
            st.info("Please upload a resume and paste a Job Description to start.")

# --- TAB 2: ATS AI PARSER (ENHANCED WITH ROBUST NAME DETECTION & PREVIEW) ---
with tab2:
    st.subheader("🤖 ATS AI Parser: What the Robot Sees")
    st.markdown("This report simulates how an AI-driven ATS extracts and categorizes data from your resume.")
    
    col_parse1, col_parse2 = st.columns([1, 1])
    
    with col_parse1:
        parse_file = st.file_uploader("Upload resume to parse", type=['pdf', 'docx'], key="parse_upload")
        
        if parse_file:
            raw_text = get_text(parse_file)
            
            # 1. Name Detected (Robust Logic for Table Headers)
            # Look for All-Caps words at the start of the document (first 500 chars)
            header_snippet = raw_text[:500]
            name_match = re.search(r'([A-Z][A-Z\s]+?[A-Z])', header_snippet)
            if name_match:
                name = name_match.group(1).strip()
                # Clean up extra spaces from table extraction
                name = re.sub(r'\s+', ' ', name)
            else:
                name = "Not Detected"
            
            # 2. Address Detected
            address_match = re.search(r'([A-Za-z\s]+, [A-Z]{2}\s+\d{5})', raw_text)
            address = address_match.group(1) if address_match else "Not Detected"
            
            # 3. Email Detected
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
            email = email_match.group(0) if email_match else "Not Detected"
            
            # 4. Sections Detected
            sections = []
            section_keywords = ['summary', 'experience', 'education', 'skills', 'certifications', 'projects', 'competencies']
            for sec in section_keywords:
                if sec in raw_text.lower():
                    sections.append(sec.title())
            
            # 5. Skills Recognized
            skill_keywords = ['python', 'aws', 'azure', 'sql', 'leadership', 'agile', 'docker', 'kubernetes', 'ai', 'llm', 'soc 2', 'hipaa', 'cloudflare', 'okta', 'generative ai']
            found_skills = [s for s in skill_keywords if s in raw_text.lower()]
            
            # 6. LinkedIn
            linkedin_match = re.search(r'linkedin\.com/in/[a-zA-Z0-9_-]+', raw_text)
            linkedin = linkedin_match.group(0) if linkedin_match else "Not Detected"
            
            # 7. Date Range
            date_matches = re.findall(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b', raw_text)
            dates = list(set(date_matches)) # Unique months/years found
            
            # 8. Bullet Points
            bullet_count = len(re.findall(r'^\s*[\-\*\•]\s', raw_text, re.MULTILINE))
            
            # 9. Quantified Impact ($ or %)
            impacts = re.findall(r'(\$[\d,]+M+|\d+%)', raw_text)
            
            # 10. Word Count
            word_count = len(raw_text.split())
            
            # 11. Seniority Signal
            seniority_terms = ['chief', 'head', 'director', 'vp', 'vice president', 'senior', 'lead', 'cto', 'cio']
            seniority_found = [s for s in seniority_terms if s in raw_text.lower()]
            seniority_signal = "Executive / Leadership" if any(s in ['chief', 'head', 'vp', 'vice president', 'cto', 'cio'] for s in seniority_found) else "Mid-Level"
            
            # 12. Industry Match
            industry_terms = {
                "Healthcare": ['hipaa', 'emr', 'ehr', 'patient', 'clinic', 'kaiser', 'acuity'],
                "Finance": ['bank', 'credit', 'fraud', 'pci-dss', 'sox', 'infosend'],
                "Tech": ['saas', 'cloud', 'api', 'devops', 'llm', 'icann'],
                "Defense": ['clearance', 'itar', 'defense', 'government']
            }
            detected_industries = [ind for ind, terms in industry_terms.items() if any(t in raw_text.lower() for t in terms)]

            # Display Parsing Report
            st.markdown("### 📋 Parsing Report")
            st.markdown(f"**1. Name Detected:** `{name}`")
            st.markdown(f"**2. Address Detected:** `{address}`")
            st.markdown(f"**3. Email Detected:** `{email}`")
            st.markdown(f"**4. Sections Found:** {', '.join(sections) if sections else 'None'}")
            st.markdown(f"**5. Skills Recognized:** {', '.join(found_skills) if found_skills else 'None'}")
            st.markdown(f"**6. LinkedIn:** `{linkedin}`")
            st.markdown(f"**7. Date Formats:** {', '.join(dates[:5]) if dates else 'None'}")
            st.markdown(f"**8. Bullet Points:** {bullet_count}")
            st.markdown(f"**9. Quantified Impact:** {', '.join(impacts) if impacts else 'None'}")
            st.markdown(f"**10. Word Count:** {word_count}")
            st.markdown(f"**11. Seniority Signal:** {seniority_signal}")
            st.markdown(f"**12. Industry Match:** {', '.join(detected_industries) if detected_industries else 'General'}")

    with col_parse2:
        if parse_file:
            st.markdown("### 📝 Raw Text Preview")
            st.markdown("*Click below to view the full unformatted text the ATS processes:*")
            
            # Button to open modal
            if st.button("👁️ Open Full Raw Text Preview", use_container_width=True):
                st.session_state['show_raw_text'] = True
            
            # Modal logic
            if st.session_state.get('show_raw_text', False):
                with st.expander("Full Raw Text Extract", expanded=True):
                    st.code(raw_text, language="text")
                    if st.button("Close Preview"):
                        st.session_state['show_raw_text'] = False
                        st.rerun()

# --- TAB 3: AI RESUME REWRITER ---
with tab3:
    st.subheader("📝 AI-Powered Resume Rewriter")
    st.markdown("Suggests how to rewrite bullet points to include high-value keywords from the Job Description.")
    
    if uploaded_file and job_description:
        if 'resume_text' not in locals():
            resume_text = get_text(uploaded_file)

        st.markdown("---")
        st.subheader("🎯 Suggested Bullet Point Improvements")
        
        # Recalculate missing if needed
        if 'prioritized_missing' not in locals():
             res_tokens = set(clean(resume_text))
             jd_tokens = set(clean(job_description))
             missing = jd_tokens - res_tokens
             jd_word_counts = Counter(clean(job_description))
             # Simplified filter for this tab
             prioritized_missing = sorted([w for w in missing if len(w)>3], key=lambda x: jd_word_counts[x], reverse=True)

        top_missing = prioritized_missing[:3] if 'prioritized_missing' in locals() else []
        
        if top_missing:
            st.markdown(f"Based on the **{industry}** job description, try rewriting your bullet points to include these terms:")
            
            for keyword in top_missing:
                jd_context = [line.strip() for line in job_description.lower().split('\n') if keyword in line and len(line) > 20]
                context_snippet = jd_context[0] if jd_context else f"Required expertise in {keyword}"
                
                st.markdown(f"**🔹 Keyword: {keyword.title()}**")
                st.markdown(f"*JD Context:* \"{context_snippet[:100]}...\"")
                
                if "security" in keyword or "compliance" in keyword:
                    suggestion = f"\"Led enterprise-wide **{keyword}** initiatives, aligning infrastructure with **NIST** frameworks and reducing regulatory risk by 40%.\""
                elif "cloud" in keyword or "infrastructure" in keyword:
                    suggestion = f"\"Architected scalable **{keyword}** solutions across multi-site environments, improving operational efficiency and supporting rapid business growth.\""
                elif "ai" in keyword or "data" in keyword:
                    suggestion = f"\"Spearheaded **{keyword}** adoption through governed AI frameworks, delivering measurable ROI and enhancing decision-making capabilities.\""
                else:
                    suggestion = f"\"Directed cross-functional teams to implement **{keyword}** best practices, resulting in improved system reliability and stakeholder satisfaction.\""
                
                st.markdown(f"*💡 **Suggested Rewrite:** {suggestion}*")
                st.markdown("")
        else:
            st.success("Your resume is already well-aligned with the top keywords!")
    else:
        st.info("Please upload a resume and paste a Job Description in Tab 1 to use this feature.")

# --- TAB 4: C-SUITE NARRATIVE ---
with tab4:
    st.subheader("👔 C-Suite Narrative Generator")
    st.markdown("Generate five distinct Executive Summaries tailored to different leadership archetypes.")
    
    if uploaded_file and job_description:
        if 'resume_text' not in locals():
            resume_text = get_text(uploaded_file)

        metrics = {
            "savings": "$10M+" if "$10M" in resume_text else "significant cost savings",
            "portfolio": "$20M+" if "$20M" in resume_text else "multi-million dollar portfolios",
            "team": "120+" if "120" in resume_text else "large-scale global teams",
            "revenue": "12%" if "12%" in resume_text else "double-digit revenue growth",
            "uptime": "99.99%" if "99.99" in resume_text else "high-availability standards"
        }

        st.markdown("---")
        
        st.markdown("### 🏗️ Archetype 1: The Transformer")
        st.markdown("*Best for: Modernization, Legacy Migration, and Efficiency.*")
        transformer_narrative = (
            f"Transformational technology executive with extensive experience leading enterprise IT strategy and cloud modernization. "
            f"Proven track record of managing **{metrics['portfolio']}** technology portfolios and directing **{metrics['team']}** person teams. "
            f"Expert in translating complex technical roadmaps into measurable board-level outcomes, including delivering **{metrics['savings']}** in cost savings and driving **{metrics['revenue']}** revenue cycle improvements. "
            f"Specializes in legacy-to-cloud migrations, DevSecOps automation, and embedding cybersecurity into high-speed delivery models."
        )
        st.info(transformer_narrative)
        st.download_button("Download Transformer Narrative", transformer_narrative, file_name="transformer_summary.txt")

        st.markdown("---")
        st.markdown("### 🛡️ Archetype 2: The Guardian")
        st.markdown("*Best for: Security, Compliance, and Risk.*")
        guardian_narrative = (
            f"Strategic IT leader with deep expertise in Cybersecurity, Zero Trust Architecture, and Regulatory Compliance. "
            f"Successfully managed **{metrics['portfolio']}** in technology investments while maintaining rigorous audit readiness and reducing lateral movement risk. "
            f"Trusted partner to Legal and Security teams, ensuring enterprise initiatives are governed by robust data privacy and model lifecycle management frameworks. "
            f"Committed to protecting sensitive infrastructure while enabling secure, scalable business growth."
        )
        st.info(guardian_narrative)
        st.download_button("Download Guardian Narrative", guardian_narrative, file_name="guardian_summary.txt")

        st.markdown("---")
        st.markdown("### 🚀 Archetype 3: The Innovator")
        st.markdown("*Best for: AI Adoption, Revenue Growth, and Competitive Advantage.*")
        innovator_narrative = (
            f"Visionary C-suite executive specializing in Generative AI (GenAI), LLM adoption, and Data-Driven Innovation. "
            f"Pioneered enterprise AI infrastructure and governed 'Big Swing' AI initiatives that delivered **{metrics['revenue']}** revenue lifts and **{metrics['savings']}** in operational efficiencies. "
            f"Expert in bridging the gap between technical engineering teams and business stakeholders to deploy Agentic AI, RAG, and predictive modeling at scale. "
            f"Focused on turning technology into a primary driver of EBITDA and market differentiation."
        )
        st.info(innovator_narrative)
        st.download_button("Download Innovator Narrative", innovator_narrative, file_name="innovator_summary.txt")

        st.markdown("---")
        st.markdown("### ⚙️ Archetype 4: The Operator")
        st.markdown("*Best for: Stability, Uptime, and Cost-Efficiency.*")
        operator_narrative = (
            f"Results-oriented IT executive with a relentless focus on operational excellence and service reliability. "
            f"Managed **{metrics['portfolio']}** budgets while achieving **{metrics['uptime']}** availability across global hybrid-cloud environments. "
            f"Expert in rationalizing technology portfolios, negotiating enterprise vendor contracts, and implementing ITIL-based service management frameworks. "
            f"Proven ability to stabilize complex infrastructures and deliver consistent, predictable value to the business."
        )
        st.info(operator_narrative)
        st.download_button("Download Operator Narrative", operator_narrative, file_name="operator_summary.txt")

        st.markdown("---")
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
        st.info("Please upload a resume and paste a Job Description in Tab 1 to generate narratives.")

# --- TAB 5: EXPERIENCE REFRAMING (SMART LOGIC) ---
with tab5:
    st.subheader("🔄 Experience Reframing")
    st.markdown("Paste a specific block of your job history below. The tool will dynamically rewrite it into 5 executive narratives based on the Job Description you provided in Tab 1.")
    
    if uploaded_file and job_description:
        if 'resume_text' not in locals():
            resume_text = get_text(uploaded_file)

        experience_block = st.text_area("Paste your Job History / Bullet Points here:", height=200, placeholder="Example: Led a team of 50 engineers...")
        
        col_ref1, col_ref2 = st.columns(2)
        with col_ref1:
            generate_button = st.button("✨ Generate Dynamic Narratives", use_container_width=True)
        with col_ref2:
            reset_reframe = st.button("🔄 Reset Input", use_container_width=True)

        if reset_reframe:
            st.session_state.pop('experience_block', None)
            st.rerun()
        
        if generate_button and experience_block:
            # Smart Keyword Extraction from User Input
            # We look for specific high-value terms rather than just cleaning everything
            high_value_terms = [
                "Four Pillars", "IT Transformation", "Legacy Modernization", "Governed AI", 
                "Visual FoxPro", "C#", "Python", "Claude", "QWEN", "SOC 2", "PCI-DSS", 
                "HIPAA", "NIST", "WCAG", "ADA", "ELLA", "Enterprise AI", "LLM routing", 
                "Big Swing", "AI Governance", "Data Privacy", "Model Lifecycle", "Zero Trust",
                "Okta", "Cloudflare", "Kubernetes", "Docker", "CI/CD", "EMR", "EHR", 
                "Revenue Cycle", "Voice AI", "Conversational AI", "Agentic AI", "RAG",
                "Google Cloud", "BigQuery", "FOCUS", "ASC", "Optical", "Claims", "EBITDA",
                "Center of Excellence", "CoE", "Dashboards", "IVR", "Patient Satisfaction"
            ]
            
            found_terms = [term for term in high_value_terms if term.lower() in experience_block.lower()]
            
            # Fallback to generic keywords if no specific terms found
            if not found_terms:
                user_tokens = set(clean(experience_block))
                found_terms = [w for w in user_tokens if len(w) > 3 and w not in set(nltk.corpus.stopwords.words('english'))][:3]

            # Find overlapping high-value keywords from the JD
            if 'prioritized_missing' not in locals():
                 res_tokens = set(clean(resume_text))
                 jd_tokens = set(clean(job_description))
                 missing = jd_tokens - res_tokens
                 jd_word_counts = Counter(clean(job_description))
                 prioritized_missing = sorted([w for w in missing if len(w)>3], key=lambda x: jd_word_counts[x], reverse=True)

            jd_high_value = [w for w in prioritized_missing[:5] if w in experience_block.lower()]
            
            # Construct dynamic narratives with proper formatting
            st.markdown("---")
            
            # 1. The Strategic Pivot
            st.markdown("### 🏛️ 1. The Strategic Pivot")
            st.info(f"**Focus:** Board-level impact and long-term vision.\n\n- Spearheaded enterprise-wide transformation by implementing **{', '.join(found_terms[:2])}**, aligning technical execution with corporate growth objectives.\n- Translated complex roadmaps into measurable business outcomes, directly supporting the organization's strategic pivot toward **{jd_high_value[0] if jd_high_value else 'operational excellence'}**.")
            
            # 2. The Technical Deep-Dive
            st.markdown("### ⚙️ 2. The Technical Deep-Dive")
            st.info(f"**Focus:** Hands-on engineering and architecture.\n\n- Architected and deployed scalable solutions focused on **{', '.join(found_terms[:2])}**.\n- Directed hands-on engineering teams in implementing **{jd_high_value[0] if jd_high_value else 'modern infrastructure'}**, ensuring robust CI/CD pipelines, Zero Trust security, and high-availability systems.")
            
            # 3. The Compliance & Risk Focus
            st.markdown("### 🛡️ 3. The Compliance & Risk Focus")
            st.info(f"**Focus:** Governance, Audit, and Security.\n\n- Established rigorous governance frameworks while executing **{', '.join(found_terms[:2])}**.\n- Partnered with Legal and Security to mitigate risks and ensure 100% audit readiness for initiatives involving **{jd_high_value[0] if jd_high_value else 'sensitive data'}**.")
            
            # 4. The Financial & ROI Focus
            st.markdown("### 💰 4. The Financial & ROI Focus")
            st.info(f"**Focus:** P&L, Cost Reduction, and Revenue.\n\n- Optimized technology spend and operational efficiency through **{', '.join(found_terms[:2])}**.\n- Achieved measurable ROI by streamlining workflows and implementing **{jd_high_value[0] if jd_high_value else 'intelligent automation'}**, directly contributing to bottom-line growth.")
            
            # 5. The Modernization & Change Leader
            st.markdown("### 🚀 5. The Modernization & Change Leader")
            st.info(f"**Focus:** Culture, Scaling, and Adoption.\n\n- Led cultural transformation by democratizing **{', '.join(found_terms[:2])}** and upskilling non-technical teams.\n- Built and scaled high-performing organizations, fostering a culture of accountability and rapid innovation around **{jd_high_value[0] if jd_high_value else 'new technologies'}**.")

            # SUMMARY OF WHY THIS WORKS
            st.markdown("---")
            st.markdown("### 💡 Why this Narrative Works")
            st.markdown(f"""
            - **Specificity:** By using terms like **'{found_terms[0] if found_terms else 'your key achievement'}'**, we move beyond generic management speak to show tangible technical leadership.
            - **Relevance:** We aligned your experience with the JD's priority on **'{jd_high_value[0] if jd_high_value else 'core business goals'}'**, showing you understand their specific pain points.
            - **Impact:** The language focuses on **outcomes** (ROI, governance, scaling) rather than just duties, which is what C-suite hiring managers look for.
            """)

        elif generate_button and not experience_block:
             st.warning("Please paste some text from your resume first!")
    else:
        st.info("Please upload a resume and paste a Job Description in Tab 1 to use this feature.")

# Footer
