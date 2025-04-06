import sqlite3
import re
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
from difflib import get_close_matches

# Load models
model = SentenceTransformer('all-MiniLM-L6-v2')  # You can upgrade to all-mpnet-base-v2 for better results
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Fetch data
def fetch_semantic_data():
    conn = sqlite3.connect("semantic_search.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, cv_text, job_role FROM semantic_data")
    rows = cursor.fetchall()
    conn.close()
    return rows, None

# Clean text utility
def clean_text(text):
    return re.sub(r"[^a-zA-Z0-9\s]", "", text).strip().lower()

# Summarize long CV text
def summarize_text(text):
    try:
        return summarizer(text[:1024], max_length=100, min_length=30, do_sample=False)[0]['summary_text']
    except:
        return "Summary not available."

# Extract tech stack
def extract_tech_stack(cv_text):
    tech_keywords = [
        "python", "java", "c++", "c#", "javascript", "typescript", "react", "angular", "vue",
        "node.js", "flask", "django", "sql", "mysql", "postgresql", "mongodb", "aws", "azure",
        "gcp", "docker", "kubernetes", "tensorflow", "pytorch", "pandas", "numpy", "matplotlib"
    ]
    found = set()
    text = clean_text(cv_text)
    for tech in tech_keywords:
        if tech in text:
            found.add(tech)
    return ', '.join(sorted(found)) if found else "Not specified"

# Summarize a candidate by name using fuzzy match
def find_candidate_by_name(name_query, data):
    names = [name for name, _, _, _ in data]
    matches = get_close_matches(name_query.lower(), [n.lower() for n in names], n=1, cutoff=0.6)
    if not matches:
        return None
    for name, email, cv_text, _ in data:
        if matches[0] in name.lower():
            return {
                "Name": name,
                "Email": email,
                "Skills & Experience": summarize_text(cv_text),
                "Tech Stack": extract_tech_stack(cv_text)
            }
    return None

# Smart HR Prompt Search
def search_candidates(prompt):
    data, error = fetch_semantic_data()
    if error or not data:
        return None, "No candidate data found."

    prompt_clean = clean_text(prompt)

    # 1. Check if it's a "summarize" prompt
    name_match = re.search(r"(?:summarize|summary\s+of)\s+([a-zA-Z\s]+)", prompt_clean)
    if name_match:
        name_query = name_match.group(1).strip()
        result = find_candidate_by_name(name_query, data)
        if result:
            return [result], None
        else:
            return None, f"No candidate matching '{name_query}' found."

    # 2. Extract how many top candidates
    num_match = re.search(r"(?:top|best|give\s+me\s+|show\s+|give\s+)(\d+)", prompt_clean)
    top_n = int(num_match.group(1)) if num_match else 5

    # 3. Extract job role more flexibly
    job_match = re.search(r"(?:for|of|to|as)\s+([a-zA-Z\s]+)", prompt_clean)
    job_filter = job_match.group(1).replace("role", "").replace("position", "").strip() if job_match else None

    # 4. Extract required tech skills
    tech_skill_match = re.findall(r"(?:knowledge\s+of|with|having)\s+([a-zA-Z0-9+#.\-]+)", prompt_clean)
    required_skills = [clean_text(skill) for skill in tech_skill_match]

    prompt_embedding = model.encode(prompt_clean, convert_to_tensor=True)
    results = []

    for name, email, cv_text, job_role in data:
        # Flexible role matching
        if job_filter:
            role_similarity = float(util.pytorch_cos_sim(
                model.encode(job_filter, convert_to_tensor=True),
                model.encode(job_role, convert_to_tensor=True)
            )[0][0])
            if role_similarity < 0.5:
                continue

        # Tech skill filtering
        if required_skills:
            cv_clean = clean_text(cv_text)
            if not all(skill in cv_clean for skill in required_skills):
                continue

        # Semantic similarity
        cv_embedding = model.encode(cv_text, convert_to_tensor=True)
        similarity = float(util.pytorch_cos_sim(prompt_embedding, cv_embedding)[0][0])
        results.append((name, email, similarity, cv_text))

    if not results:
        return None, f"No matching candidates found for role '{job_filter}' with skills '{', '.join(required_skills)}'." if job_filter or required_skills else "No candidates matched the prompt."

    # Sort by similarity score
    results.sort(key=lambda x: x[2], reverse=True)

    # Deduplicate by email and limit to top N
    seen_emails = set()
    top_results = []
    for name, email, _, cv_text in results:
        if email in seen_emails:
            continue
        seen_emails.add(email)
        top_results.append({
            "Name": name,
            "Email": email,
            "Skills & Experience": summarize_text(cv_text),
            "Tech Stack": extract_tech_stack(cv_text)
        })
        if len(top_results) >= top_n:
            break

    return top_results[:top_n], None  

