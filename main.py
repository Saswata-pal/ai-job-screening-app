import streamlit as st
import sqlite3
from resume_parser import extract_text, extract_email, extract_name
from shortlisting import calculate_ats_score, shortlist_candidate
from email_sender import send_email
from keyword_extraction import extract_keywords
from jd_summarizer import extract_job_role
from hr_prompt_search import search_candidates

# -------------------------- UI SETUP --------------------------
st.set_page_config(page_title="AI Job Screening", page_icon="🧠")
st.title("🧠 AI-Powered Job Screening System")

# ----------------------- SESSION STATE ------------------------
for key in ["processed", "applied", "shortlisted", "job_role", "jd_text"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ["applied", "shortlisted"] else False if key == "processed" else ""

# ---------------------- JOB DESCRIPTION -----------------------
st.subheader("📄 Job Description ")
jd_input = st.text_area("Paste or write the job description below:", value=st.session_state.jd_text)

if jd_input:
    st.session_state.jd_text = jd_input
    st.session_state.job_role = extract_job_role(jd_input)
    st.markdown(f"**🔖 Extracted Role:** `{st.session_state.job_role}`")

# ---------------------- RESUME UPLOAD -------------------------
st.subheader("📂 Upload Candidate Resumes")
cv_files = st.file_uploader("Upload resumes (PDF or DOCX):", type=["pdf", "docx"], accept_multiple_files=True)

# -------------------- RESUME PROCESSING -----------------------
if st.session_state.jd_text and cv_files and not st.session_state.processed:
    jd_keywords = extract_keywords(st.session_state.jd_text)

    with st.spinner("⏳ Processing resumes and shortlisting..."):
        for cv_file in cv_files:
            cv_text = extract_text(cv_file)
            email = extract_email(cv_text)
            name = extract_name(cv_text) or cv_file.name.replace(".pdf", "").replace(".docx", "")
            score = shortlist_candidate(cv_text, email, name, st.session_state.jd_text, st.session_state.job_role)

            # Store in applied list
            st.session_state.applied.append({"Name": name, "Score": score, "Email": email})

            # Shortlist and send email
            if score >= 70:
                st.session_state.shortlisted.append({"Name": name, "Score": score, "Email": email})
                send_email(email, name, st.session_state.job_role, score)

            # Store in semantic DB
            try:
                conn = sqlite3.connect("semantic_search.db")
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS semantic_data (
                        name TEXT,
                        email TEXT,
                        score INTEGER,
                        cv_text TEXT,
                        jd_text TEXT,
                        job_role TEXT
                    )
                """)
                cursor.execute("""
                    INSERT INTO semantic_data (name, email, score, cv_text, jd_text, job_role)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, email, score, cv_text, st.session_state.jd_text, st.session_state.job_role))
                conn.commit()
                conn.close()
            except Exception as e:
                st.warning(f"⚠️ Failed to save data for {name}: {e}")

    st.session_state.processed = True
    st.success("✅ Resume processing completed and emails sent!")

# ---------------------- RESULTS DISPLAY -----------------------
if st.session_state.applied:
    st.subheader("📋 Applied Candidates")
    st.table(st.session_state.applied)

if st.session_state.shortlisted:
    st.subheader("✅ Shortlisted Candidates")
    st.table(st.session_state.shortlisted)

# ------------------ HR PROMPT SEARCH BLOCK --------------------
st.subheader("🔍 HR Prompt Search ")
with st.expander("💡 Example Prompts", expanded=False):
    st.markdown("""
    - `Give 5 candidates who have knowledge of Java and fit for backend role`
    - `Top 3 candidates with React for frontend`
    - `Summarize lewra lason's profile`
    """)

search_prompt = st.text_input("Enter your prompt:", placeholder="Type here...")

if search_prompt:
    with st.spinner("🤖 Searching..."):
        results, error = search_candidates(search_prompt)

    if error:
        st.warning(error)
    elif results:
        st.success(f"✅ Found {len(results)} result(s):")
        for candidate in results:
            with st.expander(f"👤 {candidate['Name']}"):
                st.markdown(f"**📧 Email:** {candidate['Email']}")
                st.markdown(f"**💼 Skills & Experience:**\n{candidate['Skills & Experience']}")
                st.markdown(f"**🛠️ Tech Stack:**\n{candidate['Tech Stack']}")
                st.markdown("---")

# ------------------------- RESET ------------------------------
st.markdown("___")
if st.button("🔁 Reset and Upload New JD"):
    for key in ["processed", "applied", "shortlisted", "job_role", "jd_text"]:
        st.session_state[key] = [] if key in ["applied", "shortlisted"] else False if key == "processed" else ""
    st.rerun()
