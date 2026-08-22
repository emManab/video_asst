import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv(override=True)

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS (Neo-Brutalism / Gen-Z) ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Syne:wght@700;800&display=swap');

:root {
    --bg: #F4F0EA;       /* Cream background */
    --text: #000000;     /* Pure black */
    --accent: #FF3333;   /* Bright red */
    --accent-blue: #3366FF;
    --border: #000000;
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
    background-image: radial-gradient(#000000 1.5px, transparent 1.5px);
    background-size: 25px 25px;
    background-color: var(--bg);
    background-position: 0 0, 12.5px 12.5px;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
    font-weight: 800 !important;
    text-transform: uppercase;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(3rem, 7vw, 5.5rem);
    font-weight: 800;
    line-height: 0.9;
    margin: 0;
    color: var(--text);
    text-transform: uppercase;
    text-shadow: 4px 4px 0px var(--accent);
}

.hero-sub {
    font-size: 1.2rem;
    font-weight: 600;
    margin-top: 1rem;
    background: var(--text);
    color: var(--bg) !important;
    display: inline-block;
    padding: 0.3rem 0.6rem;
    border: 3px solid var(--border);
    transform: rotate(-1deg);
}

/* Brutalist Cards */
.card {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 3px solid var(--border);
    border-radius: 0;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 8px 8px 0px var(--border);
    transition: all 0.2s ease;
}
.card * {
    color: #000000 !important;
}
.card:hover {
    transform: translate(-4px, -4px);
    box-shadow: 12px 12px 0px var(--accent-blue);
}

.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    text-transform: uppercase;
    border-bottom: 3px solid var(--border);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
    color: #000000 !important;
}

.card-content {
    font-size: 1rem;
    line-height: 1.6;
    font-weight: 600;
    color: #000000 !important;
}

/* Inputs & Buttons */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: #FFFFFF !important;
    border: 3px solid var(--border) !important;
    border-radius: 0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    padding: 0.8rem !important;
    box-shadow: 4px 4px 0px var(--border) !important;
    transition: all 0.1s !important;
}

/* Force text inside inputs and selectbox selection to be black */
.stTextInput > div > div > input {
    color: #000000 !important;
}

.stSelectbox > div > div,
.stSelectbox > div > div *,
.stSelectbox > div > div > div,
.stSelectbox > div > div > div * {
    color: #000000 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    font-size: 1.05rem !important;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div:focus {
    box-shadow: 4px 4px 0px var(--accent) !important;
    outline: none !important;
}

.stButton > button {
    background: var(--accent) !important;
    color: white !important;
    border: 3px solid var(--border) !important;
    border-radius: 0 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.2rem !important;
    text-transform: uppercase !important;
    padding: 1rem 2rem !important;
    box-shadow: 6px 6px 0px var(--border) !important;
    transition: all 0.1s !important;
    width: 100%;
}

.stButton > button:hover {
    transform: translate(-2px, -2px) !important;
    box-shadow: 8px 8px 0px var(--border) !important;
}
.stButton > button:active {
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0px var(--border) !important;
}

/* Chat Message styling */
[data-testid="stChatMessage"] {
    background: #FFFFFF;
    color: #000000 !important;
    border: 3px solid var(--border);
    border-radius: 0;
    box-shadow: 4px 4px 0px var(--border);
    margin-bottom: 1.5rem;
    padding: 1rem;
}
[data-testid="stChatMessage"] * {
    color: #000000 !important;
}
[data-testid="stChatMessage"] p {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
    color: #000000 !important;
}
[data-testid="chatAvatarIcon-user"] {
    background-color: var(--accent-blue) !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background-color: var(--accent) !important;
}

/* BOTTOM CONTAINER TRANSPARENT (Removes the full-width black bar) */
[data-testid="stBottomBlockContainer"], 
[data-testid="stBottom"], 
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
.stChatFloatingInputContainer,
.stChatFloatingInputContainer > div {
    background: transparent !important;
}

