import streamlit as st
import requests
import json
import time
import pypdf
import io

st.set_page_config(page_title="SCY AI Study System", page_icon="🎓", layout="centered")

# Load MathJax for rendering equations
st.markdown("""
<script>
window.MathJax = {
  tex: { inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']] },
  svg: { fontCache: 'global' }
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
""", unsafe_allow_html=True)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0f0a 100%); color: #e8e8f0; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.hero { text-align: center; padding: 30px 0 10px 0; }
.hero h1 { font-size: 2.4rem; background: linear-gradient(135deg, #00ff88, #00cc6a); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero p { color: #a0a0b0; }
.course-badge { display: inline-block; background: rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.3); color: #00ff88; border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; margin: 4px; }
.question-box { background: rgba(0,255,136,0.05); border-left: 3px solid #00ff88; border-radius: 8px; padding: 16px; margin: 12px 0; color: #e8e8f0; }
.result-correct { background: rgba(0,255,136,0.1); border-left: 3px solid #00ff88; border-radius: 8px; padding: 12px; margin: 8px 0; color: #e8e8f0; }
.result-wrong { background: rgba(255,60,60,0.1); border-left: 3px solid #ff3c3c; border-radius: 8px; padding: 12px; margin: 8px 0; color: #e8e8f0; }
.score-box { background: linear-gradient(135deg, #00ff88, #00cc6a); color: #0a0a0f; border-radius: 16px; padding: 24px; text-align: center; font-size: 2rem; font-weight: 800; font-family: 'Syne', sans-serif; }
.timer-display { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: #00ff88; text-align: center; padding: 12px; border: 2px solid #00ff88; border-radius: 12px; margin-bottom: 16px; }
.timer-danger { color: #ff3c3c !important; border-color: #ff3c3c !important; }
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

# ── SESSION STATE ──
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

    st.markdown("### 📚 Available Courses")
    courses = ["MTH 102", "CHM 102", "PHY 102", "PHY 104", "STA 112"]
    cols = st.columns(len(courses))
    for i, c in enumerate(courses):
        with cols[i]:
            st.markdown(f'<div class="course-badge">{c}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
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

    st.markdown('<br><p style="text-align:center;color:#555;font-size:0.85rem;">Powered by SCY Intelligence • AI Study System</p>', unsafe_allow_html=True)

# ══════════════════════════════════════
# STUDY MODE
# ══════════════════════════════════════
elif st.session_state.page == "study":
    if st.button("← Home"):
        go("home")
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
        system = f"You are an expert university tutor for 100-Level Engineering students in Nigeria. Always write mathematical equations using $ for inline math (e.g. $x^2$) and $$ for display math (e.g. $$\frac{dy}{dx}$$). Never use raw LaTeX without delimiters. Course: {course}. Topic: {topic}. Teach clearly with: 1. Simple explanation 2. Detailed breakdown 3. 2 worked examples 4. Exam tips."
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

# ══════════════════════════════════════
# PRACTICE MODE
# ══════════════════════════════════════
elif st.session_state.page == "practice":
    if st.button("← Home"):
        go("home")
    st.markdown("# ✍️ Practice Mode")
    st.markdown("*Generate questions and get your answers marked*")
    st.markdown("---")
    course = st.selectbox("Select Course", list(COURSES.keys()))
    topic = st.selectbox("Select Topic", COURSES[course])
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    if "practice_questions" not in st.session_state:
        st.session_state.practice_questions = ""
    if "practice_answers" not in st.session_state:
        st.session_state.practice_answers = {}
    if st.button("Generate Questions 📝"):
        system = f"You are an exam question setter for {course} (100-Level Engineering, Nigeria). Generate exactly 5 practice questions on: {topic}. Difficulty: {difficulty}. Format as Q1. Q2. Q3. Q4. Q5. Questions only, no answers."
        with st.spinner("Generating questions..."):
            st.session_state.practice_questions = call_ai([{"role": "user", "content": f"Generate {difficulty} questions on {topic}"}], system)
        st.session_state.practice_answers = {}
    if st.session_state.practice_questions:
        st.markdown("---")
        st.markdown(f'<div class="question-box">{st.session_state.practice_questions}</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### ✍️ Your Answers")
        for i in range(1, 6):
            st.session_state.practice_answers[f"q{i}"] = st.text_area(f"Answer to Q{i}", value=st.session_state.practice_answers.get(f"q{i}", ""), key=f"ans_{i}")
        if st.button("Check My Answers ✅"):
            answers_text = "\n".join([f"Q{i}: {st.session_state.practice_answers.get(f'q{i}', 'No answer')}" for i in range(1, 6)])
            system = f"You are a university examiner for {course}. Questions: {st.session_state.practice_questions}. Student answers: {answers_text}. Mark each answer, give correct answer and explanation."
            with st.spinner("Marking your answers..."):
                feedback = call_ai([{"role": "user", "content": "Mark my answers"}], system)
            st.markdown("### 📊 Feedback")
            st.markdown(f'<div class="chat-ai">🤖 {feedback}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════
# CBT MODE
# ══════════════════════════════════════
elif st.session_state.page == "cbt":
    if "cbt_state" not in st.session_state:
        st.session_state.cbt_state = "setup"
    if "cbt_questions" not in st.session_state:
        st.session_state.cbt_questions = []
    if "cbt_answers" not in st.session_state:
        st.session_state.cbt_answers = {}
    if "cbt_start_time" not in st.session_state:
        st.session_state.cbt_start_time = None
    if "cbt_current_q" not in st.session_state:
        st.session_state.cbt_current_q = 0

    if st.session_state.cbt_state == "setup":
        if st.button("← Home"):
            go("home")
        st.markdown("# 🖥️ CBT Mode")
        st.markdown("*Timed computer-based test — exam simulation*")
        st.markdown("---")
        course = st.selectbox("Select Course", list(COURSES.keys()))
        topic = st.selectbox("Select Topic", ["All Topics"] + COURSES[course])
        num_q = st.selectbox("Number of Questions", [10, 20, 30, 40])
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"])
        duration = st.selectbox("Time Allowed", ["15 minutes", "30 minutes", "45 minutes", "60 minutes"])
        if st.button("Start CBT 🚀"):
            topic_str = topic if topic != "All Topics" else f"all topics in {course}"
            system = f"""You are a CBT question generator for {course} (100-Level Engineering, Nigeria).
Generate exactly {num_q} questions on {topic_str}. Difficulty: {difficulty}.
Mix multiple choice (A,B,C,D) and short written answer questions.
Return ONLY a valid JSON array:
[
  {{"type": "mcq", "question": "question text", "options": {{"A": "opt1", "B": "opt2", "C": "opt3", "D": "opt4"}}, "answer": "A", "explanation": "why"}},
  {{"type": "written", "question": "question text", "answer": "correct answer", "explanation": "explanation"}}
]
No markdown, no preamble. Only the JSON array."""
            with st.spinner(f"Generating {num_q} questions..."):
                raw = call_ai([{"role": "user", "content": f"Generate {num_q} CBT questions"}], system)
            try:
                clean = raw.strip().replace("```json", "").replace("```", "").strip()
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
                st.error(f"Failed to parse questions. Try again. Error: {e}")
                st.code(raw)

    elif st.session_state.cbt_state == "testing":
        questions = st.session_state.cbt_questions
        total = len(questions)
        current = st.session_state.cbt_current_q
        elapsed = time.time() - st.session_state.cbt_start_time
        remaining = st.session_state.cbt_duration - elapsed
        if remaining <= 0:
            st.session_state.cbt_state = "results"
            st.rerun()
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        timer_class = "timer-display timer-danger" if remaining < 120 else "timer-display"
        st.markdown(f'<div class="{timer_class}">⏱ {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
        st.progress(current / total)
        st.markdown(f"**Question {current + 1} of {total}**")
        q = questions[current]
        st.markdown(f'<div class="question-box"><strong>Q{current+1}. {q["question"]}</strong></div>', unsafe_allow_html=True)
        if q["type"] == "mcq":
            options = q.get("options", {})
            choice = st.radio("Select your answer:", list(options.keys()), format_func=lambda x: f"{x}. {options[x]}", key=f"cbt_mcq_{current}")
            st.session_state.cbt_answers[current] = choice
        else:
            answer = st.text_area("Your answer:", key=f"cbt_written_{current}")
            st.session_state.cbt_answers[current] = answer
        col1, col2, col3 = st.columns(3)
        with col1:
            if current > 0:
                if st.button("⬅ Prev"):
                    st.session_state.cbt_current_q -= 1
                    st.rerun()
        with col2:
            if current < total - 1:
                if st.button("Next ➡"):
                    st.session_state.cbt_current_q += 1
                    st.rerun()
        with col3:
            if st.button("Submit 🏁"):
                st.session_state.cbt_state = "results"
                st.rerun()
        time.sleep(1)
        st.rerun()

    elif st.session_state.cbt_state == "results":
        st.markdown("## 🏁 Test Complete!")
        questions = st.session_state.cbt_questions
        answers = st.session_state.cbt_answers
        total = len(questions)
        score = 0
        written_qs = []
        for i, q in enumerate(questions):
            if q["type"] == "mcq":
                if answers.get(i, "").strip().upper() == q["answer"].strip().upper():
                    score += 1
            else:
                written_qs.append({"index": i, "question": q["question"], "student_answer": answers.get(i, ""), "correct_answer": q["answer"]})
        written_score = 0
        written_feedback = {}
        if written_qs:
            written_text = "\n".join([f"Q: {w['question']}\nStudent: {w['student_answer']}\nCorrect: {w['correct_answer']}" for w in written_qs])
            system = 'Mark written answers. For each give score 0 or 1 and brief feedback. Return ONLY JSON: [{"index": 0, "score": 1, "feedback": "..."}]'
            with st.spinner("Marking written answers..."):
                raw = call_ai([{"role": "user", "content": written_text}], system)
            try:
                clean = raw.strip().replace("```json", "").replace("```", "").strip()
                w_results = json.loads(clean)
                for r in w_results:
                    written_score += r.get("score", 0)
                    written_feedback[r["index"]] = r.get("feedback", "")
            except:
                pass
        total_score = score + written_score
        percentage = round((total_score / total) * 100)
        st.markdown(f'<div class="score-box">🎓 {total_score} / {total} ({percentage}%)</div>', unsafe_allow_html=True)
        st.markdown("")
        if percentage >= 70:
            st.success("🌟 Excellent performance!")
        elif percentage >= 50:
            st.warning("📖 Good effort! Review the topics you missed.")
        else:
            st.error("💪 Keep studying!")
        st.markdown("---")
        st.markdown("### 📋 Question Review")
        for i, q in enumerate(questions):
            student_ans = answers.get(i, "No answer")
            correct_ans = q["answer"]
            if q["type"] == "mcq":
                is_correct = student_ans.strip().upper() == correct_ans.strip().upper()
                css_class = "result-correct" if is_correct else "result-wrong"
                icon = "✅" if is_correct else "❌"
                options = q.get("options", {})
                opt_text = " | ".join([f"{k}. {v}" for k, v in options.items()])
                st.markdown(f'<div class="{css_class}"><strong>{icon} Q{i+1}. {q["question"]}</strong><br><small>{opt_text}</small><br>Your answer: <strong>{student_ans}</strong> | Correct: <strong>{correct_ans}</strong><br><em>{q.get("explanation","")}</em></div>', unsafe_allow_html=True)
            else:
                fb = written_feedback.get(i, "")
                st.markdown(f'<div class="result-correct"><strong>📝 Q{i+1}. {q["question"]}</strong><br>Your answer: {student_ans}<br>Correct: <strong>{correct_ans}</strong><br><em>{fb}</em></div>', unsafe_allow_html=True)
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
