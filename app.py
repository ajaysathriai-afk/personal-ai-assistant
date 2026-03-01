import streamlit as st
import os
import base64
import time
from dotenv import load_dotenv
from core.llm import get_llm
from core.memory import build_context

# ------------------ LOAD ENV ------------------
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ OPENAI_API_KEY missing in .env file")
    st.stop()

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Personal AI Assistant",
    page_icon="🤖",
    layout="centered"
)

# ------------------ LOAD BACKGROUND IMAGE ------------------
def get_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

img = get_base64("assets/robot.jpg")

# ------------------ GLOBAL STYLING ------------------
background_style = f"""
<style>

/* Background Image */
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/jpg;base64,{img}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.65);
}}

[data-testid="stAppViewBlockContainer"] {{
    background: transparent;
    padding-top: 2rem;
}}

/* Neon Glow Animation */
@keyframes neonGlow {{
    0% {{
        text-shadow: 0 0 5px #00f5ff,
                     0 0 10px #00f5ff,
                     0 0 20px #00f5ff;
        opacity: 1;
    }}
    50% {{
        text-shadow: 0 0 25px #00f5ff,
                     0 0 50px #00f5ff,
                     0 0 80px #00f5ff;
        opacity: 0.85;
    }}
    100% {{
        text-shadow: 0 0 5px #00f5ff,
                     0 0 10px #00f5ff,
                     0 0 20px #00f5ff;
        opacity: 1;
    }}
}}

.neon-title {{
    font-size: 46px;
    font-weight: 800;
    color: #00f5ff;
    animation: neonGlow 1.8s infinite ease-in-out;
}}

/* Chat Bubbles */
.message-card {{
    padding: 14px 18px;
    border-radius: 18px;
    margin-bottom: 14px;
    backdrop-filter: blur(6px);
    width: fit-content;
    max-width: 65%;
    animation: fadeIn 0.3s ease-in;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.user-card {{
    background: linear-gradient(135deg,#007bff,#00d4ff);
    color: white;
    margin-left: auto;
}}

.assistant-card {{
    background: rgba(255,255,255,0.95);
    color: black;
    margin-right: auto;
}}

.mode-badge {{
    padding: 4px 10px;
    border-radius: 20px;
    background-color: #111;
    color: white;
    font-size: 12px;
}}

</style>
""" if img else "<style></style>"

st.markdown(background_style, unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.markdown('<h1 class="neon-title">🤖 Personal AI Assistant</h1>', unsafe_allow_html=True)
st.markdown("*Your intelligent conversation partner*")

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    mode = st.selectbox(
        "Conversation Mode",
        ["General", "Tutor", "Career Coach", "Deep Thinker"]
    )

    temperature = st.slider("Creativity Level", 0.0, 1.0, 0.7)

    if st.button("🗑️ Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("### 🧩 Active Mode")
    st.markdown(
        f"<span class='mode-badge'>{mode}</span>",
        unsafe_allow_html=True
    )
    
    if 'messages' in st.session_state:
        st.divider()
        st.markdown("### 📊 Statistics")
        st.metric("Total Messages", len(st.session_state.messages))

# ------------------ MEMORY ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

mode_prompts = {
    "General": "You are a helpful AI assistant. Be friendly and conversational. DO NOT start your responses with 'AI:' or any prefix.",
    "Tutor": "You are a patient teacher. Explain concepts clearly step by step with examples. DO NOT start your responses with 'AI:' or any prefix.",
    "Career Coach": "You are a professional career advisor. Give structured, practical career advice. DO NOT start your responses with 'AI:' or any prefix.",
    "Deep Thinker": "You are a philosophical thinker. Respond analytically with deep insights. DO NOT start your responses with 'AI:' or any prefix."
}

# Get LLM
llm = get_llm(temperature)

# ------------------ DISPLAY MESSAGES ------------------
for msg in st.session_state.messages:
    role_class = "user-card" if msg["role"] == "user" else "assistant-card"
    st.markdown(
        f"<div class='message-card {role_class}'>{msg['content']}</div>",
        unsafe_allow_html=True
    )

# ------------------ CHAT INPUT ------------------
prompt = st.chat_input("Ask something...")

if prompt:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    # Show user message immediately
    st.markdown(
        f"<div class='message-card user-card'>{prompt}</div>",
        unsafe_allow_html=True
    )
    
    # Show typing indicator with spinner
    with st.spinner("🤔 Thinking..."):
        # Build context
        context = build_context(st.session_state.messages)

        full_prompt = f"""
{mode_prompts[mode]}

Conversation:
{context}

Respond naturally to the latest user message. DO NOT include 'AI:' or any prefix in your response. Just provide the response directly.
"""

        # Get AI response
        try:
            response = llm.invoke(full_prompt)
            answer = response.content
            
            # Remove any "AI:" prefix if present
            if answer.startswith("AI:"):
                answer = answer[3:].strip()
            if answer.startswith("AI :"):
                answer = answer[4:].strip()

            # Add assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("💡 Tip: Make sure your OpenAI API key is correctly set")
    
    # Rerun to show new message
    st.rerun()

# ------------------ FOOTER ------------------
st.divider()
st.markdown("""
    <div style='text-align: center; color: #999; padding: 1rem; font-size: 14px;'>
        <p>Built with ❤️ using LangChain & Streamlit | Personal AI Assistant v1.0</p>
        <p style='font-size: 12px; margin-top: 5px;'>© 2026 Ajay Kumar Sathri</p>
    </div>
""", unsafe_allow_html=True)
