import os
from dotenv import load_dotenv
import pyttsx3
from langchain_groq import ChatGroq

# LOAD ENV
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY missing")

# TTS
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    print("\nAI:\n", text)
    engine.say(text)
    engine.runAndWait()

# LLM
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.6,
    api_key=api_key
)

# JOB TYPE DETECTOR
def detect_job_type(text):
    text = text.lower()

    if any(word in text for word in ["ai", "chatbot", "machine learning", "automation", "langchain"]):
        return "ai"

    elif any(word in text for word in ["website", "react", "frontend", "backend", "api"]):
        return "web"

    else:
        return "general"

# PROMPT GENERATORS
def generate_prompt(job, job_type):
    
    if job_type == "ai":
        return f"""
Write a professional AI project proposal.

Job:
{job}

Include:
- Understanding of AI problem
- Technical solution (models, APIs, tools)
- Timeline
- Strong CTA

Tone: Expert, confident
"""

    elif job_type == "web":
        return f"""
Write a web development proposal.

Job:
{job}

Include:
- Understanding of website/app needs
- Tech stack (React, Node, etc.)
- Clean delivery plan
- CTA
Tone: Professional and clear
"""

    else:
        return f"""
Write a freelance proposal.

Job:
{job}

- Start with strong hook
- Show understanding
- Offer solution
- Keep under 200 words
- Add CTA
"""

# SAVE FILE
def save_proposal(text):
    with open("proposal.csv", "w", encoding="utf-8") as f:
        f.write(text)
    print("Saved to proposal.csv")

# MAIN LOOP
speak("Welcome to the AI proposal Agent!")
print("AI Proposal Agent Started")
print("Paste job description or type 'exit'\n")

while True:
    job = input("Job Description:\n")
    if job.lower() == "exit":
        speak("Goodbye! Agent shutting down.")
        break

    job_type = detect_job_type(job)
    print(f"Detected: {job_type.upper()} job")
    prompt = generate_prompt(job, job_type)
    try:
        response = llm.invoke(prompt).content
        print(response)
        save_proposal(response)
    except Exception as e:
        print("Error:", e)
        
        
        
        
