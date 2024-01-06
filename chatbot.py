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

from utils import read_prompt, load_tool, load_tools, construct_messages

open_ai_key = os.getenv("OPEN_AI_KEY")
open_ai_organisation = os.getenv("OPEN_AI_ORG")
model = "gpt-4-1106-preview"

PATH_RESEARCH_DIR = "research_papers"

def run_chat(messages, tool_choice='none'):
    '''Chat to the research chatbot'''
    
    response = client.chat.completions.create(
        model='gpt-4-1106-preview',
        messages=messages,
        tools=load_tools('tools'),
        tool_choice=tool_choice,
        temperature=0
    ).choices[0].message.content
    
    messages.append({'role':'assistant', 'content':response})
    
    return response, messages

def categorize(conversation_history, prompt):
    messages = construct_messages(conversation_history, prompt)
    category, _ = run_chat(messages)
    return category

def chatting(conversation_history, prompt):
    messages = construct_messages(conversation_history, prompt, category='chatting', step='chat')
    response, conversation_history = run_chat(messages)
    
    return response, conversation_history

def thought(conversation_history, category, prompt):
    messages = construct_messages(conversation_history, prompt, category=category, step='thought')
    response, conversation_history = run_chat(messages)
    
    return response, conversation_history

def act(conversation_history, prompt, category):
    messages = construct_messages(conversation_history, prompt, category=category, step='act')
    response, conversation_history = run_chat(messages)
    
    return response, conversation_history

def observe(conversation_history, prompt, category):
    messages = construct_messages(conversation_history, prompt, category=category, step='observe')
    response, conversation_history = run_chat(messages)
    
    return response, conversation_history
    


def ReAct(prompt,conversation_history):
    """ React Flow """
    
    #Categorize message type
    category = categorize(conversation_history, prompt)
    
    if category=='chatting':
        response, conversation_history = chatting(conversation_history, prompt)
    else:
        response = ""
        for i in range(3):
            response, conversation_history = thought(conversation_history, prompt, category)
            response, conversation_history = act(conversation_history, prompt, category)
            response, conversation_history = observe(conversation_history, prompt, category)
            if response == 'I know the final answer':
                pass # do something
                break
            return response, conversation_history
            
    return response, conversation_history

client = OpenAI()
conversation_history = []

# Streamlit
st.title("Fred's Personal Assistant 💬")

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.chat_messages:
    st.chat_message(msg["role"]).write(msg['content'])
    conversation_history.append(msg)
    
if prompt := st.chat_input(placeholder="Enter your question here"):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        response, conversation_history = ReAct(prompt,conversation_history)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.write(response)
        #st.chat_message("assistant").write(response)