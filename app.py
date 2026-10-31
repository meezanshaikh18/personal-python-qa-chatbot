import streamlit as st

from chatbot import answer_question, build_vectorizer, load_knowledge_base

st.set_page_config(page_title="Python Q&A Bot", page_icon="🐍")
st.title("🐍 Python Q&A Bot")
st.caption("Ask me a Python question. I answer from a built-in knowledge base.")


@st.cache_resource
def load_bot():
    """Build the vectorizer once, not on every message."""
    questions, answers = load_knowledge_base()
    vectorizer, matrix = build_vectorizer(questions)
    return questions, answers, vectorizer, matrix


questions, answers, vectorizer, matrix = load_bot()

with st.sidebar:
    st.header("About")
    st.write(f"Knowledge base: {len(questions)} question phrasings")
    show_debug = st.checkbox("Show match details")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_input := st.chat_input("Type your Python question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    reply, score, matched = answer_question(
        user_input, vectorizer, matrix, questions, answers
    )
    if show_debug:
        reply += f"\n\n*Matched: {matched} (score {score:.2f})*"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)