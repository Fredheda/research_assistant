import json
import os

def read_prompt(promptPath):
    with open(promptPath, 'r') as file:
        prompt = file.read()
    return prompt 

def load_tool(path):
    with open(path, 'r') as file:
        tool = json.load(file)
    return tool

def load_tools(tool_path):
    tool_dir = os.listdir(tool_path)
    tools = []
    for tool in tool_dir:
        path = os.path.join(tool_path, tool)
        tools.append(load_tool(path))
    return tools

def construct_messages(category='none', step='init', prev_messages=[]):
        
    if step == 'init':
        system_message = read_prompt('base_prompts/system_message.txt')
        messages = [{"role": "system", "content": system_message}]
    
    elif category=='chatting':
        system_message = read_prompt('base_prompts/chatting.txt')
        messages = [{"role": "system", "content": system_message}]
    
    if prev_messages != []:
        for msg in prev_messages:
            messages.append(msg)
        
        
    return messages
    

# Print the contents
#print(contents)

#def read_pdf(path, dir_path=PATH_RESEARCH_DIR):
#    """Reads PDF file and creates a string containing the content of the PDF """
#    
#    filepath=dir_path + path
#    reader = PdfReader(filepath)
#    number_of_pages = len(reader.pages)
#    content =""
#    for i in range(number_of_pages):
#        page = reader.pages[i]
#        text = page.extract_text()
#        content += text
#        content += "\n\n"
#    
#    response = f"""Content from the pdf called: {path} is given below and is delimited by triple dashes (-)
#    ---
#    {content}
#    ---
#    
#    
#    """
#    return response
#
#def update_table(query):
#    """Executes an sql query on the research_papers table which will update the table"""
#    
#    print(query)
#    result = cur.execute(query)
#    con.commit()
#    
#    output = f"successfully used {query} to update the table."
#    
#    return output
#
#def query_database(query, cur=cur):
#    """Executes an sql query on the research_papers table which will query the database"""
#    
#    print(query)
#    result = str(cur.execute(query).fetchall())
#    
#    return result
#
#def db_setup():
#    con = sqlite3.connect("research.db")
#    cur = con.cursor()
#    
#    db_tables = cur.execute("SELECT type, name, sql FROM sqlite_master WHERE type='table';").fetchall()
#    if db_tables == []:
#        cur.execute("CREATE TABLE research_papers(title, summary)")
#    
#    return cur
#    
#
#def research_assistant_wrapper(PATH_RESEARCH_DIR, cur):
#    
#    paper_list = os.listdir(PATH_RESEARCH_DIR)
#    cur = db_setup()
#    db_entries = str(cur.execute('SELECT * FROM research_papers').fetchall())
#    
#    
#    
#    
#    
#    
#    
#    
#    return answer
#
#def format_prompt(prompt, message_history, base_message, tool_call=None):
#    
#    messages = [
#        {'role':'system', 'content':base_message},
#        {'role':'system', 'content':message_history},
#        {'role':'system', 'content':prompt}
#    ]
#    
#    if tool_call:
#        messages.append(
#            {
#                "tool_call_id": tool_call.id,
#                "role": "tool",
#                "name": tool_call.function.name,
#                "content": function_response,
#            }
#        )
#    
#    return messages
#
#
#def chat(prompt, message_history, base_message, tools):
#    
#    messages = format_prompt(prompt, message_history, base_message)
#    
#    
#    return response
#    
#def run_chat(prompt,messages, model_name="gpt-4-1106-preview"):
#    '''Chat to the research chatbot'''
#    
#    messages.append({'role':'user', 'content':prompt})
#    response = client.chat.completions.create(
#        model=model_name,
#        messages=messages,
#        tools=tools,
#        tool_choice="auto",
#        temperature=0
#    )
#    
#    response_message = response.choices[0].message
#    tool_calls = response_message.tool_calls
#    
#    if tool_calls:
#        available_functions = {"read_pdf": read_pdf}
#        messages.append(response_message)
#        
#        messages = call_functions(tool_calls, messages)
#        second_response = client.chat.completions.create(
#            model=model_name,
#            messages=messages,
#            temperature=0,
#        )
#        second_response = second_response.choices[0].message.content
#        messages.pop()
#        messages.pop()
#        messages.append({'role':'assistant', 'content':second_response})
#        
#        return second_response, messages
#    messages.append({'role':'assistant', 'content':response_message.content})
#    return response_message.content, messages
#
#def call_functions(tool_calls, messages,  available_functions=available_functions):
#    
#    for tool_call in tool_calls:
#        function_name = tool_call.function.name
#        function_to_call = available_functions[function_name]
#        function_args = json.loads(tool_call.function.arguments)
#        if function_to_call == read_pdf:
#            function_response = function_to_call(
#                path=function_args.get("path"),
#            )
#        elif function_to_call == update_table or function_to_call == query_database:
#            function_response = function_to_call(
#                query=function_args.get("query"),
#            )
#        else:
#            raise ValueError('function call failed')
#        messages.append(
#            {
#                "tool_call_id": tool_call.id,
#                "role": "tool",
#                "name": function_name,
#                "content": function_response,
#            }
#        ) 
#    return messages
#
#
#
#
#
#
#    
#    
#
#