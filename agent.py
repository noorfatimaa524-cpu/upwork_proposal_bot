import streamlit as st
import os
import io
import pandas as pd
from gtts import gTTS
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# --- INITIAL SETUP ---
load_dotenv()
st.set_page_config(page_title="AI Proposal Agent", layout="wide")

# Initialize Session State for multi-page navigation
if "step" not in st.session_state:
    st.session_state.step = 1
if "job_description" not in st.session_state:
    st.session_state.job_description = ""
if "proposal_result" not in st.session_state:
    st.session_state.proposal_result = ""

# --- AUDIO HELPER ---
def speak_web(text):
    tts = gTTS(text=text, lang='en')
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    return audio_fp

# --- CORE LOGIC (From agent.py) ---
def detect_job_type(text):
    text = text.lower()
    if any(word in text for word in ["ai", "chatbot", "machine learning", "automation", "langchain"]):
        return "ai"
    elif any(word in text for word in ["website", "react", "frontend", "backend", "api"]):
        return "web"
    return "general"

def generate_prompt(job, job_type):
    templates = {
        "ai": f"Write a professional AI project proposal.\n\nJob:\n{job}\n\nInclude: Technical solution, Timeline, CTA.",
        "web": f"Write a web development proposal.\n\nJob:\n{job}\n\nInclude: Tech stack, Delivery plan, CTA.",
        "general": f"Write a freelance proposal.\n\nJob:\n{job}\n\nKeep under 200 words with a strong hook."
    }
    return templates.get(job_type)

# --- PAGE NAVIGATION ---
def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

# --- MULTI-PAGE FLOW ---

# SIDEBAR: Progress & Key
with st.sidebar:
    st.title("🚀 Navigation")
    st.write(f"**Current Step:** {st.session_state.step} of 3")
    api_key = st.text_input("Enter Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    if st.button("Reset App"):
        st.session_state.step = 1
        st.session_state.proposal_result = ""
        st.rerun()

# --- STEP 1: JOB DESCRIPTION ---
if st.session_state.step == 1:
    st.header("Step 1: Paste Job Description")
    st.info("The AI Agent will analyze the text to detect the job category.")
    
    job_input = st.text_area("Paste the client's requirements here:", height=300)
    
    if st.button("Analyze & Continue"):
        if job_input:
            st.session_state.job_description = job_input
            next_step()
            st.rerun()
        else:
            st.warning("Please paste a description first.")

# --- STEP 2: REVIEW & GENERATE ---
elif st.session_state.step == 2:
    st.header("Step 2: AI Classification")
    
    job_type = detect_job_type(st.session_state.job_description)
    st.subheader(f"Detected Category: :blue[{job_type.upper()}]")
    
    st.write("Does this look correct? Click below to generate your professional proposal.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            prev_step()
            st.rerun()
    with col2:
        if st.button("✨ Generate Proposal"):
            if not api_key:
                st.error("Missing API Key!")
            else:
                with st.spinner("AI is writing your proposal..."):
                    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)
                    prompt = generate_prompt(st.session_state.job_description, job_type)
                    st.session_state.proposal_result = llm.invoke(prompt).content
                    next_step()
                    st.rerun()

# --- STEP 3: FINAL PROPOSAL & EXPORT ---
elif st.session_state.step == 3:
    st.header("Step 3: Your Professional Proposal")
    
    # Audio Review
    st.audio(speak_web("Your proposal is ready for review."), format="audio/mp3")
    
    st.markdown("---")
    st.markdown(st.session_state.proposal_result)
    st.markdown("---")
    
    # Export options (Replaces save_proposal csv logic)
    st.subheader("💾 Export Options")
    
    # Text Download
    st.download_button(
        label="Download as TXT",
        data=st.session_state.proposal_result,
        file_name="proposal.txt",
        mime="text/plain"
    )
    
    # CSV Download (Matches your original agent.py logic)
    df = pd.DataFrame([{"Proposal": st.session_state.proposal_result}])
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="proposal.csv",
        mime="text/csv"
    )

    if st.button("Start New Proposal"):
        st.session_state.step = 1
        st.session_state.proposal_result = ""
        st.rerun()
        st.warning("Please paste a job description first.")
        
