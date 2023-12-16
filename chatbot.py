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

open_ai_key = os.getenv("OPEN_AI_KEY")
open_ai_organisation = os.getenv("OPEN_AI_ORG")
model = "gpt-4-1106-preview"
PATH_RESEARCH_DIR = "research_papers"

client = OpenAI()
con = sqlite3.connect("research.db")
cur = con.cursor()

def read_pdf(path, dir_path=PATH_RESEARCH_DIR):
    """Reads PDF file and creates a string containing the content of the PDF """
    
    filepath=dir_path + path
    reader = PdfReader(filepath)
    number_of_pages = len(reader.pages)
    content =""
    for i in range(number_of_pages):
        page = reader.pages[i]
        text = page.extract_text()
        content += text
        content += "\n\n"
    
    response = f"""Content from the pdf called: {path} is given below and is delimited by triple dashes (-)
    ---
    {content}
    ---
    
    
    """
    return response

def update_table(query):
    """Executes an sql query on the research_papers table which will update the table"""
    
    print(query)
    result = cur.execute(query)
    con.commit()
    
    output = f"successfully used {query} to update the table."
    
    return output

def query_database(query, cur=cur):
    """Executes an sql query on the research_papers table which will query the database"""
    
    print(query)
    result = str(cur.execute(query).fetchall())
    
    return result

paper_list = os.listdir(PATH_RESEARCH_DIR)
db_tables = cur.execute("SELECT type, name, sql FROM sqlite_master WHERE type='table';").fetchall()
if db_tables == []:
    cur.execute("CREATE TABLE research_papers(title, abstract, summary)")
db_entries = str(cur.execute('SELECT title FROM research_papers').fetchall())

system_message = f"""
You are a personal research assistant. Your task is to support the user with literature reviews.

You should act as a chatbot.

You are given always given access to the following research papers:
{paper_list}.

you also have access to a database, containing a single table called research papers, with schema detailed below:
title: TEXT
abstract: TEXT
summary: TEXT

The following papers are already in the database:
{db_entries}

Any questions about Data science or Generative AI, should **only** be answered using the information contained in the research papers.

Additional guidance:
- Whenever you are asked about one or more research paper, you should always first check if the paper(s) already have an entry in the database. If they do, query the database to retrieve additional information.
- If a question cannot be answered using data that is in the database, you should refer to the papers that are available to you. You should offer to create an entry for relevant papers in the database.
- If you intend to run an sql query which will update the table, you should prepare the sql query and ask the user to confirm that you are to run that sql query.
- Whenever you summarise a paper or create a database entry, you should aim to do create a summary that is **500-1000 words long**, to ensure you capture enough detail.
- Make sure that the "abstract field, contains the exact abstract as it is written in the paper."
- Ensure that you are using sqlite3 syntax and use double quotes in your sql statements
- Once you have updated the database, you should confirm to the user that you have finished the task.
"""

messages = [
    {"role": "system", "content": system_message},
]
tools = [
    {
        "type": "function",
        "function": {
            "name": "update_table",
            "description": "Executes an sql query on the research_papers table which will update the table",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query",
                    }
                },
                "required": ["query"],
            },
        },
    },
    
    
    {
        "type": "function",
        "function": {
            "name": "read_pdf",
            "description": "Read the content of a PDF",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The filepath for the PDF document",
                    }
                },
                "required": ["path"],
            },
        },
    },
    
    
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Query the research_papers table in the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "the sql query",
                    }
                },
                "required": ["query"],
            },
        },
    },
]

available_functions = {
    "read_pdf": read_pdf,
    "update_table": update_table,
    "query_database": query_database
}

def call_functions(tool_calls, messages,  available_functions=available_functions):
    
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        if function_to_call == read_pdf:
            function_response = function_to_call(
                path=function_args.get("path"),
            )
        elif function_to_call == update_table or function_to_call == query_database:
            function_response = function_to_call(
                query=function_args.get("query"),
            )
        else:
            raise ValueError('function call failed')
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        ) 
    return messages

def run_chat(prompt,messages, model_name="gpt-4-1106-preview"):
    '''Chat to the research chatbot'''
    
    messages.append({'role':'user', 'content':prompt})
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    if tool_calls:
        available_functions = {"read_pdf": read_pdf}
        messages.append(response_message)
        
        messages = call_functions(tool_calls, messages)
        second_response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0,
        )
        second_response = second_response.choices[0].message.content
        messages.pop()
        messages.pop()
        messages.append({'role':'assistant', 'content':second_response})
        
        return second_response, messages
    messages.append({'role':'assistant', 'content':response_message.content})
    return response_message.content, messages

st.title("Fred's Research Chatbot 💬")

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.chat_messages:
    st.chat_message(msg["role"]).write(msg['content'])
    messages.append(msg)
    
if prompt := st.chat_input(placeholder="Enter your question here"):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        response, messages = run_chat(prompt,messages)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.write(response)