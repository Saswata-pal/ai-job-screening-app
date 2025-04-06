from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline

def extract_job_role(jd_text):
    """Extract the job role/title from a given job description."""
    
    # Step 1: Summarize JD to make it concise
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(jd_text, max_length=50, min_length=20, do_sample=False)
    summarized_text = summary[0]['summary_text']


    # Step 2: Use FLAN-T5 to extract only the job title
    hf_llm = HuggingFacePipeline.from_model_id(
        model_id="google/flan-t5-large",  # More accurate than small models
        task="text2text-generation"
    )

    # Step 3: Prompt FLAN-T5 to extract only the job role
    job_role_prompt = f"Extract only the job title from this job description: {summarized_text}"
    job_role = hf_llm.invoke(job_role_prompt)

    return job_role.strip()
