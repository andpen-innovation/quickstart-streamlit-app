import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
import os

st.title('🦜🔗 Quickstart App')

# OpenAI API key input from user
openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

# Set the key in environment (some packages rely on this)
os.environ["OPENAI_API_KEY"] = openai_api_key

def generate_response(input_text):
    llm = init_chat_model(
        "gpt-4o-mini",
        model_provider="openai",
        openai_api_key=openai_api_key
    )
    response = llm.invoke([HumanMessage(content=input_text)])
    st.info(response.content)

with st.form('my_form'):
    text = st.text_area('Enter text:', 'What are the three key pieces of advice for learning how to code?')
    submitted = st.form_submit_button('Submit')
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    if submitted and openai_api_key.startswith('sk-'):
        generate_response(text)
