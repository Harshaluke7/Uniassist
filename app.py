import streamlit as st
import joblib
import time
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from google import genai
import logging
from dotenv import load_dotenv
load_dotenv()

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
logging.getLogger("transformers").setLevel(logging.ERROR)

st.set_page_config(
    page_title="UniAssist — Smart Helpdesk",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif;
    background: #f0f4ff;
    color: #1a1a2e;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
# [data-testid="stToolbar"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * { color: #e0e6ff !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; }

.sidebar-logo {
    font-family: 'Sora', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #fff !important;
    letter-spacing: -0.5px;
    margin-bottom: 4px;
}
.sidebar-tagline {
    font-size: 12px;
    color: rgba(255,255,255,0.45) !important;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 24px;
}
.sidebar-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 500;
    margin-bottom: 8px;
    color: #a5c7ff !important;
}
.sidebar-stat-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.sidebar-stat-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: rgba(255,255,255,0.4) !important;
    margin-bottom: 4px;
}
.sidebar-stat-value {
    font-family: 'Sora', sans-serif;
    font-size: 20px;
    font-weight: 600;
    color: #fff !important;
}
.sidebar-tip {
    background: rgba(99,179,255,0.12);
    border-left: 3px solid #63b3ff;
    border-radius: 0 10px 10px 0;
    padding: 10px 14px;
    font-size: 13px;
    color: #a5c7ff !important;
    margin-top: 8px;
}

/* ── Main content area ── */
[data-testid="stMain"] {
    background: #f0f4ff;
}
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Header bar ── */
.header-bar {
    background: #ffffff;
    border-bottom: 1px solid #e2e8f8;
    padding: 18px 36px;
    display: flex;
    align-items: center;
    gap: 14px;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 20px rgba(99,130,255,0.06);
    position: relative;
    top: auto;
    z-index: 1;
}
.header-avatar {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
}
.header-title {
    font-family: 'Sora', sans-serif;
    font-size: 18px;
    font-weight: 600;
    color: #1a1a2e;
    letter-spacing: -0.3px;
}
.header-subtitle {
    font-size: 12px;
    color: #8896b3;
    margin-top: 1px;
}
.status-dot {
    width: 8px; height: 8px;
    background: #22c55e;
    border-radius: 50%;
    box-shadow: 0 0 0 3px rgba(34,197,94,0.2);
    animation: pulse-green 2s infinite;
    margin-left: auto;
}
@keyframes pulse-green {
    0%, 100% { box-shadow: 0 0 0 3px rgba(34,197,94,0.2); }
    50% { box-shadow: 0 0 0 6px rgba(34,197,94,0.08); }
}

