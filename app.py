import streamlit as st
import requests
import json
import time
import PyPDF2
import io

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SCY AI Study System",
    page_icon="🎓",
    layout="centered"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
}

.main {
    background: #0a0a0f;
    color: #e8e8f0;
}

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0f0a 100%);
}

.mode-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
}

.score-box {
    background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
    color: #0a0a0f;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
}

.question-box {
    background: rgba(0, 255, 136, 0.05);
    border-left: 3px solid #00ff88;
    border-radius: 8px;
    padding: 16px;
    margin: 12px 0;
}

.result-correct {
    background: rgba(0, 255, 136, 0.1);
    border-left: 3px solid #00ff88;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}

.result-wrong {
    background: rgba(255, 60, 60, 0.1);
    border-left: 3px solid #ff3c3c;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}

.stButton > button {
    background: linear-gradient(135deg, #00ff88, #00cc6a);
    color: #0a0a0f;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 12px 28px;
    font-size: 1rem;
    cursor: pointer;
    width: 100%;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,255,136,0.3);
}

.timer-display {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #00ff88;
    text-align: center;
    padding: 12px;
    border: 2px solid #00ff88;
    border-radius: 12px;
    margin-bottom: 16px;
}

.timer-warning {
    color: #ff6b00;
    border-color: #ff6b00;
}

.timer-danger {
    color: #ff3c3c;
    border-color: #ff3c3c;
}

.chat-user {
    background: rgba(0,255,136,0.08);
    border-radius: 12px 12px 2px 12px;
    padding: 12px 16px;
    margin: 8px 0;
    text-align: right;
}

.chat-ai {
    background: rgba(255,255,255,0.05);
    border-radius: 12px 12px 12px 2px;
    padding: 12px 16px;
    margin: 8px 0;
}

div[data-testid="stSidebar"] {
    background: #07070f;
    border-right: 1px solid rgba(255,255,255,0.06);
}

.stSelectbox label, .stTextInput label, .stTextArea label {
    color: #a0a0b0 !important;
    font-family: 'DM Sans', sans-serif;
}

.stRadio label {
    color: #e8e8f0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# COURSE DATA
# ─────────────────────────────────────────────
COURSES = {
    "MTH 102 — Mathematics": {
        "topics": [
            "Functions of a real variable, graphs, limits, and continuity",
            "Derivatives and differentiation techniques",
            "Maxima and minima",
            "Curve sketching",
            "Integration and definite integrals",
            "Reduction formulae",
            "Areas and volumes (Trapezium and Simpson's rules)"
        ]
    },
    "CHM 102 — Organic Chemistry": {
        "topics": [
            "History of organic chemistry",
            "Fullerenes and nanochemistry",
            "Electronic theory in organic chemistry",
            "Isolation and purification of organic compounds",
            "Nomenclature and functional groups",
            "Reaction mechanisms and kinetics",
            "Stereochemistry",
            "Alkanes, alkenes, alkynes",
            "Alcohols, ethers, amines, alkyl halides",
            "Aldehydes, ketones, carboxylic acids",
            "Chemistry of metals, non-metals, and transition metals"
        ]
    },
    "PHY 102 — Electricity & Magnetism": {
        "topics": [
            "Forces in nature",
            "Electrostatics and Coulomb's law",
            "Electric field and potential",
            "Gauss's law and capacitance",
            "Conductors and insulators",
            "DC circuit analysis and Ohm's law",
            "Magnetic fields and Lorentz force",
            "Biot-Savart and Ampère's laws",
            "Electromagnetic induction",
            "Faraday and Lenz's laws",
            "Transformers and self/mutual inductance",
            "Maxwell's equations",
            "AC circuits with inductors, capacitors, resistance"
        ]
    },
    "PHY 104 — Waves & Optics": {
        "topics": [
            "Simple harmonic motion (SHM)",
            "Damped SHM, Q values, resonance",
            "Forced SHM and transients",
            "Coupled SHM and normal modes",
            "Types and properties of waves",
            "Superposition, interference, diffraction",
            "Dispersion and polarisation",
            "Echo, beats, and Doppler effect",
            "Sound propagation in gases, solids, liquids",
            "Nature and propagation of light",
            "Reflection and refraction",
            "Internal reflection and dispersion",
            "Thin lenses and optical instruments",
            "Huygens's principle"
        ]
    },
    "STA 112 — Statistics & Probability": {
        "topics": [
            "Permutation and combination",
            "Concepts and principles of probability",
            "Random variables",
            "Probability and distribution functions",
            "Binomial distribution",
            "Geometric distribution",
            "Poisson distribution",
            "Normal distribution",
            "Sampling distributions",
            "Exploratory data analysis"
        ]
    }
}

# ─────────────────────────────────────────────
# API CALL
# ─────────────────────────────────────────────
def call_ai(messages, system_prompt):
    api_key = st.secrets["OPENROUTER_API_KEY"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://scyintelligence.streamlit.app",
        "X-Title": "SCY AI Study System"
    }
    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "max_tokens": 2000
    }
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ─────────────────────────────────────────────
# EXTRACT PDF TEXT
# ─────────────────────────────────────────────
def extract_pdf_text(uploaded_file):
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text[:8000]  # limit to avoid token overflow
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 SCY AI Study System")
    st.markdown("*100L Engineering — Rain Semester*")
    st.markdown("---")
    mode = st.radio(
        "Select Mode",
        ["📚 Study Mode", "✍️ Practice Mode", "🖥️ CBT Mode", "📄 PDF Chat"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**Courses Available**")
    for c in COURSES:
        st.markdown(f"• {c}")

# ─────────────────────────────────────────────
# STUDY MODE
# ─────────────────────────────────────────────
if mode == "📚 Study Mode":
    st.markdown("# 📚 Study Mode")
    st.markdown("*Your AI tutor — ask anything about your courses*")

    course = st.selectbox("Select Course", list(COURSES.keys()))
    topic = st.selectbox("Select Topic", COURSES[course]["topics"])
    custom = st.text_input("Or type a specific question / subtopic (optional)")

    if "study_chat" not in st.session_state:
        st.session_state.study_chat = []

    if st.button("Teach Me 🚀"):
        question = custom if custom else f"Teach me about: {topic}"
        course_context = f"""
You are an expert university tutor for 100-Level Engineering students in Nigeria.
Course: {course}
Topic: {topic}
Course outline topics: {', '.join(COURSES[course]['topics'])}

Teach clearly with:
1. Simple explanation
2. Detailed breakdown
3. 2 worked examples
4. Exam tips
Stay strictly within the course content.
"""
        with st.spinner("Thinking..."):
            response = call_ai(
                st.session_state.study_chat + [{"role": "user", "content": question}],
                course_context
            )
        st.session_state.study_chat.append({"role": "user", "content": question})
        st.session_state.study_chat.append({"role": "assistant", "content": response})

    # Follow-up chat
    if st.session_state.study_chat:
        st.markdown("---")
        for msg in st.session_state.study_chat:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">🧑‍🎓 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

        followup = st.text_input("Ask a follow-up question...", key="study_followup")
        if st.button("Send 💬"):
            if followup:
                system = f"You are an expert tutor for {course}. Continue helping the student understand {topic}. Stay within the course content."
                with st.spinner("Thinking..."):
                    response = call_ai(
                        st.session_state.study_chat + [{"role": "user", "content": followup}],
                        system
                    )
                st.session_state.study_chat.append({"role": "user", "content": followup})
                st.session_state.study_chat.append({"role": "assistant", "content": response})
                st.rerun()

        if st.button("Clear Chat 🗑️"):
            st.session_state.study_chat = []
            st.rerun()

# ─────────────────────────────────────────────
# PRACTICE MODE
# ─────────────────────────────────────────────
elif mode == "✍️ Practice Mode":
    st.markdown("# ✍️ Practice Mode")
    st.markdown("*Generate questions and get your answers marked*")

    course = st.selectbox("Select Course", list(COURSES.keys()))
    topic = st.selectbox("Select Topic", COURSES[course]["topics"])
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    if "practice_questions" not in st.session_state:
        st.session_state.practice_questions = ""
    if "practice_answers" not in st.session_state:
        st.session_state.practice_answers = {}

    if st.button("Generate Questions 📝"):
        system = f"""You are an exam question setter for {course} (100-Level Engineering, Nigeria).
Generate exactly 5 practice questions on: {topic}
Difficulty: {difficulty}
Format each question as:
Q1. [question]
Q2. [question]
...
Do NOT include answers yet. Questions only."""
        with st.spinner("Generating questions..."):
            st.session_state.practice_questions = call_ai(
                [{"role": "user", "content": f"Generate {difficulty} questions on {topic} for {course}"}],
                system
            )
        st.session_state.practice_answers = {}

    if st.session_state.practice_questions:
        st.markdown("---")
        st.markdown(f'<div class="question-box">{st.session_state.practice_questions}</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### ✍️ Type Your Answers")

        for i in range(1, 6):
            st.session_state.practice_answers[f"q{i}"] = st.text_area(
                f"Your answer to Q{i}",
                value=st.session_state.practice_answers.get(f"q{i}", ""),
                key=f"ans_{i}"
            )

        if st.button("Check My Answers ✅"):
            answers_text = "\n".join([
                f"Q{i}: {st.session_state.practice_answers.get(f'q{i}', 'No answer')}"
                for i in range(1, 6)
            ])
            system = f"""You are a university examiner for {course}.
Questions asked: {st.session_state.practice_questions}
Student answers: {answers_text}
For each question:
- Mark correct or incorrect
- Give the correct answer
- Explain why
Be encouraging but honest."""
            with st.spinner("Marking your answers..."):
                feedback = call_ai(
                    [{"role": "user", "content": "Please mark my answers"}],
                    system
                )
            st.markdown("### 📊 Feedback")
            st.markdown(f'<div class="chat-ai">🤖 {feedback}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CBT MODE
# ─────────────────────────────────────────────
elif mode == "🖥️ CBT Mode":
    st.markdown("# 🖥️ CBT Mode")
    st.markdown("*Timed computer-based test — exam simulation*")

    if "cbt_state" not in st.session_state:
        st.session_state.cbt_state = "setup"
    if "cbt_questions" not in st.session_state:
        st.session_state.cbt_questions = []
    if "cbt_answers" not in st.session_state:
        st.session_state.cbt_answers = {}
    if "cbt_start_time" not in st.session_state:
        st.session_state.cbt_start_time = None
    if "cbt_results" not in st.session_state:
        st.session_state.cbt_results = ""
    if "cbt_current_q" not in st.session_state:
        st.session_state.cbt_current_q = 0

    # ── SETUP ──
    if st.session_state.cbt_state == "setup":
        course = st.selectbox("Select Course", list(COURSES.keys()))
        topic = st.selectbox("Select Topic", ["All Topics"] + COURSES[course]["topics"])
        num_q = st.selectbox("Number of Questions", [10, 20, 30, 40])
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"])
        duration = st.selectbox("Time Allowed", ["15 minutes", "30 minutes", "45 minutes", "60 minutes"])

        if st.button("Start CBT 🚀"):
            topic_str = topic if topic != "All Topics" else f"all topics in {course}"
            system = f"""You are a CBT question generator for {course} (100-Level Engineering, Nigeria).
Generate exactly {num_q} questions on {topic_str}. Difficulty: {difficulty}.
Mix multiple choice (A,B,C,D) and short written answer questions.
Format STRICTLY as JSON array:
[
  {{
    "type": "mcq",
    "question": "question text",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "answer": "A",
    "explanation": "why this is correct"
  }},
  {{
    "type": "written",
    "question": "question text",
    "answer": "correct answer",
    "explanation": "explanation"
  }}
]
Return ONLY the JSON array. No preamble, no markdown."""

            with st.spinner(f"Generating {num_q} questions..."):
                raw = call_ai(
                    [{"role": "user", "content": f"Generate {num_q} CBT questions"}],
                    system
                )
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

    # ── TESTING ──
    elif st.session_state.cbt_state == "testing":
        questions = st.session_state.cbt_questions
        total = len(questions)
        current = st.session_state.cbt_current_q

        # Timer
        elapsed = time.time() - st.session_state.cbt_start_time
        remaining = st.session_state.cbt_duration - elapsed

        if remaining <= 0:
            st.session_state.cbt_state = "results"
            st.rerun()

        mins = int(remaining // 60)
        secs = int(remaining % 60)
        timer_class = "timer-display"
        if remaining < 120:
            timer_class += " timer-danger"
        elif remaining < 300:
            timer_class += " timer-warning"

        st.markdown(f'<div class="{timer_class}">⏱ {mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
        st.progress((current) / total)
        st.markdown(f"**Question {current + 1} of {total}**")

        q = questions[current]
        st.markdown(f'<div class="question-box"><strong>Q{current+1}. {q["question"]}</strong></div>', unsafe_allow_html=True)

        if q["type"] == "mcq":
            options = q.get("options", {})
            choice = st.radio(
                "Select your answer:",
                list(options.keys()),
                format_func=lambda x: f"{x}. {options[x]}",
                key=f"cbt_mcq_{current}"
            )
            st.session_state.cbt_answers[current] = choice
        else:
            answer = st.text_area("Your answer:", key=f"cbt_written_{current}")
            st.session_state.cbt_answers[current] = answer

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if current > 0:
                if st.button("⬅ Previous"):
                    st.session_state.cbt_current_q -= 1
                    st.rerun()
        with col2:
            if current < total - 1:
                if st.button("Next ➡"):
                    st.session_state.cbt_current_q += 1
                    st.rerun()
        with col3:
            if st.button("Submit Test 🏁"):
                st.session_state.cbt_state = "results"
                st.rerun()

        # Auto-refresh for timer
        time.sleep(1)
        st.rerun()

    # ── RESULTS ──
    elif st.session_state.cbt_state == "results":
        st.markdown("## 🏁 Test Complete!")
        questions = st.session_state.cbt_questions
        answers = st.session_state.cbt_answers
        total = len(questions)

        # Auto-score MCQ
        score = 0
        mcq_count = 0
        written_qs = []

        for i, q in enumerate(questions):
            if q["type"] == "mcq":
                mcq_count += 1
                if answers.get(i, "").strip().upper() == q["answer"].strip().upper():
                    score += 1
            else:
                written_qs.append({
                    "index": i,
                    "question": q["question"],
                    "student_answer": answers.get(i, ""),
                    "correct_answer": q["answer"]
                })

        # Score written answers via AI
        written_score = 0
        written_feedback = {}
        if written_qs:
            written_text = "\n".join([
                f"Q: {w['question']}\nStudent: {w['student_answer']}\nCorrect: {w['correct_answer']}"
                for w in written_qs
            ])
            system = f"""You are marking written answers for {st.session_state.get('cbt_course', 'a university course')}.
For each written question, give a score of 0 or 1 and brief feedback.
Return ONLY JSON: [{{"index": 0, "score": 1, "feedback": "..."}}]"""
            with st.spinner("Marking written answers..."):
                raw = call_ai(
                    [{"role": "user", "content": written_text}],
                    system
                )
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
            st.success("🌟 Excellent performance! Keep it up!")
        elif percentage >= 50:
            st.warning("📖 Good effort! Review the topics you missed.")
        else:
            st.error("💪 Keep studying! You'll do better next time.")

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
                st.markdown(f"""
<div class="{css_class}">
<strong>{icon} Q{i+1}. {q['question']}</strong><br>
<small>{opt_text}</small><br>
Your answer: <strong>{student_ans}</strong> | Correct: <strong>{correct_ans}</strong><br>
<em>{q.get('explanation', '')}</em>
</div>""", unsafe_allow_html=True)
            else:
                fb = written_feedback.get(i, "")
                st.markdown(f"""
<div class="result-correct">
<strong>📝 Q{i+1}. {q['question']}</strong><br>
Your answer: {student_ans}<br>
Correct answer: <strong>{correct_ans}</strong><br>
<em>{fb}</em>
</div>""", unsafe_allow_html=True)

        if st.button("🔄 Start New Test"):
            st.session_state.cbt_state = "setup"
            st.session_state.cbt_questions = []
            st.session_state.cbt_answers = {}
            st.rerun()

# ─────────────────────────────────────────────
# PDF CHAT MODE
# ─────────────────────────────────────────────
elif mode == "📄 PDF Chat":
    st.markdown("# 📄 PDF Chat")
    st.markdown("*Upload your notes or textbook and ask the AI anything about it*")

    uploaded = st.file_uploader("Upload your PDF", type=["pdf"])

    if "pdf_chat" not in st.session_state:
        st.session_state.pdf_chat = []
    if "pdf_text" not in st.session_state:
        st.session_state.pdf_text = ""

    if uploaded:
        if st.session_state.pdf_text == "":
            with st.spinner("Reading your PDF..."):
                st.session_state.pdf_text = extract_pdf_text(uploaded)
            st.success(f"✅ PDF loaded! ({len(st.session_state.pdf_text)} characters read)")

        question = st.text_input("Ask a question about your PDF...")
        if st.button("Ask 💬"):
            if question:
                system = f"""You are a study assistant. Answer questions ONLY based on the document content below.
If the answer is not in the document, say so clearly.

DOCUMENT CONTENT:
{st.session_state.pdf_text}"""
                with st.spinner("Reading and answering..."):
                    response = call_ai(
                        st.session_state.pdf_chat + [{"role": "user", "content": question}],
                        system
                    )
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
