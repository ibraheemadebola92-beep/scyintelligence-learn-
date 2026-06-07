import streamlit as st
import requests
import json
import time
import pypdf
import io

st.set_page_config(page_title="SCY AI Study System", page_icon="🎓", layout="centered")

st.markdown("""
<style>
html, body, [class*="css"] { font-family: sans-serif; }
.stApp { background: #0a0a0f; color: #e8e8f0; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.hero { text-align: center; padding: 30px 0 10px 0; }
.hero h1 { font-size: 2.2rem; color: #00ff88; margin-bottom: 4px; }
.hero p { color: #a0a0b0; }
.course-badge { display: inline-block; background: rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.3); color: #00ff88; border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; margin: 4px; }
.question-box { background: rgba(0,255,136,0.05); border-left: 3px solid #00ff88; border-radius: 8px; padding: 16px; margin: 12px 0; color: #e8e8f0; white-space: pre-wrap; }
.result-correct { background: rgba(0,255,136,0.1); border-left: 3px solid #00ff88; border-radius: 8px; padding: 12px; margin: 8px 0; color: #e8e8f0; }
.result-wrong { background: rgba(255,60,60,0.1); border-left: 3px solid #ff3c3c; border-radius: 8px; padding: 12px; margin: 8px 0; color: #e8e8f0; }
.score-box { background: #00ff88; color: #0a0a0f; border-radius: 16px; padding: 24px; text-align: center; font-size: 2rem; font-weight: 800; }
.timer-box { font-size: 1.8rem; font-weight: 800; color: #00ff88; text-align: center; padding: 10px; border: 2px solid #00ff88; border-radius: 12px; margin-bottom: 12px; }
.chat-user { background: rgba(0,255,136,0.08); border-radius: 12px 12px 2px 12px; padding: 12px 16px; margin: 8px 0; text-align: right; color: #e8e8f0; }
.chat-ai { background: rgba(255,255,255,0.05); border-radius: 12px 12px 12px 2px; padding: 12px 16px; margin: 8px 0; color: #e8e8f0; white-space: pre-wrap; }
.stButton > button { background: #00ff88; color: #0a0a0f; font-weight: 700; border: none; border-radius: 12px; padding: 12px 24px; font-size: 1rem; width: 100%; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

MODELS = [
    "sourceful/riverflow-v2.5-fast:free",
    "liquid/lfm-2.5-1.2b-thinking:free",
    "google/gemma-3-4b-it:free",
    "openai/gpt-oss-120b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "poolside/laguna-xs.2:free"
]

COURSES = {
    "MTH 102 — Mathematics": ["Functions, graphs, limits, and continuity","Derivatives and differentiation techniques","Maxima and minima","Curve sketching","Integration and definite integrals","Reduction formulae","Areas and volumes (Trapezium and Simpson's rules)"],
    "CHM 102 — Organic Chemistry": ["History of organic chemistry","Fullerenes and nanochemistry","Electronic theory in organic chemistry","Isolation and purification of organic compounds","Nomenclature and functional groups","Reaction mechanisms and kinetics","Stereochemistry","Alkanes, alkenes, alkynes","Alcohols, ethers, amines, alkyl halides","Aldehydes, ketones, carboxylic acids","Chemistry of metals, non-metals, and transition metals"],
    "PHY 102 — Electricity & Magnetism": ["Forces in nature","Electrostatics and Coulomb's law","Electric field and potential","Gauss's law and capacitance","Conductors and insulators","DC circuit analysis and Ohm's law","Magnetic fields and Lorentz force","Biot-Savart and Ampere's laws","Electromagnetic induction","Faraday and Lenz's laws","Transformers and inductance","Maxwell's equations","AC circuits"],
    "PHY 104 — Waves & Optics": ["Simple harmonic motion (SHM)","Damped SHM, Q values, resonance","Forced SHM and transients","Coupled SHM and normal modes","Types and properties of waves","Superposition, interference, diffraction","Dispersion and polarisation","Echo, beats, and Doppler effect","Sound propagation","Nature and propagation of light","Reflection and refraction","Internal reflection and dispersion","Thin lenses and optical instruments","Huygens's principle"],
    "STA 112 — Statistics & Probability": ["Permutation and combination","Concepts and principles of probability","Random variables","Probability and distribution functions","Binomial distribution","Geometric distribution","Poisson distribution","Normal distribution","Sampling distributions","Exploratory data analysis"]
}

def call_ai(messages, system_prompt, max_tokens=1500):
    api_key = st.secrets["OPENROUTER_API_KEY"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://scyintelligenceaitutor.streamlit.app",
        "X-Title": "SCY AI Study System"
    }
    for model in MODELS:
        try:
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": system_prompt}] + messages,
                "max_tokens": max_tokens
            }
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=45)
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
        return text[:6000]
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page):
    st.session_state.page = page
    st.rerun()

# ══════════════════════════════════════
# HOME
# ══════════════════════════════════════
if st.session_state.page == "home":
    st.markdown("""
    <div class="hero">
        <div style="font-size:3rem;">🎓</div>
        <h1>SCY AI Study System</h1>
        <p>100L Engineering — Rain Semester</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**📚 Courses:** MTH 102 | CHM 102 | PHY 102 | PHY 104 | STA 112")
    st.markdown("---")
    st.markdown("### 🚀 Choose Your Mode")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📚 Study Mode"):
            go("study")
        if st.button("🖥️ CBT Mode"):
            go("cbt")
    with col2:
        if st.button("✍️ Practice Mode"):
            go("practice")
        if st.button("📄 PDF Chat"):
            go("pdf")

    st.markdown('<br><p style="text-align:center;color:#555;font-size:0.8rem;">Powered by SCY Intelligence</p>', unsafe_allow_html=True)

# ══════════════════════════════════════
# STUDY MODE
# ══════════════════════════════════════
elif st.session_state.page == "study":
    if st.button("← Home"):
        go("home")
    st.markdown("# 📚 Study Mode")
    st.markdown("---")
    course = st.selectbox("Select Course", list(COURSES.keys()))
    topic = st.selectbox("Select Topic", COURSES[course])
    custom = st.text_input("Or type a specific question (optional)")
    if "study_chat" not in st.session_state:
        st.session_state.study_chat = []
    if st.button("Teach Me 🚀"):
        question = custom if custom else f"Teach me about: {topic}"
        system = f"You are a university tutor for 100L Engineering students in Nigeria. Course: {course}. Topic: {topic}. Teach with: simple explanation, detailed breakdown, 2 examples, exam tips. Use plain text for math (e.g. write 'x squared' not 'x^2' where possible, or use simple notation like x^2)."
        with st.spinner("Thinking..."):
            response = call_ai(st.session_state.study_chat + [{"role": "user", "content": question}], system, max_tokens=1200)
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
                system = f"You are a tutor for {course}. Continue explaining {topic} clearly."
                with st.spinner("Thinking..."):
                    response = call_ai(st.session_state.study_chat[-4:] + [{"role": "user", "content": followup}], system, max_tokens=1000)
                st.session_state.study_chat.append({"role": "user", "content": followup})
                st.session_state.study_chat.append({"role": "assistant", "content": response})
                st.rerun()
        if st.button("Clear Chat 🗑️"):
            st.session_state.study_chat = []
            st.rerun()

# ══════════════════════════════════════
# PRACTICE MODE
# ══════════════════════════════════════
elif st.session_state.page == "practice":
    if st.button("← Home"):
        go("home")
    st.markdown("# ✍️ Practice Mode")
    st.markdown("---")
    course = st.selectbox("Select Course", list(COURSES.keys()))
    topic = st.selectbox("Select Topic", COURSES[course])
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    if "practice_questions" not in st.session_state:
        st.session_state.practice_questions = ""
    if "practice_answers" not in st.session_state:
        st.session_state.practice_answers = {}
    if st.button("Generate Questions 📝"):
        system = f"You are an exam setter for {course} (100L Engineering, Nigeria). Generate exactly 5 {difficulty} questions on: {topic}. Number them Q1 to Q5. Questions only, no answers."
        with st.spinner("Generating..."):
            st.session_state.practice_questions = call_ai(
                [{"role": "user", "content": f"Generate 5 {difficulty} questions on {topic}"}],
                system, max_tokens=800
            )
        st.session_state.practice_answers = {}
    if st.session_state.practice_questions:
        st.markdown("---")
        st.markdown(f'<div class="question-box">{st.session_state.practice_questions}</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### ✍️ Your Answers")
        for i in range(1, 6):
            st.session_state.practice_answers[f"q{i}"] = st.text_area(
                f"Answer to Q{i}",
                value=st.session_state.practice_answers.get(f"q{i}", ""),
                key=f"ans_{i}"
            )
        if st.button("Check My Answers ✅"):
            answers_text = "\n".join([f"Q{i}: {st.session_state.practice_answers.get(f'q{i}', 'No answer')}" for i in range(1, 6)])
            system = f"You are an examiner for {course}. Questions: {st.session_state.practice_questions}\nStudent answers: {answers_text}\nMark each, give correct answer and brief explanation."
            with st.spinner("Marking..."):
                feedback = call_ai([{"role": "user", "content": "Mark my answers"}], system, max_tokens=1200)
            st.markdown("### 📊 Feedback")
            st.markdown(f'<div class="chat-ai">🤖 {feedback}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════
# CBT MODE
# ══════════════════════════════════════
elif st.session_state.page == "cbt":
    for key, default in [("cbt_state","setup"),("cbt_questions",[]),("cbt_answers",{}),("cbt_start_time",None),("cbt_current_q",0)]:
        if key not in st.session_state:
            st.session_state[key] = default

    if st.session_state.cbt_state == "setup":
        if st.button("← Home"):
            go("home")
        st.markdown("# 🖥️ CBT Mode")
        st.markdown("---")
        course = st.selectbox("Select Course", list(COURSES.keys()))
        topic = st.selectbox("Select Topic", ["All Topics"] + COURSES[course])
        num_q = st.selectbox("Number of Questions", [5, 10, 20, 30])
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"])
        duration = st.selectbox("Time Allowed", ["5 minutes", "10 minutes", "15 minutes", "30 minutes", "45 minutes", "60 minutes"])
        if st.button("Start CBT 🚀"):
            topic_str = topic if topic != "All Topics" else f"all topics in {course}"
            system = f"""Generate exactly {num_q} CBT questions on {topic_str} for {course}. Difficulty: {difficulty}.
Mix MCQ (A,B,C,D) and short written questions.
Return ONLY valid JSON array, no markdown:
[
  {{"type":"mcq","question":"...","options":{{"A":"...","B":"...","C":"...","D":"..."}},"answer":"A","explanation":"..."}},
  {{"type":"written","question":"...","answer":"...","explanation":"..."}}
]"""
            with st.spinner(f"Generating {num_q} questions..."):
                raw = call_ai(
                    [{"role": "user", "content": f"Generate {num_q} questions"}],
                    system, max_tokens=3000
                )
            try:
                clean = raw.strip().replace("```json","").replace("```","").strip()
                questions = json.loads(clean)
                st.session_state.cbt_questions = questions
                st.session_state.cbt_answers = {}
                st.session_state.cbt_current_q = 0
                st.session_state.cbt_course = course
                st.session_state.cbt_duration = int(duration.split()[0]) * 60
                st.session_state.cbt_start_time = time.time()
                st.session_state.cbt_state = "testing"
                st.rerun()
            except Exception as e:
                st.error(f"Failed to load questions. Try again. ({e})")
                st.code(raw[:500])

    elif st.session_state.cbt_state == "testing":
        questions = st.session_state.cbt_questions
        total = len(questions)
        current = st.session_state.cbt_current_q
        elapsed = time.time() - st.session_state.cbt_start_time
        remaining = max(0, st.session_state.cbt_duration - elapsed)
        if remaining <= 0:
            st.session_state.cbt_state = "results"
            st.rerun()
        mins, secs = int(remaining // 60), int(remaining % 60)
        st.markdown(f'<div class="timer-box">⏱ {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
        st.progress(current / total)
        st.markdown(f"**Question {current + 1} of {total}**")
        q = questions[current]
        st.markdown(f'<div class="question-box"><b>Q{current+1}. {q["question"]}</b></div>', unsafe_allow_html=True)
        if q["type"] == "mcq":
            options = q.get("options", {})
            opts = ["-- Select an answer --"] + list(options.keys())
            choice = st.radio("", opts, format_func=lambda x: x if x == "-- Select an answer --" else f"{x}. {options[x]}", key=f"mcq_{current}")
            if choice != "-- Select an answer --":
                st.session_state.cbt_answers[current] = choice
        else:
            ans = st.text_area("Your answer:", key=f"written_{current}")
            st.session_state.cbt_answers[current] = ans
        col1, col2, col3 = st.columns(3)
        with col1:
            if current > 0 and st.button("⬅ Prev"):
                st.session_state.cbt_current_q -= 1
                st.rerun()
        with col2:
            if current < total - 1 and st.button("Next ➡"):
                st.session_state.cbt_current_q += 1
                st.rerun()
        with col3:
            if st.button("Submit 🏁"):
                st.session_state.cbt_state = "results"
                st.rerun()

    elif st.session_state.cbt_state == "results":
        questions = st.session_state.cbt_questions
        answers = st.session_state.cbt_answers
        total = len(questions)
        score = 0
        written_qs = []
        for i, q in enumerate(questions):
            if q["type"] == "mcq":
                if answers.get(i,"").strip().upper() == q["answer"].strip().upper():
                    score += 1
            else:
                written_qs.append({"index":i,"question":q["question"],"student_answer":answers.get(i,""),"correct_answer":q["answer"]})
        written_score = 0
        written_feedback = {}
        if written_qs:
            wtext = "\n".join([f"Q:{w['question']}\nStudent:{w['student_answer']}\nCorrect:{w['correct_answer']}" for w in written_qs])
            sys = 'Mark answers. Return ONLY JSON: [{"index":0,"score":1,"feedback":"..."}]'
            with st.spinner("Marking written answers..."):
                raw = call_ai([{"role":"user","content":wtext}], sys, max_tokens=800)
            try:
                clean = raw.strip().replace("```json","").replace("```","").strip()
                for r in json.loads(clean):
                    written_score += r.get("score",0)
                    written_feedback[r["index"]] = r.get("feedback","")
            except:
                pass
        total_score = score + written_score
        pct = round((total_score / total) * 100)
        st.markdown(f'<div class="score-box">🎓 {total_score} / {total} ({pct}%)</div>', unsafe_allow_html=True)
        st.markdown("")
        if pct >= 70: st.success("🌟 Excellent!")
        elif pct >= 50: st.warning("📖 Good effort! Review missed topics.")
        else: st.error("💪 Keep studying!")
        st.markdown("---")
        st.markdown("### 📋 Review")
        for i, q in enumerate(questions):
            sa = answers.get(i,"No answer")
            ca = q["answer"]
            if q["type"] == "mcq":
                ok = sa.strip().upper() == ca.strip().upper()
                opts = " | ".join([f"{k}.{v}" for k,v in q.get("options",{}).items()])
                icon = "✅" if ok else "❌"
                css = "result-correct" if ok else "result-wrong"
                st.markdown(f'<div class="{css}"><b>{icon} Q{i+1}. {q["question"]}</b><br><small>{opts}</small><br>You: <b>{sa}</b> | Correct: <b>{ca}</b><br><em>{q.get("explanation","")}</em></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="result-correct"><b>📝 Q{i+1}. {q["question"]}</b><br>You: {sa}<br>Correct: <b>{ca}</b><br><em>{written_feedback.get(i,"")}</em></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 New Test"):
                st.session_state.cbt_state = "setup"
                st.session_state.cbt_questions = []
                st.session_state.cbt_answers = {}
                st.rerun()
        with col2:
            if st.button("🏠 Home"):
                go("home")

# ══════════════════════════════════════
# PDF CHAT
# ══════════════════════════════════════
elif st.session_state.page == "pdf":
    if st.button("← Home"):
        go("home")
    st.markdown("# 📄 PDF Chat")
    st.markdown("---")
    if "pdf_chat" not in st.session_state:
        st.session_state.pdf_chat = []
    if "pdf_text" not in st.session_state:
        st.session_state.pdf_text = ""
    uploaded = st.file_uploader("Upload your PDF", type=["pdf"])
    if uploaded:
        if st.session_state.pdf_text == "":
            with st.spinner("Reading PDF..."):
                st.session_state.pdf_text = extract_pdf_text(uploaded)
            st.success("✅ PDF loaded!")
        question = st.text_input("Ask a question about your PDF...")
        if st.button("Ask 💬"):
            if question:
                system = f"Answer ONLY from this document. If not found, say so.\n\n{st.session_state.pdf_text}"
                with st.spinner("Answering..."):
                    response = call_ai(
                        st.session_state.pdf_chat[-4:] + [{"role":"user","content":question}],
                        system, max_tokens=1000
                    )
                st.session_state.pdf_chat.append({"role":"user","content":question})
                st.session_state.pdf_chat.append({"role":"assistant","content":response})
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
        st.info("👆 Upload a PDF to get started.")
