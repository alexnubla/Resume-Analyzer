# 📄 Resume Evaluator & ATS Optimizer

A sophisticated, AI-powered resume analysis tool designed for modern executives and technical leaders. Built with **Streamlit**, **Python**, and **NLP**, this application goes beyond simple keyword matching to provide strategic career pivoting advice, executive-level narrative generation, and deep ATS parseability checks.

🚀 **Live Demo:** [https://resume-scorer.streamlit.app](https://resume-scorer.streamlit.app)

---

## 🌟 Key Features

### 1. 🎯 Industry-Specific ATS Analysis
Unlike generic checkers, this tool allows you to select a **Target Industry** (e.g., Defense, Healthcare, Banking, Tech). It uses dynamic filtering to:
*   Ignore industry-specific "noise" words that don't apply to your target role.
*   Prioritize high-value keywords based on weighted sections (Responsibilities vs. Legal Disclaimers).
*   Calculate a **Rejection Risk Score** and **Keyword Match Percentage**.

### 2. 🤖 ATS AI Parser
Simulates exactly how an Applicant Tracking System "sees" your resume. It extracts and validates:
*   **Contact Info:** Name, Email, Phone, LinkedIn.
*   **Structure:** Sections, Bullet Points, Date Ranges.
*   **Impact:** Quantified metrics ($, %) and Seniority Signals.
*   **Raw Text Preview:** View the unformatted text to ensure headers and tables aren't hiding critical data.

### 3. 👔 C-Suite Narrative Generator
Generates five distinct Executive Summaries tailored to different leadership archetypes:
*   **The Transformer:** Focuses on modernization and efficiency.
*   **The Guardian:** Highlights security, compliance, and risk.
*   **The Innovator:** Showcases AI adoption and revenue growth.
*   **The Operator:** Emphasizes stability and uptime.
*   **The Product-Minded Leader:** Focuses on user experience and agility.

### 4. 🔄 Experience Reframing
Paste a specific block of your job history, and the tool will dynamically rewrite it into five executive narratives based on your target Job Description. It intelligently extracts your unique achievements (e.g., "ELLA," "FoxPro Migration," "SOC 2") and weaves them into targeted stories.

### 5. 📝 AI-Powered Rewriter
Suggests specific bullet point improvements by identifying missing high-value keywords from the Job Description and providing context-aware rewrite templates.

---

## 🛠️ Tech Stack

*   **Frontend:** Streamlit
*   **Backend:** Python
*   **NLP:** NLTK (Natural Language Toolkit)
*   **File Processing:** PyPDF2, python-docx
*   **Data Handling:** Collections, Re (Regex)

---

## 🚀 How to Use

1.  **Select Your Industry:** Choose your target sector from the sidebar to optimize the filtering logic.
2.  **Upload Your Resume:** Supports PDF and DOCX formats.
3.  **Paste the Job Description:** Copy the full JD from the company website.
4.  **Explore the Tabs:**
    *   **ATS Analysis:** Get your score and missing keywords.
    *   **Parseability Check:** Ensure the robot can read your contact info.
    *   **AI Rewriter:** Get specific bullet point suggestions.
    *   **C-Suite Narrative:** Generate a tailored executive summary.
    *   **Experience Reframing:** Rewrite specific job blocks for maximum impact.

---

## 💡 Why This Tool?

As technology leaders, we know that ATS systems are more than just keyword counters—they are gatekeepers. This tool was built to bridge the gap between **technical depth** and **executive storytelling**, helping professionals pivot industries (e.g., from Healthcare IT to Defense Aerospace) by highlighting transferable skills like **NIST compliance**, **Zero Trust**, and **AI Governance**.

---

## 📦 Local Installation

If you want to run this locally:

1.  Clone the repository:
    ```bash
    git clone https://github.com/alexnubla/Resume-Analyzer.git
    cd Resume-Analyzer
    ```
2.  Create a virtual environment and install dependencies:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  Run the app:
    ```bash
    streamlit run app.py
    ```

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

**Built with ❤️ by Alex Nubla**  
*Head of IT | AI & Cloud Transformation Leader*
