
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


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Nova AI Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

create_tables()

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


# ---------------- AI MODEL ----------------

@st.cache_resource
def load_model():
    api_key = st.secrets.get("OLLAMA_API_KEY", "")

    if not api_key:
        raise ValueError(
            "OLLAMA_API_KEY is missing. "
            "Please configure it in Streamlit Cloud Secrets."
        )

    return ChatOpenAI(
        model="gemma4:31b",
        base_url="https://ollama.com/v1",
        api_key=api_key,
        temperature=0.7
    )


# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

/* Main application */
.stApp {
    background: #0b1020;
    color: #f8fafc;
}

/* Header */
header[data-testid="stHeader"] {
    background: #0b1020;
}

/* Main content */
.main .block-container {
    max-width: 1200px;
    padding: 2rem 2rem 2rem 2rem;
}

/* Text visibility */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    color: #f8fafc;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #111827;
}

/* Hero section */
.hero {
    padding: 28px;
    border-radius: 18px;
    background: linear-gradient(
        120deg,
        #172554,
        #312e81,
        #164e63
    );
    margin-bottom: 25px;
    width: 100%;
    box-sizing: border-box;
}

.hero h1 {
    color: white !important;
    font-size: 2.3rem;
}

.hero p {
    color: #dbeafe !important;
    font-size: 1.1rem;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: #151f31;
    border-radius: 15px;
    border: 1px solid #29364b;
    padding: 15px;
    margin-bottom: 12px;
    width: 100%;
    box-sizing: border-box;
}

/* Chat message text */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {
    color: #f8fafc !important;
    line-height: 1.65;
    overflow-wrap: anywhere;
}

/* Chat input */
[data-testid="stChatInput"] {
    background: #151f31 !important;
    border: 1px solid #465a80 !important;
    border-radius: 14px !important;
}

[data-testid="stChatInput"] textarea {
    color: white !important;
    background: transparent !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #aab7cc !important;
}

/* Buttons */
.stButton > button {
    border-radius: 10px;
    background: #1b2940;
    color: white;
    border: 1px solid #465a80;
    width: 100%;
    min-height: 42px;
}

.stButton > button:hover {
    background: #293b5c;
    color: white;
    border-color: #60a5fa;
}

/* Forms */
[data-testid="stForm"] {
    background: #111827;
    border: 1px solid #29364b;
    border-radius: 15px;
    padding: 18px;
}

/* Input fields */
.stTextInput input {
    background: #1f2937;
    color: white;
    border-radius: 9px;
}

/* Information boxes */
[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Mobile responsive design */
@media screen and (max-width: 768px) {

    .main .block-container {
        padding: 1rem 0.7rem 5rem 0.7rem !important;
        max-width: 100% !important;
        width: 100% !important;
    }

    .hero {
        padding: 18px !important;
        border-radius: 14px !important;
        margin-bottom: 16px !important;
    }

    .hero h1 {
        font-size: 1.55rem !important;
        line-height: 1.3 !important;
    }

    .hero p {
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
    }

    [data-testid="stChatMessage"] {
        padding: 10px !important;
        border-radius: 13px !important;
        margin-bottom: 10px !important;
        width: 100% !important;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        font-size: 0.94rem !important;
        line-height: 1.6 !important;
        overflow-wrap: anywhere !important;
    }

    [data-testid="stChatInput"] {
        width: 100% !important;
        border-radius: 12px !important;
    }

    [data-testid="stChatInput"] textarea {
        font-size: 16px !important;
        color: white !important;
    }

    /* Stack columns vertically */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.5rem !important;
    }

    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 100% !important;
        width: 100% !important;
        flex: 1 1 100% !important;
    }

    /* Headings */
    h1 {
        font-size: 1.6rem !important;
    }

    h2 {
        font-size: 1.3rem !important;
    }

    h3 {
        font-size: 1.1rem !important;
    }

    /* Buttons */
    .stButton > button {
        min-height: 44px !important;
        font-size: 0.9rem !important;
    }

    /* Forms */
    [data-testid="stForm"] {
        padding: 12px !important;
    }

    /* Prevent wide content */
    .stMarkdown,
    [data-testid="stMarkdownContainer"] {
        max-width: 100% !important;
        overflow-wrap: anywhere !important;
    }

    /* Tables and code */
    [data-testid="stDataFrame"],
    pre,
    code {
        max-width: 100% !important;
        overflow-x: auto !important;
    }
}

</style>
""", unsafe_allow_html=True)


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

    # Login
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
                    st.warning(
                        "Please enter username and password."
                    )

                else:

                    user_id = login_user(
                        username.strip(),
                        password
                    )

                    if user_id:

                        st.session_state.logged_in = True
                        st.session_state.user_id = user_id
                        st.session_state.active_chat = None

                        st.success("Login successful!")
                        st.rerun()

                    else:
                        st.error(
                            "Invalid username or password."
                        )

    # Sign Up
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

# Create first chat
if not chats:

    new_chat_id = create_chat(user_id)

    st.session_state.active_chat = new_chat_id

    st.rerun()


chat_ids = [chat[0] for chat in chats]

# Validate active chat
if st.session_state.active_chat not in chat_ids:

    st.session_state.active_chat = chats[0][0]


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown("## 🤖 Nova AI")

    st.caption("Your personal AI assistant")

    st.divider()

    st.markdown("### 👤 Your Account")

    st.write("Logged in successfully")

    # New Chat
    if st.button(
        "＋ New Chat",
        use_container_width=True
    ):

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

    st.write("**Model:** Gemma 4 (31B)")
    st.write("**Framework:** LangChain")
    st.write("**Database:** SQLite")
    st.write("**Status:** Ollama Cloud")

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

    st.divider()

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

    # Update chat title
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
                "Give clear, simple and accurate answers. "
                "Explain difficult topics step by step."
            )
        )
    ]

    for message in messages:

        if message["role"] == "user":

            chat_history.append(
                HumanMessage(
                    content=message["content"]
                )
            )

        else:

            chat_history.append(
                AIMessage(
                    content=message["content"]
                )
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
