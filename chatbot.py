"""Public Groq LLM chatbot for the login/home page."""

import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

load_dotenv()


def _get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None, "GROQ_API_KEY not found. Please set it in your .env file."
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.3,
        api_key=api_key,
    )
    return llm, None


def render_public_chatbot():
    """Render the Groq chatbot section on the public home/login page."""
    st.markdown(
        "<p style='text-align:center;color:#475569;font-size:0.95rem;margin-bottom:1.5rem;'>"
        "Ask health-related questions or get general assistance before signing in."
        "</p>",
        unsafe_allow_html=True,
    )

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found. Please set it in your .env file.")
        return

    user_input = st.text_area(
        "Enter your prompt:",
        value="How can I login and signup ?",
        height=120,
    )

    if st.button("Run LLM", type="primary", use_container_width=True):
        if not user_input.strip():
            st.warning("Please enter a prompt.")
            return

        llm, err = _get_llm()
        if err:
            st.error(err)
            return

        with st.spinner("Thinking..."):
            response = llm.invoke([HumanMessage(content=user_input)])

        st.subheader("Response:")
        st.write(response.content)
