import re
from io import BytesIO
from pdfminer.high_level import extract_text as extract_text_from_pdf
from docx import Document

def extract_text(file):
    """Extracts text from PDF or DOCX resumes."""
    file_type = file.name.split('.')[-1].lower()

    if file_type == "pdf":
        return extract_text_from_pdf(file)
    elif file_type == "docx":
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return ""

def extract_email(text):
    """Extracts the first valid email from the text using regex."""
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return emails[0] if emails else "N/A"  

def extract_name(text):
    """Extracts the candidate's name from the resume text using regex."""
    
    # Remove common misleading words
    text = re.sub(r'\b(Resume|Candidate)\b[:\s]*', '', text, flags=re.IGNORECASE)

    # Look for "Name: [First Last]" pattern
    match = re.search(r"Name:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)", text)
    if match:
        return match.group(1)

    # Fallback: Look for first two consecutive title-cased words
    words = text.split()
    for i in range(len(words) - 1):
        if words[i].istitle() and words[i+1].istitle():
            return f"{words[i]} {words[i+1]}"

    return "Unknown Candidate"





