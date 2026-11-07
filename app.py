
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage
)

from database import (
    create_tables,
    register_user,
    login_user,
    create_chat,
    get_user_chats,
    get_messages,
    save_message,
    update_chat_title,
    delete_chat
)


# Page configuration
st.set_page_config(
    page_title="Nova AI Chat",
    page_icon="🤖",
    layout="wide"
)

create_tables()


# ---------------- CSS ----------------

st.markdown("""
<style>

.stApp {
    background: #0b1020;
    color: white;
}

.main .block-container {
    max-width: 1200px;
    padding: 2rem 2rem 1rem 2rem;
}

[data-testid="stSidebar"] {
    min-width: 260px !important;
    max-width: 260px !important;
    background: #111827;
}

[data-testid="stSidebar"] > div:first-child {
    width: 260px !important;
}

.hero {
    padding: 25px;
    border-radius: 18px;
    background: linear-gradient(
        120deg,
        #172554,
        #312e81,
        #164e63
    );
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
}

.hero p {
    color: #dbeafe;
}

[data-testid="stChatMessage"] {
    background: #151f31;
    border-radius: 15px;
    border: 1px solid #29364b;
}

.stButton > button {
    border-radius: 10px;
    background: #1b2940;
    color: white;
    border: 1px solid #465a80;
    width: 100%;
}

@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem;
    }
}

</style>
""", unsafe_allow_html=True)


# ---------------- AI MODEL ----------------

@st.cache_resource
def load_model():
    return ChatOpenAI(
        model="gemma4:31b",
        base_url="https://ollama.com/v1",
        api_key=st.secrets["OLLAMA_API_KEY"],
        temperature=0.7
    )

# ---------------- SESSION STATE ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "active_chat" not in st.session_state:
    st.session_state.active_chat = None


# ---------------- LOGIN PAGE ----------------

if not st.session_state.logged_in:

    st.markdown("""
    <div class="hero">
        <h1>🤖 Welcome to Nova AI</h1>
        <p>Your personal AI assistant</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Login to continue")

    login_tab, signup_tab = st.tabs(
        ["Login", "Sign Up"]
    )

    # Login form
    with login_tab:

        with st.form("login_form"):

            username = st.text_input("Username")

            password = st.text_input(
                "Password",
                type="password"
            )

            login_button = st.form_submit_button(
                "Login",
                use_container_width=True
            )

            if login_button:

                if not username.strip() or not password:
                    st.warning("Please enter username and password.")

                else:
                    user_id = login_user(
                        username,
                        password
                    )

                    if user_id:

                        st.session_state.logged_in = True
                        st.session_state.user_id = user_id
                        st.session_state.active_chat = None

                        st.success("Login successful!")
                        st.rerun()

                    else:
                        st.error("Invalid username or password.")

    # Sign up form
    with signup_tab:

        with st.form("signup_form"):

            new_username = st.text_input(
                "Choose a username"
            )

            new_password = st.text_input(
                "Choose a password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )

            signup_button = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

            if signup_button:

                if len(new_username.strip()) < 3:
                    st.warning(
                        "Username must have at least 3 characters."
                    )

                elif len(new_password) < 8:
                    st.warning(
                        "Password must have at least 8 characters."
                    )

                elif new_password != confirm_password:
                    st.error("Passwords do not match.")

                else:

                    success = register_user(
                        new_username.strip(),
                        new_password
                    )

                    if success:
                        st.success(
                            "Account created! Please login."
                        )

                    else:
                        st.error(
                            "Username already exists."
                        )

    st.stop()


# ---------------- USER CHATS ----------------

user_id = st.session_state.user_id

chats = get_user_chats(user_id)

# Create first chat for new user
if not chats:

    new_chat_id = create_chat(user_id)

    st.session_state.active_chat = new_chat_id

    st.rerun()


chat_ids = [chat[0] for chat in chats]

# Validate selected chat
if st.session_state.active_chat not in chat_ids:

    st.session_state.active_chat = chats[0][0]


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown("## 🤖 Nova AI")
    st.caption("Your personal AI assistant")

    st.divider()

    st.markdown("### 👤 Your Account")
    st.write("Logged in successfully")

    # New chat
    if st.button("＋ New Chat", use_container_width=True):

        new_chat_id = create_chat(user_id)

        st.session_state.active_chat = new_chat_id

        st.rerun()

    st.divider()

    st.markdown("### 🕘 Recent Chats")

    for chat_id, title in chats:

        if st.button(
            f"💬 {title}",
            key=f"chat_{chat_id}",
            use_container_width=True
        ):

            st.session_state.active_chat = chat_id

            st.rerun()

    st.divider()

    st.markdown("### Model Information")

    st.write("**Model:** Qwen 2.5 (3B)")
    st.write("**Framework:** LangChain")
    st.write("**Database:** SQLite")
    st.write("**Status:** Local AI")

    st.divider()

    # Delete current chat
    if st.button("🗑️ Delete Current Chat"):

        delete_chat(
            st.session_state.active_chat,
            user_id
        )

        remaining_chats = get_user_chats(user_id)

        if remaining_chats:

            st.session_state.active_chat = remaining_chats[0][0]

        else:

            st.session_state.active_chat = create_chat(user_id)

        st.rerun()

    # Logout
    if st.button("🚪 Logout"):

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.active_chat = None

        st.rerun()


# ---------------- CURRENT CHAT ----------------

active_id = st.session_state.active_chat

messages = get_messages(active_id, user_id)


# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>🤖 Nova AI Assistant</h1>
    <p>Your intelligent companion for learning, coding and creativity.</p>
</div>
""", unsafe_allow_html=True)


# ---------------- WELCOME SCREEN ----------------

if not messages:

    st.markdown("## ✨ Welcome to Nova AI")

    st.write("What would you like to explore today?")

    col1, col2 = st.columns(2)

    with col1:
        st.info("💻 Explain Python programming")
        st.info("🧠 What is Artificial Intelligence?")

    with col2:
        st.info("🚀 Suggest project ideas")
        st.info("📚 Help me prepare for exams")


# ---------------- DISPLAY MESSAGES ----------------

for message in messages:

    with st.chat_message(
        message["role"],
        avatar="👤" if message["role"] == "user" else "🤖"
    ):

        st.markdown(message["content"])


# ---------------- CHAT INPUT ----------------

prompt = st.chat_input("Message Nova AI...")

if prompt:

    # Save user message
    save_message(
        active_id,
        "user",
        prompt,
        user_id
    )

    # Update title for first message
    if not messages:

        update_chat_title(
            active_id,
            user_id,
            prompt[:30]
        )

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Load conversation history
    messages = get_messages(active_id, user_id)

    chat_history = [
        SystemMessage(
            content=(
                "You are Nova AI, a helpful and friendly assistant. "
                "Give clear and simple answers."
            )
        )
    ]

    for message in messages:

        if message["role"] == "user":

            chat_history.append(
                HumanMessage(content=message["content"])
            )

        else:

            chat_history.append(
                AIMessage(content=message["content"])
            )

    # Generate AI response
    with st.chat_message("assistant", avatar="🤖"):

        try:

            llm = load_model()

            response = st.write_stream(
                chunk.content
                for chunk in llm.stream(chat_history)
                if isinstance(chunk.content, str)
                and chunk.content
            )

            # Save assistant response
            save_message(
                active_id,
                "assistant",
                response,
                user_id
            )

        except Exception as e:

            st.error(f"AI Error: {e}")
