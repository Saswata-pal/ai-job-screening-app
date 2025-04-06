new_job/
├── .env                      # Stores sensitive environment variables like API keys and config values
├── email_sender.py           # Handles sending call letters/emails to shortlisted candidates via SMTP
├── hr_prompt_search.py       # Uses prompt engineering to help HR refine and search the best fit candidate criteria dynamically.
├── jd_summarizer.py          # Summarizes job descriptions to extract core roles, responsibilities, and required skills
├── job_screening.db          # SQLite database storing parsed resumes, job data, and ATS (Applicant Tracking System) scores
├── keyword_extraction.py     # Extracts relevant keywords from summarized job descriptions to aid in scoring resumes
├── main.py                   # Main orchestrator script that runs the multi-agent system to automate the hiring process
├── requirements.txt          # Contains all Python package dependencies needed to run the project
├── resume_parser.py          # Parses resume files (PDF, DOCX) and converts them into structured, machine-readable format
├── shortlisting.py           # Applies ATS scoring, filters candidates, and handles verification steps for shortlisting
├── __pycache__/              # Python's bytecode cache directory for faster module 
