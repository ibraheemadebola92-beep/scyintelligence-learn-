import streamlit as st
import requests
import random

st.set_page_config(page_title="Study Mode", page_icon="📚", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0f0a 100%); color: #e8e8f0; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
div[data-testid="stSidebar"] { background: #07070f; border-right: 1px solid rgba(255,255,255,0.06); }
.chat-user { background: rgba(0,255,136,0.08); border-radius: 12px 12px 2px 12px; padding: 12px 16px; margin: 8px 0; text-align: right; color: #e8e8f0; }
.chat-ai { background: rgba(255,255,255,0.05); border-radius: 12px 12px 12px 2px; padding: 12px 16px; margin: 8px 0; color: #e8e8f0; }
.stButton > button { background: linear-gradient(135deg, #00ff88, #00cc6a); color: #0a0a0f; font-family: 'Syne', sans-serif; font-weight: 700; border: none; border-radius: 14px; padding: 14px 28px; font-size: 1rem; width: 100%; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

MODELS = [
    "google/gemma-3-4b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "openai/gpt-oss-120b:free"
]

COURSES = {
    "MTH 102 — Mathematics": ["Functions, graphs, limits, and continuity","Derivatives and differentiation techniques","Maxima and minima","Curve sketching","Integration and definite integrals","Reduction formulae","Areas and volumes (Trapezium and Simpson's rules)"],
    "CHM 102 — Organic Chemistry": ["History of organic chemistry","Fullerenes and nanochemistry","Electronic theory in organic chemistry","Isolation and purification of organic compounds","Nomenclature and functional groups","Reaction mechanisms and kinetics","Stereochemistry","Alkanes, alkenes, alkynes","Alcohols, ethers, amines, alkyl halides","Aldehydes, ketones, carboxylic acids","Chemistry of metals, non-metals, and transition metals"],
    "PHY 102 — Electricity & Magnetism": ["Forces in nature","Electrostatics and Coulomb's law","Electric field and potential","Gauss's law and capacitance","Conductors and insulators","DC circuit analysis and Ohm's law","Magnetic fields and Lorentz force","Biot-Savart and Ampere's laws","Electromagnetic induction","Faraday and Lenz's laws","Transformers and inductance","Maxwell's equations","AC circuits"],
    "PHY 104 — Waves & Optics": ["Simple harmonic motion (SHM)","Damped SHM, Q values, resonance","Forced SHM and transients","Coupled SHM and normal modes","Types and properties of waves","Superposition, interference, diffraction","Dispersion and polarisation","Echo, beats, and Doppler effect","Sound propagation","Nature and propagation of light","Reflection and refraction","Internal reflection and dispersion","Thin lenses and optical instruments","Huygens's principle"],
    "STA 112 — Statistics & Probability": ["Permutation and combination","Concepts and principles of probability","Random variables","Probability and distribution functions","Binomial distribution","Geometric distribution","Poisson distribution","Normal distribution","Sampling distributions","Exploratory data analysis"]
}

def call_ai(messages, system_prompt):
    api_key = st.secrets["OPENROUTER_API_KEY"]
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "HTTP-Referer": "https://scyintelligenceaitutor.streamlit.app", "X-Title": "SCY AI Study System"}
    for model in MODELS:
        try:
            payload = {"model": model, "messages": [{"role": "system", "content": system_prompt}] + messages, "max_tokens": 2000}
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
            data = r.json()
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"]
        except:
            continue
    return "⚠️ All models are busy. Please try again in a moment."

if st.button("← Back to Home"):
    st.switch_page("app.py")

st.markdown("# 📚 Study Mode")
st.markdown("*Your AI tutor — ask anything about your courses*")
st.markdown("---")

course = st.selectbox("Select Course", list(COURSES.keys()))
topic = st.selectbox("Select Topic", COURSES[course])
custom = st.text_input("Or type a specific question (optional)")

if "study_chat" not in st.session_state:
    st.session_state.study_chat = []

if st.button("Teach Me 🚀"):
    question = custom if custom else f"Teach me about: {topic}"
    system = f"You are an expert university tutor for 100-Level Engineering students in Nigeria. Course: {course}. Topic: {topic}. Teach clearly with: 1. Simple explanation 2. Detailed breakdown 3. 2 worked examples 4. Exam tips. Stay strictly within the course content."
    with st.spinner("Thinking..."):
        response = call_ai(st.session_state.study_chat + [{"role": "user", "content": question}], system)
    st.session_state.study_chat.append({"role": "user", "content": question})
    st.session_state.study_chat.append({"role": "assistant", "content": response})

if st.session_state.get("study_chat"):
    st.markdown("---")
    for msg in st.session_state.study_chat:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">🧑‍🎓 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    followup = st.text_input("Ask a follow-up question...", key="study_followup")
    if st.button("Send 💬"):
        if followup:
            system = f"You are an expert tutor for {course}. Continue helping the student understand {topic}."
            with st.spinner("Thinking..."):
                response = call_ai(st.session_state.study_chat + [{"role": "user", "content": followup}], system)
            st.session_state.study_chat.append({"role": "user", "content": followup})
            st.session_state.study_chat.append({"role": "assistant", "content": response})
            st.rerun()
    if st.button("Clear Chat 🗑️"):
        st.session_state.study_chat = []
        st.rerun()
