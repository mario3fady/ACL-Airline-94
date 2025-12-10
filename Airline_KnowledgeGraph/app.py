import streamlit as st

# Backend imports
from router import answer_question

# -------------------------------
# Streamlit Page Settings
# -------------------------------
st.set_page_config(
    page_title="Airline Insights Assistant",
    layout="wide",
    page_icon="✈️"
)

# -------------------------------
# Session State Initialization
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "welcome"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_input_key" not in st.session_state:
    st.session_state.user_input_key = 0

if "theme" not in st.session_state:
    st.session_state.theme = "dark"  # default theme


# -------------------------------
# THEME HANDLER
# -------------------------------
def load_theme(theme: str) -> str:
    if theme == "dark":
        return """
        <style>
        /* Global background and text */
        html, body, [class*="css"], [data-testid="stAppViewContainer"] {
            background-color: #0F172A;
            color: #F9FAFB;
        }

        [data-testid="stSidebar"] {
            background: #020617;
        }

        /* Chat bubbles */
        .chat-user {
            background: linear-gradient(135deg, #1E88E5, #42A5F5);
            color: #F9FAFB;
            box-shadow: 0 10px 20px rgba(15, 23, 42, 0.6);
        }

        .chat-bot {
            background-color: #111827;
            color: #E5E7EB;
            box-shadow: 0 10px 20px rgba(15, 23, 42, 0.6);
        }

        /* Buttons */
        .stButton>button {
            background-color: #2563EB;
            color: white;
            border-radius: 999px;
            border: none;
            padding: 0.5rem 1.2rem;
            font-weight: 600;
            transition: all 0.25s ease;
        }

        .stButton>button:hover {
            background-color: #1D4ED8;
            transform: translateY(-1px) scale(1.03);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        /* Text input styling */
        .stTextInput > div > div > input {
            border-radius: 999px;
            padding: 0.75rem 1rem;
            border: 1px solid #1F2937;
            background-color: #020617;
            color: #E5E7EB;
        }

        .stTextInput > div > div > input:focus {
            border-color: #3B82F6;
            box-shadow: 0 0 0 1px #3B82F6;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Section titles */
        h2, h3, h4 {
            color: #E5E7EB;
        }

        /* Scrollbar tweak (dark) */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #020617;
        }
        ::-webkit-scrollbar-thumb {
            background: #1F2937;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #374151;
        }
        </style>
        """
    else:
        return """
        <style>
        /* Global background and text */
        html, body, [class*="css"], [data-testid="stAppViewContainer"] {
            background-color: #F1F5F9;
            color: #0F172A;
        }

        [data-testid="stSidebar"] {
            background: #E2E8F0;
        }

        /* Chat bubbles */
        .chat-user {
            background: linear-gradient(135deg, #DCF8C6, #B7E4C7);
            color: #0F172A;
            box-shadow: 0 10px 20px rgba(148, 163, 184, 0.4);
        }

        .chat-bot {
            background-color: #E5E7EB;
            color: #111827;
            box-shadow: 0 10px 20px rgba(148, 163, 184, 0.4);
        }

        /* Buttons */
        .stButton>button {
            background-color: #0EA5E9;
            color: white;
            border-radius: 999px;
            border: none;
            padding: 0.5rem 1.2rem;
            font-weight: 600;
            transition: all 0.25s ease;
        }

        .stButton>button:hover {
            background-color: #0284C7;
            transform: translateY(-1px) scale(1.03);
            box-shadow: 0 10px 25px rgba(14, 165, 233, 0.4);
        }

        /* Text input styling */
        .stTextInput > div > div > input {
            border-radius: 999px;
            padding: 0.75rem 1rem;
            border: 1px solid #CBD5F5;
            background-color: white;
            color: #0F172A;
        }

        .stTextInput > div > div > input:focus {
            border-color: #0EA5E9;
            box-shadow: 0 0 0 1px #0EA5E9;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Scrollbar tweak (light) */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #E5E7EB;
        }
        ::-webkit-scrollbar-thumb {
            background: #CBD5F5;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #94A3B8;
        }
        </style>
        """


# Inject CSS for selected theme
st.markdown(load_theme(st.session_state.theme), unsafe_allow_html=True)


# -------------------------------
# SIDEBAR SETTINGS
# -------------------------------
st.sidebar.header("⚙️ Settings")

# Theme toggle

if st.sidebar.button(
    "🌙 Dark Mode" if st.session_state.theme == "light" else "☀ Light Mode"
):
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
    st.rerun()

model_choice = st.sidebar.selectbox(
    "Choose LLM Model",
    ["deepseek", "gemma", "llama"]
)