/* SLEEK CHAT INPUT (Light Pill, Neo-Brutalist) */
[data-testid="stChatInput"] {
    background: #FFFFFF !important;
    border: 3px solid var(--border) !important;
    box-shadow: 6px 6px 0px var(--border) !important;
    border-radius: 40px !important;
    max-width: 768px !important;
    margin: 0 auto !important;
    padding: 0.3rem 0.5rem !important;
    transition: all 0.2s ease;
}
/* Force inner wrappers to be transparent and remove default focus borders */
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] > div:focus-within,
[data-testid="stChatInput"] > div > div:focus-within {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"]:focus-within {
    transform: translate(-2px, -2px);
    box-shadow: 8px 8px 0px var(--accent-blue) !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    color: #000000 !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #888888 !important;
}
[data-testid="stChatInput"] button {
    background: var(--text) !important;
    color: #FFFFFF !important;
    border-radius: 50% !important;
    width: 38px !important;
    height: 38px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 5px;
    transition: all 0.2s !important;
}
[data-testid="stChatInput"] button:hover {
    background: var(--accent) !important;
    transform: scale(1.05);
}

/* Expander (RAW Transcript) styling */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 3px solid var(--border) !important;
    border-radius: 0 !important;
    box-shadow: 6px 6px 0px var(--border) !important;
    margin-bottom: 1.5rem !important;
    color: #000000 !important;
}
[data-testid="stExpander"] summary {
    padding: 1rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.1rem !important;
    text-transform: uppercase !important;
    color: #000000 !important;
}
[data-testid="stExpander"] summary * {
    color: #000000 !important;
}
[data-testid="stExpander"] summary:hover {
    background: #F4F0EA !important;
}

/* Transcript Box */
.transcript-box {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 3px solid var(--border);
    padding: 1.5rem;
    font-size: 0.95rem;
    line-height: 1.6;
    max-height: 350px;
    overflow-y: auto;
    font-weight: 500;
    box-shadow: inset 4px 4px 0px rgba(0,0,0,0.05);
}