/* ── Chat scroll area ── */
.chat-scroll {
    height: calc(100vh - 160px);
    overflow-y: auto;
    padding: 24px 36px 16px;
    scroll-behavior: smooth;
}
.chat-scroll::-webkit-scrollbar { width: 4px; }
.chat-scroll::-webkit-scrollbar-track { background: transparent; }
.chat-scroll::-webkit-scrollbar-thumb { background: #d0d9f0; border-radius: 4px; }

/* ── Welcome card ── */
.welcome-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(102,126,234,0.3);
}
.welcome-card::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 160px; height: 160px;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
}
.welcome-card::after {
    content: '';
    position: absolute;
    bottom: -60px; right: 60px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.welcome-greeting {
    font-family: 'Sora', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 6px;
    position: relative; z-index: 1;
}
.welcome-desc {
    font-size: 14px;
    color: rgba(255,255,255,0.75);
    line-height: 1.6;
    position: relative; z-index: 1;
}
.chip-row {
    display: flex; flex-wrap: wrap; gap: 8px;
    margin-top: 16px;
    position: relative; z-index: 1;
}
.chip {
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 12px;
    color: #fff;
    backdrop-filter: blur(4px);
    cursor: default;
    transition: background 0.2s;
}
.chip:hover { background: rgba(255,255,255,0.28); }

/* ── Chat bubbles ── */
.msg-row {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    margin-bottom: 16px;
    animation: fadeSlideUp 0.35s ease both;
}
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
.msg-row.user { flex-direction: row-reverse; }

.msg-avatar {
    width: 34px; height: 34px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    flex-shrink: 0;
    color: #ffffff;
    letter-spacing: -0.5px;
}
.msg-avatar.bot-avatar {
    background: linear-gradient(135deg, #667eea, #764ba2);
    box-shadow: 0 4px 12px rgba(102,126,234,0.35);
    font-size: 11px;
}
.msg-avatar.user-avatar {
    background: linear-gradient(135deg, #f093fb, #f5576c);
    box-shadow: 0 4px 12px rgba(245,87,108,0.3);
    font-size: 15px;
}
.bubble {
    max-width: 72%;
    min-width: fit-content;
    padding: 13px 18px;
    border-radius: 18px;
    font-size: 14.5px;
    line-height: 1.65;
    position: relative;
    word-wrap: break-word;
    white-space: pre-wrap;
    display: inline-block;
}
.bubble.bot {
    background: #ffffff;
    color: #1a1a2e;
    border-bottom-left-radius: 4px;
    box-shadow: 0 2px 16px rgba(99,130,255,0.1);
    border: 1px solid #eaedff;
}
.bubble.user {
    background: linear-gradient(135deg, #667eea 0%, #5a67d8 100%);
    color: #ffffff;
    border-bottom-right-radius: 4px;
    box-shadow: 0 4px 18px rgba(102,126,234,0.35);
}
.bubble-time {
    font-size: 10px;
    margin-top: 4px;
    color: #b0bcd6;
    text-align: right;
}
.bubble.bot + .bubble-time { text-align: left; }

/* ── Typing indicator ── */
.typing-bubble {
    background: #ffffff;
    border: 1px solid #eaedff;
    border-radius: 18px;
    border-bottom-left-radius: 4px;
    padding: 14px 20px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    box-shadow: 0 2px 16px rgba(99,130,255,0.1);
}
.typing-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #667eea;
    animation: bounce 1.4s infinite ease-in-out;
}
.typing-dot:nth-child(1) { animation-delay: 0s; }
.typing-dot:nth-child(2) { animation-delay: 0.18s; }
.typing-dot:nth-child(3) { animation-delay: 0.36s; }
@keyframes bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
    30%            { transform: translateY(-6px); opacity: 1; }
}

/* ── Dividers ── */
.date-divider {
    text-align: center;
    font-size: 11px;
    color: #b0bcd6;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    margin: 20px 0 14px;
    position: relative;
}
.date-divider::before, .date-divider::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 35%;
    height: 1px;
    background: #e2e8f8;
}
.date-divider::before { left: 0; }
.date-divider::after  { right: 0; }

/* ── Source tag ── */
.source-tag {
    display: inline-flex; align-items: center; gap: 4px;
    background: #eef2ff;
    color: #667eea;
    font-size: 10.5px;
    font-weight: 500;
    padding: 2px 9px;
    border-radius: 10px;
    margin-top: 6px;
    letter-spacing: 0.2px;
}

/* ── Input area ── */
.input-wrapper {
    background: #ffffff;
    border-top: 1px solid white;
    padding: 14px 36px 18px;
    position: sticky;
    bottom: 0;
    box-shadow: 0 -4px 20px rgba(99,130,255,0.06);
}

/* Streamlit chat_input override */
[data-testid="stChatInput"] {
    border-radius: 14px !important;
    border: 2px solid #e2e8f8 !important;
    background: #f7f9ff !important;
    transition: border-color 0.2s !important;
    box-shadow: 0 2px 12px rgba(99,130,255,0.05) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #667eea !important;
    box-shadow: 0 0 0 4px rgba(102,126,234,0.1) !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14.5px !important;
    color: #1a1a2e !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(99,130,255,0.2) !important;
}

/* ── Clear button — fully explicit overrides ── */
[data-testid="stChatInput"] {
    border-radius: 14px !important;
    border: 2px solid #e2e8f8 !important;
    background: #ffffff !important;
    transition: border-color 0.2s !important;
    box-shadow: 0 2px 12px rgba(99,130,255,0.05) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #667eea !important;
    box-shadow: 0 0 0 4px rgba(102,126,234,0.1) !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14.5px !important;
    color: #1a1a2e !important;
    background: #ffffff !important;
    caret-color: #667eea !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #a0aec0 !important;
    opacity: 1 !important;
}
""", 
unsafe_allow_html=True)

client = genai.Client(api_key=os.environ.get("AQ.Ab8RN6InJzFjrMRbxCEFrnvetI1lcHvXFf202CirFUHZVlmY5A"))

from shared import get_sbert, get_knowledge
model_st = get_sbert()
embeddings, responses = get_knowledge()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "msg_count" not in st.session_state:
    st.session_state.msg_count = 0
if "kb_hits" not in st.session_state:
    st.session_state.kb_hits = 0

def enhance_response(query, base_response, source="kb"):
    try:
        source_note = (
            "This answer comes from the university knowledge base."
            if source == "kb"
            else "This answer was generated by AI."
        )
        prompt = f"""
You are UniAssist, a warm and helpful AI assistant for a university helpdesk.

User asked: "{query}"

Raw answer: "{base_response}"

Context: {source_note}

Your job is to rewrite the raw answer into a polished, friendly, well-formatted reply.

Rules:
1. PRESERVE every detail exactly — all links, emails, room numbers, names, phone numbers
2. Use a warm, approachable tone — like a helpful senior student
3. Use relevant emojis naturally (don't overdo it)
4. Use bullet points or short sections where it helps readability
5. If the answer contains a link, present it clearly with a label like: 🔗 [Visit here](url)
6. If the answer has contact info (email/room/name), format it as a neat contact card block
7. Add a short 1-line friendly opener that acknowledges what the user asked
8. End with a brief helpful closer like "Let me know if you need anything else! 😊" — but only if it feels natural
9. Do NOT invent any new information. Do NOT add details not in the raw answer.
10. Keep the total response concise — no unnecessary padding

Respond with ONLY the final improved message, no preamble.
"""
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt
        )
        return response.text.strip()

    except:
        return base_response

def llm_response(query):
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=query
        )
        return response.text
    except Exception:
        return "⚠️ Unable to process your request right now. Please try again."

def get_timestamp():
    return time.strftime("%I:%M %p")

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🎓 UniAssist</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">AI-Powered Helpdesk</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-badge">🟢 &nbsp;System Online</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-badge">⚡ &nbsp;Gemini Fallback Ready</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Session Stats**")

    st.markdown(f"""
    <div class="sidebar-stat-card">
        <div class="sidebar-stat-label">Messages Sent</div>
        <div class="sidebar-stat-value">{st.session_state.msg_count}</div>
    </div>
    <div class="sidebar-stat-card">
        <div class="sidebar-stat-label">Knowledge Base Hits</div>
        <div class="sidebar-stat-value">{st.session_state.kb_hits}</div>
    </div>
    <div class="sidebar-stat-card">
        <div class="sidebar-stat-label">AI Fallback Used</div>
        <div class="sidebar-stat-value">{max(0, st.session_state.msg_count - st.session_state.kb_hits)}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**How It Works**")
    st.markdown("""
    <div class="sidebar-tip">
        Your query is embedded with <b>MiniLM</b>, matched via cosine similarity. 
        If confidence ≥ 0.4, the knowledge base answers. Otherwise, <b>Gemini AI</b> responds.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Quick Topics**")
    for topic in ["📋 Admissions", "💳 Fee Structure", "🏛️ Facilities", "📅 Academic Calendar", "🎓 Scholarships"]:
        st.markdown(f"<div class='sidebar-badge'>{topic}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("🗑️  Clear Conversation"):
        st.session_state.chat_history = []
        st.session_state.msg_count = 0
        st.session_state.kb_hits   = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="header-bar">
    <div class="header-avatar">🎓</div>
    <div>
        <div class="header-title">University Helpdesk</div>
        <div class="header-subtitle">Hybrid NLP · Knowledge Base + Gemini AI</div>
    </div>
    <div class="status-dot"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-scroll" id="chat-scroll">', unsafe_allow_html=True)

if not st.session_state.chat_history:
    st.markdown("""
    <div class="welcome-card">
        <div class="welcome-greeting">👋 Hello! I'm UniAssist</div>
        <div class="welcome-desc">
            Your AI-powered university helpdesk. I can answer questions about admissions,
            fees, facilities, schedules, scholarships, and more — instantly.
        </div>
        <div class="chip-row">
            <span class="chip">📋 Admission process</span>
            <span class="chip">💳 Fee payment</span>
            <span class="chip">🏛️ Campus facilities</span>
            <span class="chip">📅 Exam schedule</span>
            <span class="chip">🎓 Scholarships</span>
        </div>
    </div>
    <div class="date-divider">Start of conversation</div>
    """, unsafe_allow_html=True)

for i, (role, msg, ts, source) in enumerate(st.session_state.chat_history):
    if role == "user":
        st.markdown(f"""
        <div class="msg-row user">
            <div>
                <div class="bubble user">{msg}</div>
                <div class="bubble-time">{ts}</div>
            </div>
            <div class="msg-avatar user-avatar">U</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        source_tag = (
            '<span class="source-tag">&#128218; Knowledge Base</span>' if source == "kb"
            else '<span class="source-tag">&#10024; Gemini AI</span>'
        )
        st.markdown(f"""
        <div class="msg-row bot">
            <div class="msg-avatar bot-avatar">AI</div>
            <div>
                <div class="bubble bot">{msg}</div>
                {source_tag}
                <div class="bubble-time">{ts}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close chat-scroll

st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)
user_input = st.chat_input("Ask anything about your university…")
st.markdown('</div>', unsafe_allow_html=True)

if user_input:
    ts = get_timestamp()
    st.session_state.chat_history.append(("user", user_input, ts, None))
    st.session_state.msg_count += 1

    with st.spinner(""):
        query_embedding = model_st.encode([user_input])
        similarity      = cosine_similarity(query_embedding, embeddings)
        best_match      = similarity.argmax()
        time.sleep(0.4)  # typing feel

        if similarity[0][best_match] >= 0.4:
            raw_answer = responses[best_match]
            answer = enhance_response(user_input, raw_answer, source="kb")
            source = "kb"
            st.session_state.kb_hits += 1
        else:
            raw_answer = llm_response(user_input)
            answer = enhance_response(user_input, raw_answer, source="ai")
            source = "ai"

    bot_ts = get_timestamp()
    st.session_state.chat_history.append(("bot", answer, bot_ts, source))
    st.rerun()

st.markdown("""
<script>
    const chatEl = document.getElementById('chat-scroll');
    if (chatEl) chatEl.scrollTop = chatEl.scrollHeight;
    // Also scroll the whole page bottom
    window.scrollTo(0, document.body.scrollHeight);
</script>
""", unsafe_allow_html=True)