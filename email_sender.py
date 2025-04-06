import os 
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate

# Load environment variables for email credentials
load_dotenv()
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Load the HF model
model_name = "MBZUAI/LaMini-Flan-T5-783M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Create pipeline
text_gen_pipeline = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=300,
    temperature=0.7,
    top_p=0.9,
)

# LangChain-compatible wrapper
llm = HuggingFacePipeline(pipeline=text_gen_pipeline)

# Improved PromptTemplate
email_prompt_template = PromptTemplate.from_template("""
Write a professional and clear interview invitation email using the format below:

Dear {name},
                                                     
                                                     

Congratulations! You scored {score}% in our AI-powered screening for the {job_role} role.

Based on a comprehensive evaluation of your profile, we are pleased to invite you for an interview. We believe your skills and background align well with the requirements of this position.

If you have a portfolio, GitHub repository, or a demo project you'd like to share, please include it in your response.


Best regards,
HR Team
""")

# Function to generate formatted email body
def generate_email(name, job_role, score):
    formatted_prompt = email_prompt_template.format(name=name, job_role=job_role, score=score)
    response = llm.invoke(formatted_prompt)

    if isinstance(response, list):
        content = response[0].get("generated_text", "")
    elif isinstance(response, str):
        content = response
    else:
        content = str(response)

    return content.strip()

# Function to send email
def send_email(recipient_email, name, job_role, score):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print(" Email credentials not found in environment variables.")
        return

    subject = f"Interview Invitation for {job_role} Role"
    content = generate_email(name, job_role, score)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = recipient_email
    msg.set_content(content)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"Email sent to {name} at {recipient_email}")
    except Exception as e:
        print(f" Error sending email to {name}: {e}")
