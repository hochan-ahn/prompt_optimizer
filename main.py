import os

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

MODEL_NAME = "gemini-2.5-flash"
BASE_STYLE = """
    <style>
    body, .stApp {
        background-color: #f7f7f7;
        color: #1f1f1f;
    }
    .stChatMessage {
        background: white;
        border: 1px solid #e6e6e6;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .stChatMessage:nth-child(odd) {
        background: #fcfcfc;
    }
    </style>
"""


def load_api_key() -> str:
    """Load the Google Gemini API key from the environment."""
    load_dotenv()
    return os.getenv("GOOGLE_API_KEY", "")


def generate_response(user_prompt: str, system_instruction: str = "") -> str:
    """
    Send the user's prompt to Gemini and return the text response.

    A system instruction can be provided to steer the model's behavior
    (e.g., "너는 도움이 되는 AI 어시스턴트야").
    """
    api_key = load_api_key()
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing. Add it to your .env file.")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        MODEL_NAME, system_instruction=system_instruction or None
    )
    response = model.generate_content(user_prompt)
    return response.text or ""


def main() -> None:
    st.set_page_config(page_title="Gemini Chatbot Starter", page_icon="🤖")
    st.title("Gemini Chatbot Starter")
    st.markdown(BASE_STYLE, unsafe_allow_html=True)

    api_key = load_api_key()

    if api_key:
        st.success("API key loaded successfully.")
        st.caption(f"Loaded key ends with: {api_key[-4:]}")
    else:
        st.error(
            "GOOGLE_API_KEY is missing. Add it to your .env file to continue."
        )
        st.stop()

    # Initialize chat state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False

    # Sidebar controls
    with st.sidebar:
        st.subheader("설정")
        system_instruction = st.text_area(
            "System instruction",
            value="너는 도움이 되는 AI 어시스턴트야",
            help="모델의 톤/행동을 지정할 수 있습니다.",
        )
        if st.button("대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.session_state.is_generating = False
            st.experimental_rerun()

    # Render chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_prompt = st.chat_input(
        "메시지를 입력하세요",
        disabled=st.session_state.is_generating,
    )

    if user_prompt:
        # Add user message to history and display
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Generate assistant reply
        st.session_state.is_generating = True
        with st.spinner("Gemini가 응답을 생성 중..."):
            try:
                reply = generate_response(user_prompt, system_instruction)
            except Exception as exc:  # pragma: no cover - UI feedback only
                st.error(f"Error: {exc}")
                st.session_state.is_generating = False
                return

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.is_generating = False


if __name__ == "__main__":
    main()

