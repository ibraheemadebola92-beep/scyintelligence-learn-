import streamlit as st
import requests
import pypdf
import io

st.set_page_config(page_title="PDF Chat", page_icon="📄", layout="centered")

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
    return "⚠️ All models are busy. Please try again."

def extract_pdf_text(uploaded_file):
    try:
        reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text[:8000]
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# Home button removed


st.markdown("# 📄 PDF Chat")
st.markdown("*Upload your notes or textbook and ask the AI anything about it*")
st.markdown("---")

if "pdf_chat" not in st.session_state:
    st.session_state.pdf_chat = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

uploaded = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded:
    if st.session_state.pdf_text == "":
        with st.spinner("Reading your PDF..."):
            st.session_state.pdf_text = extract_pdf_text(uploaded)
        st.success("✅ PDF loaded! Ask me anything about it.")
    question = st.text_input("Ask a question about your PDF...")
    if st.button("Ask 💬"):
        if question:
            system = f"You are a study assistant. Answer questions ONLY based on this document:\n\n{st.session_state.pdf_text}\n\nIf the answer is not in the document, say so clearly."
            with st.spinner("Answering..."):
                response = call_ai(st.session_state.pdf_chat + [{"role": "user", "content": question}], system)
            st.session_state.pdf_chat.append({"role": "user", "content": question})
            st.session_state.pdf_chat.append({"role": "assistant", "content": response})
            st.rerun()
    for msg in st.session_state.pdf_chat:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">🧑‍🎓 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
    if st.session_state.pdf_chat:
        if st.button("Clear Chat 🗑️"):
            st.session_state.pdf_chat = []
            st.session_state.pdf_text = ""
            st.rerun()
else:
    st.info("👆 Upload a PDF above to get started.")
