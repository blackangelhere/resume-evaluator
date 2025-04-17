from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pdfplumber
import openai
import os

openai.api_key = "your-openai-api-key"

app = FastAPI()

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(file):
    with pdfplumber.open(file.file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

def evaluate_resume(resume_text, job_desc=None):
    prompt = f"""
You are an expert resume reviewer. Review the resume below and give a score (0-100), plus suggestions to improve.

Resume:
{resume_text}

"""
    if job_desc:
        prompt += f"\nMatch it with this job description:\n{job_desc}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response['choices'][0]['message']['content']

@app.post("/analyze_resume/")
async def analyze_resume(resume: UploadFile, job_desc: str = Form(None)):
    text = extract_text_from_pdf(resume)
    analysis = evaluate_resume(text, job_desc)
    return {"analysis": analysis}
