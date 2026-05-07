import os
import streamlit as st
from gtts import gTTS
import io
from langchain_groq import ChatGroq

# --- 1. SECURE API KEY LOADING ---
# This checks Streamlit Secrets first (Cloud), then falls back to environment variables (Local)
api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("Missing GROQ_API_KEY! Please add it to your Streamlit Secrets.")
    st.stop()

# --- 2. LLM SETUP ---
llm = ChatGroq(
    model="llama-3.1-70b-versatile", # Groq supports Llama models natively
    temperature=0.6,
    api_key=api_key
)

# --- 3. HELPER FUNCTIONS ---
def detect_job_type(text):
    text = text.lower()
    if any(word in text for word in ["ai", "chatbot", "machine learning", "automation", "langchain"]):
        return "ai"
    elif any(word in text for word in ["website", "react", "frontend", "backend", "api"]):
        return "web"
    else:
        return "general"

def generate_prompt(job, job_type):
    if job_type == "ai":
        return f"Write a professional AI project proposal.\n\nJob:\n{job}\n\nInclude: Technical solution, timeline, and CTA."
    elif job_type == "web":
        return f"Write a web development proposal.\n\nJob:\n{job}\n\nInclude: Tech stack and delivery plan."
    else:
        return f"Write a freelance proposal under 200 words for:\n{job}"

# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="AI Proposal Agent", page_icon="🤖")
st.title("🤖 AI Proposal Generator")

job_description = st.text_area("Paste Job Description Here:", height=200)

if st.button("Generate Proposal"):
    if job_description:
        job_type = detect_job_type(job_description)
        st.info(f"Detected Category: {job_type.upper()}")
        
        with st.spinner("Generating..."):
            try:
                prompt = generate_prompt(job_description, job_type)
                response = llm.invoke(prompt).content
                
                st.success("Proposal Ready!")
                st.markdown("---")
                st.write(response)
                
                # --- 5. AUDIO OUTPUT (gTTS) ---
                tts = gTTS(text=response, lang='en')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp, format='audio/mp3')
                
                # --- 6. DOWNLOAD OPTION ---
                st.download_button(
                    label="Download Proposal",
                    data=response,
                    file_name="proposal.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"LLM Error: {e}")
    else:
        st.warning("Please paste a job description first.")
        
