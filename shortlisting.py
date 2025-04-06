import sqlite3 
from keyword_extraction import extract_keywords  

def shortlist_candidate(cv_text, email, name, jd_text, job_role):
    """Calculate ATS score and update database if shortlisted."""

    jd_keywords = extract_keywords(jd_text)  
    score = calculate_ats_score(cv_text, jd_keywords)

    conn = sqlite3.connect("job_screening.db")  
    cursor = conn.cursor()
    
    # Added job_role to schema
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, 
            email TEXT UNIQUE, 
            score INTEGER,
            job_role TEXT
        )"""
    )

    if score >= 70:
        cursor.execute("SELECT * FROM candidates WHERE email=?", (email,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO candidates (name, email, score, job_role) VALUES (?, ?, ?, ?)", 
                (name, email, score, job_role)
            )
            conn.commit()

    conn.close()
    return score

def calculate_ats_score(text, jd_keywords):
    """Improved ATS score calculation to prevent excessive 100% scores."""
    words = text.lower().split()
    matched_keywords = sum(1 for word in words if word in jd_keywords)

    # Adjust weight to avoid all 100% matches
    score = min(100, (matched_keywords / max(len(jd_keywords) + 5, 1)) * 100)
    return round(score)
