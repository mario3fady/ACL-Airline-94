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


# -------------------------------
# SIDEBAR SETTINGS
# -------------------------------
st.sidebar.header("⚙️ Settings")

model_choice = st.sidebar.selectbox(
    "Choose LLM Model",
    ["deepseek", "gemma", "llama"]
)


st.sidebar.caption("Note: Hybrid uses both Cypher & Embeddings (recommended).")


# ======================================================
# PAGE 1 — LANDING PAGE
# ======================================================
if st.session_state.page == "welcome":

    st.markdown("""
    <div style="background-color:#1E88E5;padding:30px;border-radius:12px;">
        <h1 style='text-align: center; color: white;'>
            ✈️ Airline Knowledge Graph Assistant
        </h1>
        <p style='text-align: center; color: white; font-size: 18px;'>
            Powered by Neo4j + Hybrid Graph-RAG + Multi-LLM comparison.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    ### 🌟 What this assistant does:
    - Extracts entities from your question
    - Classifies intent using DeepSeek
    - Builds structured LLM prompts
    - Compares answers across **DeepSeek, Gemma, and Llama**
    """)

    if st.button("💬 Begin Chat"):
        st.session_state.page = "chat"
        st.rerun()


# ======================================================
# PAGE 2 — CHAT INTERFACE
# ======================================================
if st.session_state.page == "chat":

    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅ Back"):
            st.session_state.page = "welcome"
            st.rerun()

    with col2:
        if st.button("🧹 Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.user_input_key += 1
            st.rerun()

    st.markdown("<h2>🤖 Airline Knowledge Assistant</h2>", unsafe_allow_html=True)
    st.write("Ask a question about flights, delays, journeys, satisfaction scores...")

    # -------------------------------
    # Display Chat Bubbles
    # -------------------------------
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div style='text-align:right; margin:10px;'>
                    <div style='display:inline-block; background-color:#DCF8C6;
                    padding:10px 15px; border-radius:12px; max-width:70%;'>
                        🧑‍✈️ {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style='text-align:left; margin:10px;'>
                    <div style='display:inline-block; background-color:#F1F0F0;
                    padding:10px 15px; border-radius:12px; max-width:70%;'>
                        🤖 {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

    # -------------------------------
    # USER INPUT
    # -------------------------------
    user_msg = st.text_input(
        "Type your message:",
        key=f"user_input_{st.session_state.user_input_key}"
    )

    if st.button("Send"):
        if user_msg.strip() != "":
            # Save user message
            st.session_state.chat_history.append({"role": "user", "content": user_msg})

            # -----------------------------------------------------
            # RUN BACKEND: returns hybrid context + model answers
            # -----------------------------------------------------
            try:
                response = answer_question(user_msg)
            except Exception as e:
                st.error(f"Backend Error: {str(e)}")
                st.stop()

            # -----------------------------------------------------
            # Display final answer from selected model
            # -----------------------------------------------------
            model_results = response["model_comparison"]
            final_answer = model_results[model_choice]["answer"]

            # Show assistant bubble in chat
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
            st.write("Below are responses from all 3 models:")

            for model_name, data in model_results.items():
                with st.expander(f"Model: {model_name.upper()} (Latency: {data['latency_seconds']}s)"):
                    st.write(data["answer"])

            st.rerun()