# ======================================================
# PAGE 1 — LANDING PAGE
# ======================================================
if st.session_state.page == "welcome":

    st.markdown(
        """
        <div style="
            background: radial-gradient(circle at top left, #38BDF8, #1E3A8A);
            padding: 40px;
            border-radius: 24px;
            box-shadow: 0 20px 50px rgba(15,23,42,0.55);
            text-align: center;
            margin-bottom: 30px;
        ">
            <h1 style="color: #F9FAFB; font-size: 42px; margin-bottom: 10px;">
                ✈️ Airline Knowledge Graph Assistant
            </h1>
            <p style="color: #E5E7EB; font-size: 18px; max-width: 650px; margin: 0 auto;">
                Ask anything about flights, delays, journeys, and satisfaction metrics across routes and airlines,
                powered by Neo4j, Hybrid Graph RAG, and multi LLM evaluation.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            """
            ### 🌟 What this assistant does
            - Extracts entities from your question  
            - Classifies intent using DeepSeek  
            - Builds structured LLM prompts  
            - Compares answers across **DeepSeek, Gemma, and Llama**  
            """,
            unsafe_allow_html=True
        )
    with col_b:
        st.markdown(
            """
            ### 🚀 How to use
            1. Click **Begin Chat**  
            2. Ask airline analytics questions  
            3. Explore detected intent, entities, and hybrid KG context  
            4. Inspect per model answers and latencies  
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    center_col = st.columns([1, 1, 1])[1]
    with center_col:
        if st.button("💬 Begin Chat", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()


# ======================================================
# PAGE 2 — CHAT INTERFACE
# ======================================================
if st.session_state.page == "chat":

    # Navigation buttons
    top_col1, top_col2, top_col3 = st.columns([1, 1, 4])
    with top_col1:
        if st.button("⬅ Back"):
            st.session_state.page = "welcome"
            st.rerun()

    with top_col2:
        if st.button("🧹 Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.user_input_key += 1
            st.rerun()

    st.markdown(
        """
        <h2 style="margin-top: 0.5rem; margin-bottom: 0.25rem;">🤖 Airline Knowledge Assistant</h2>
        <p style="opacity: 0.85; margin-bottom: 1.5rem;">
            Ask a question about flights, delays, journeys, satisfaction scores, routes, or carriers.
        </p>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------
    # Display Chat Bubbles
    # -------------------------------
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div style='display:flex; justify-content:flex-end; margin:12px 0; animation: fadeIn 0.4s ease-in;'>
                    <div class='chat-user' style='padding:12px 18px; border-radius:18px; max-width:70%;'>
                        🧑‍✈️ {msg['content']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style='display:flex; justify-content:flex-start; margin:12px 0; animation: fadeIn 0.4s ease-in;'>
                    <div class='chat-bot' style='padding:12px 18px; border-radius:18px; max-width:70%;'>
                        🤖 {msg['content']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # -------------------------------
    # USER INPUT (Enter + Button)
    # -------------------------------
    with st.form(key="chat_form", clear_on_submit=True):
        user_msg = st.text_input(
            "Chat message",
            placeholder="Type your message here about flights, delays, journeys, or satisfaction scores...",
            key=f"user_input_{st.session_state.user_input_key}",
            label_visibility="collapsed"
)


        send_clicked = st.form_submit_button("Send")

    if send_clicked:
        if user_msg.strip() != "":
            # Save user message
            st.session_state.chat_history.append(
                {"role": "user", "content": user_msg}
            )

            # -----------------------------------------------------
            # RUN BACKEND
            # -----------------------------------------------------
            try:
                with st.spinner("✈️ Thinking... analyzing routes and satisfaction patterns..."):
                    response = answer_question(user_msg)
            except Exception as e:
                st.error(f"Backend Error: {str(e)}")
                st.stop()

            # -----------------------------------------------------
            # Display final answer
            # -----------------------------------------------------
            model_results = response["model_comparison"]
            final_answer = model_results[model_choice]["answer"]

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": final_answer
            })

            # --- Intent & Entities ---
            st.subheader("🧠 Detected Intent")
            st.write(response.get("intent", ""))

            st.subheader("🏷 Extracted Entities")
            st.json(response.get("entities", {}))

            # --- KG Retrieval Context ---
            st.subheader("🧩 Hybrid KG Context")
            st.json(response.get("context", {}))

            # --- Prompt Used ---
            with st.expander("📝 Structured Prompt Sent to LLM"):
                st.code(response.get("prompt_used", ""), language="markdown")

            # --- Model Comparison ---
            st.subheader("🤖 Model Comparisons")
            for model_name, data in model_results.items():
                with st.expander(
                    f"Model: {model_name.upper()} (Latency: {data['latency_seconds']}s)"
                ):
                    st.write(data["answer"])

            st.session_state.user_input_key += 1
            st.rerun()