/* Status dots */
.status-bar {
    background: #FFFFFF !important;
    color: #000000 !important;
    border: 3px solid var(--border);
    padding: 0.5rem 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    font-weight: 600;
    box-shadow: 3px 3px 0px var(--border);
}
.status-bar span, .status-bar p, .status-bar div {
    color: #000000 !important;
}
.status-dot { width: 12px; height: 12px; border: 2px solid var(--border); }
.dot-active { background: var(--accent); animation: blink 1s infinite; }
.dot-done { background: #00FF00; }
.dot-pending { background: #FFFFFF; }
@keyframes blink { 50% { opacity: 0; } }

/* Overrides */
[data-testid="stMarkdownContainer"] p { color: #000000 !important; }
label { color: var(--text) !important; font-family: 'Space Grotesk', sans-serif !important; font-weight: 700 !important; font-size: 1.1rem !important; text-transform: uppercase; }

/* Make main block slightly narrower for better readability if desired */
.block-container {
    max-width: 1200px !important;
}

/* Hide Sidebar toggle */
[data-testid="collapsedControl"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "pipeline_done": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ─── Main Header ──────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">AI VIDEO</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">NO MORE BORING MEETINGS</div>', unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)


# ─── Input Section ────────────────────────────────────────────────────────────────
if not st.session_state.result:
    st.markdown("""
    <div class="card" style="box-shadow: 12px 12px 0px var(--accent);">
        <div class="card-title">🔥 DROP YOUR LINK</div>
        <div class="card-content">
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1], gap="large")
    with col1:
        source = st.text_input("URL OR FILE PATH", placeholder="https://youtube.com/watch?v=...")
    with col2:
        language = st.selectbox("AUDIO LANGUAGE", ["english", "hinglish"], index=0)
    
    st.markdown("<br>", unsafe_allow_html=True)
    btn_col = st.empty()
    run_btn = False
    cancel_btn = False

    if not st.session_state.get("processing", False):
        run_btn = btn_col.button("IGNITE ANALYSIS", icon=":material/rocket_launch:")
    else:
        cancel_btn = btn_col.button("CANCEL 🛑", type="primary")

    if cancel_btn:
        st.session_state.processing = False
        st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)

    # ── Run Pipeline ────────────────────────────────────────────────────────────────
    if run_btn:
        if not source.strip():
            st.error("Please enter a YouTube URL or file path.")
        else:
            st.session_state.processing = True
            st.session_state.pipeline_done = False
            st.session_state.result        = None
            st.session_state.chat_history  = []
            st.rerun()

    if st.session_state.get("processing", False):
        try:
            with st.status("⚙️ PROCESSING…", expanded=True) as status:
                # ── Step 1: Audio
                status.update(label="🔊 RIPPING AUDIO…")
                st.write("Extracting chunks...")
                chunks = process_input(source)

                # ── Step 2: Transcription
                status.update(label="📝 LISTENING…")
                st.write("Transcribing audio to English...")
                transcript = transcribe_all(chunks, language)

                # ── Step 3: Title
                status.update(label="🏷️ NAMING IT…")
                st.write("Generating title...")
                title = generate_title(transcript)

                # ── Step 4: Summary
                status.update(label="📋 SUMMARIZING…")
                st.write("Building summary...")
                summary = summarize(transcript)

                # ── Step 5: Extraction
                status.update(label="🔍 EXTRACTING INTEL…")
                st.write("Pulling action items and decisions...")
                action_items = extract_action_items(transcript)
                decisions    = extract_key_decisions(transcript)
                questions    = extract_questions(transcript)

                # ── Step 6: RAG
                status.update(label="🧠 WAKING UP AI…")
                st.write("Preparing chat engine...")
                rag_chain = build_rag_chain(transcript)

                status.update(label="✅ DONE!", state="complete", expanded=False)

            st.session_state.result = {
                "title":        title,
                "transcript":   transcript,
                "summary":      summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain":    rag_chain,
            }
            st.session_state.pipeline_done = True
            st.session_state.processing = False
            time.sleep(0.4)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.session_state.processing = False

# ─── Results Dashboard ──────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # Title banner & New Analysis Button
    col_t1, col_t2 = st.columns([4, 1], gap="large")
    with col_t1:
        st.markdown(f"""
        <div class="card" style="border-color: var(--accent); box-shadow: 12px 12px 0px var(--accent);">
            <div class="card-title">TITLE</div>
            <div style="font-family:'Syne',sans-serif;font-size:2.5rem;font-weight:800;text-transform:uppercase;">{r['title']}</div>
        </div>""", unsafe_allow_html=True)
    with col_t2:
        if st.button("NEW ANALYSIS 🔄", use_container_width=True):
            st.session_state.result = None
            st.session_state.processing = False
            st.session_state.pipeline_done = False
            st.session_state.chat_history = []
            st.rerun()

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown(f'<div class="card"><div class="card-title">TL;DR SUMMARY</div><div class="card-content">{r["summary"]}</div></div>', unsafe_allow_html=True)
    with col2:
        with st.expander("FULL TRANSCRIPT (RAW)"):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="large")
    with c1: st.markdown(f'<div class="card" style="box-shadow: 6px 6px 0px #00FF00;"><div class="card-title">DO THIS</div><div class="card-content">{r["action_items"]}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card" style="box-shadow: 6px 6px 0px var(--accent-blue);"><div class="card-title">DECIDED</div><div class="card-content">{r["key_decisions"]}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="card" style="box-shadow: 6px 6px 0px var(--accent);"><div class="card-title">UNANSWERED</div><div class="card-content">{r["open_questions"]}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="hero-title" style="font-size:2.5rem; margin-bottom:1rem; text-shadow: 3px 3px 0px var(--accent-blue);">INTERROGATE THE AI</div>', unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Render reset button if history exists
    if st.session_state.chat_history:
        if st.button("NUKE CHAT 💥", key="reset_chat"):
            st.session_state.chat_history = []
            st.rerun()
            
    # Add some bottom padding so chat input doesn't overlap reset button
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    # Chat input fixed at bottom
    if prompt := st.chat_input("Ask something about the meeting..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_question(r["rag_chain"], prompt)
                st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})