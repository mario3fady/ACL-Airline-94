import streamlit as st
import requests

# -------------------------------
# Streamlit Page Settings
# -------------------------------
st.set_page_config(
    page_title="Airline Insights Chat Assistant",
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
# SIDEBAR SETTINGS (Always visible)
# -------------------------------
st.sidebar.header("⚙️ Settings")

model = st.sidebar.selectbox(
    "Choose LLM Model",
    ["deepseek", "llama (locked)", "gemma (locked)"]
)
selected_model = "deepseek"

if "locked" in model:
    st.sidebar.warning("🔒 This model is locked. DeepSeek will be used automatically.")

retrieval_method = st.sidebar.selectbox(
    "Retrieval Method",
    ["baseline", "embeddings", "hybrid"]
)

theme = st.sidebar.selectbox(
    "Theme",
    ["Airline", "Hotel", "FPL"]
)

backend_url = st.sidebar.text_input(
    "Backend URL",
    "http://localhost:8000/query"
)



# ======================================================
# PAGE 1 — GREETING / LANDING PAGE
# ======================================================
if st.session_state.page == "welcome":

    st.markdown("""
    <div style="background-color:#1E88E5;padding:30px;border-radius:12px;">
        <h1 style='text-align: center; color: white;'>
            ✈️ Welcome to the Airline Insights Chat Assistant
        </h1>
        <p style='text-align: center; color: white; font-size: 18px;'>
            Your intelligent assistant powered by Neo4j Knowledge Graphs + DeepSeek LLM.<br>
            Explore flights, delays, airport performance, and more with accuracy and clarity.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    ## 🌟 What this assistant does:
    - Understands your question using **Intent Classification**
    - Extracts key entities like airports, flights, and dates
    - Retrieves structured knowledge from **Neo4j Knowledge Graph**
    - Produces grounded, non-hallucinated answers using **DeepSeek**
    """)

    st.markdown("### 🚀 Ready to begin?")
    if st.button("💬 Start Asking Questions"):
        st.session_state.page = "chat"
        st.rerun()



# ======================================================
# PAGE 2 — CHATBOT INTERFACE
# ======================================================
if st.session_state.page == "chat":

    # Back + Clear buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back to Home"):
            st.session_state.page = "welcome"
            st.rerun()

    with col2:
        if st.button("🧹 Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.user_input_key += 1
            st.rerun()

    st.markdown("""
    <h2>🤖 Airline Insights ChatBot</h2>
    <p>Ask about flights, delays, routes, airport statistics, or satisfaction insights.</p>
    <hr>
    """, unsafe_allow_html=True)

    # -------------------------------
    # Display CHAT BUBBLES
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
    # USER INPUT BOX
    # -------------------------------
    user_msg = st.text_input(
        "Type your message:",
        key=f"user_input_{st.session_state.user_input_key}"
    )

    if st.button("Send"):
        if user_msg.strip() != "":
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": user_msg})

            # Simulated backend response (replace later)
            fake_response = {
                "intent": "flight_search",
                "entities": {"origin": "Cairo", "destination": "Dubai"},
                "cypher_query": "MATCH (f:Flight)...",
                "kg_context": {
                    "nodes": ["Flight123", "Airport_CAI", "Airport_DXB"],
                    "relationships": ["DEPARTS_FROM", "ARRIVES_TO"]
                },
                "llm_answer": "There are 5 flights today from Cairo to Dubai with minimal delays."
            }

            # Add assistant response
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": fake_response["llm_answer"]
            })

            # System information sections
            st.subheader("🧠 Detected Intent")
            st.write(fake_response["intent"])

            st.subheader("🏷️ Extracted Entities")
            st.json(fake_response["entities"])

            with st.expander("📄 Cypher Query Executed"):
                st.code(fake_response["cypher_query"], language="cypher")

            st.subheader("🗂️ KG Retrieved Context")
            st.json(fake_response["kg_context"])

            st.subheader("🤖 Final Answer")
            st.write(fake_response["llm_answer"])

            st.rerun()
