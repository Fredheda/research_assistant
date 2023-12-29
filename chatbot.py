import streamlit as st
from openai import OpenAI
import openai
import os
from dotenv import load_dotenv
import pandas as pd
import json
from pypdf import PdfReader
import sqlite3
_ = load_dotenv()

from utils import read_prompt, load_tool, load_tools

open_ai_key = os.getenv("OPEN_AI_KEY")
open_ai_organisation = os.getenv("OPEN_AI_ORG")
model = "gpt-4-1106-preview"

PATH_RESEARCH_DIR = "research_papers"

def run_chat(prompt,messages, model_name="gpt-4-1106-preview",tool_path='tools', tool_choice='none'):
    '''Chat to the research chatbot'''
    
    
    messages.append({'role':'user', 'content':prompt})
    
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=load_tools(tool_path),
        tool_choice=tool_choice,
        temperature=0
    ).choices[0].message.content
    
    return response
        


client = OpenAI()
system_message = read_prompt('base_prompts/system_message.txt')
messages = [{"role": "system", "content": system_message}]


# Streamlit
st.title("Fred's Personal Assistant 💬")

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.chat_messages:
    st.chat_message(msg["role"]).write(msg['content'])
    messages.append(msg)
    
if prompt := st.chat_input(placeholder="Enter your question here"):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        response = run_chat(prompt,messages)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.write(response)
