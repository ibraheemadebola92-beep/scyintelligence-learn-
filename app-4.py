import streamlit as st

st.set_page_config(page_title="SCY AI Study System", page_icon="🎓", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0f0a 100%); color: #e8e8f0; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
div[data-testid="stSidebar"] { background: #07070f; border-right: 1px solid rgba(255,255,255,0.06); }
.hero { text-align: center; padding: 40px 0 20px 0; }
.hero h1 { font-size: 2.8rem; background: linear-gradient(135deg, #00ff88, #00cc6a); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; }
.hero p { color: #a0a0b0; font-size: 1.1rem; }
.course-badge { display: inline-block; background: rgba(0,255,136,0.1); border: 1px solid rgba(0,255,136,0.3); color: #00ff88; border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; margin: 4px; }
.stButton > button { background: linear-gradient(135deg, #00ff88, #00cc6a); color: #0a0a0f; font-family: 'Syne', sans-serif; font-weight: 700; border: none; border-radius: 14px; padding: 16px 28px; font-size: 1.05rem; width: 100%; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

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
    if st.button("📚 Study Mode\nLearn any topic with AI"):
        st.switch_page("pages/1_Study.py")
    if st.button("🖥️ CBT Mode\nTimed exam simulation"):
        st.switch_page("pages/3_CBT.py")
with col2:
    if st.button("✍️ Practice Mode\nGenerate & check answers"):
        st.switch_page("pages/2_Practice.py")
    if st.button("📄 PDF Chat\nChat with your notes"):
        st.switch_page("pages/4_PDF_Chat.py")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#555;font-size:0.85rem;">Powered by SCY Intelligence • AI Study System</p>', unsafe_allow_html=True)
