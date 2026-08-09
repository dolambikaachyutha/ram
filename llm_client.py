import os
import streamlit as st
from google import genai

def get_api_key():
    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", None)

client = None
api_key = get_api_key()
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception:
        client = None

MODEL = "gemini-2.5-flash"

def ask_ai(prompt):
    global client
    if not client:
        current_key = get_api_key()
        if current_key:
            try:
                client = genai.Client(api_key=current_key)
            except Exception:
                pass
                
    if not client:
        return "AI Assistant features require a valid GEMINI_API_KEY configured in Streamlit Secrets."

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            return response.text
        except Exception:
            return f"AI Service response unavailable: {e}"