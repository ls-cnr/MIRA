from langchain_core.messages import AIMessage

response_store = {}  # Store for session-specific responses

# Module that restores the conversation's session
def get_session_responses(session_id: str):
    global response_store
    session_data = response_store.get(session_id, [])
    formatted_messages = [
        AIMessage(content=item["MIRA_response"]) for item in session_data
    ]
    return formatted_messages

# Module that saves responses in the short memory
def save_response(session_id: str, user_prompt: str, response: str):
    global response_store  # Explicitly reference the global variable
    if session_id not in response_store:
        response_store[session_id] = []
    response_store[session_id].append({"User_prompt": user_prompt, "MIRA_response": response})

# Module that rescues the conversation
def get_all_responses():
    global response_store
    return response_store