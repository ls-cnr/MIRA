from flask import Flask, request, jsonify, render_template
import time
from langchain_core.messages import SystemMessage
from query_maker import *
from chooser import *
from goal_tree_analyzer import *
from goal_tree_utils import *
from short_memory import *
import json

app = Flask(__name__)

# Importing goal_tree and prompts
with open("json_docs/json_name.json", "r", encoding="utf-8") as f:
    json_name = json.load(f)

# Loading model data from 'models.json'
with open('json_docs/models.json', 'r') as f:
    model_data = json.load(f)

selected_model_name = model_data["selected_model"]
model_params = model_data["models"][selected_model_name]
model_params.pop("model", None)

# Initializing LLM
llm = OllamaLLM(model=selected_model_name, **model_params)

# Loading prompt data from 'prompts.json'
with open(json_name["prompts"], 'r') as f:
    prompt_data = json.load(f)

@app.route('/')
def index():
    """Render the main interface."""
    set_goal_uncompleted(json_name["goal_tree"])
    return render_template('index.html')

# Module responsible for the conversation
@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_prompt = data.get('query', '')
    session_id = data.get('session_id', 'default_session')
    is_continue = data.get('is_continue', False)

    if not user_prompt and not is_continue:
        return jsonify({"error": "Query is required"}), 400

    # Starting timing
    start_time = time.perf_counter()

    # Retrieving previous responses as chat history
    chat_history = get_session_responses(session_id)
    if not is_continue:  # If it's a new prompt, add to history
        chat_history.append(HumanMessage(content=user_prompt))

    # Setting up the LLM prompt
    reactive_response_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content=f"Your name is {prompt_data['name']} "
                        f"You are {prompt_data['conversation_prompt']}. "
                        "Your task is to analyze the user's requests, understand them, and provide the best response. "
                        f"\n- Follow these personality and response style expectations: {prompt_data['personality']} and {prompt_data['social_practice']}."
                        f"Always respond in {prompt_data['language']}, regardless of input language."
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    # Processing the user prompt with the LLM
    chain = reactive_response_prompt | llm
    llm_answer = chain.invoke({
        "messages": chat_history
    })

    # Generating questions based on user input and LLM answer
    questions = query_maker(llm_answer, user_prompt, goal_tree_analyzer(user_prompt), chat_history)

    # Calculating elapsed time
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    elapsed_time = round(elapsed_time, 3)

    # Making decision based on the status of the flag
    if set_flag():
        return jsonify({
            "response": llm_answer,
            "show_continue_prompt": True,
            "elapsed_time": elapsed_time,
        })

    # Default response if no continuation is needed
    response = chooser(questions)

    # Saving the response to the session-specific store
    save_response(session_id, user_prompt, response)

    with open("json_docs/conversation.json", "w", encoding="utf-8") as f:
        json.dump(response_store, f, ensure_ascii=False, indent=4)

    return jsonify({
        "response": response,
        "elapsed_time": elapsed_time,
    })

# Module responsible for continuing the conversation when the root goal is satisfied
@app.route('/continue', methods=['POST'])
def continue_route():
    data = request.json
    choice = data.get('choice')
    user_prompt = data.get('query', '')
    session_id = data.get('session_id', 'default_session')
    last_response = data.get('last_response')

    if not last_response:
        return jsonify({"error": "No response received from the previous request"}), 400

    # Salvataggio della risposta finale
    save_response(session_id, user_prompt, last_response)

    with open("json_docs/conversation.json", "w", encoding="utf-8") as f:
        json.dump(response_store, f, ensure_ascii=False, indent=4)

    if choice == "No":
        set_goal_uncompleted(json_name["goal_tree"])
        return jsonify({
            "response": "Travel booked, have a nice trip! :)",
            "show_end_screen": True
        })
    elif choice == "Yes":
        return jsonify({
            "response": last_response,
            "show_end_screen": False
        })
    else:
        return jsonify({"error": "Invalid choice"}), 400

if __name__ == '__main__':
    # Initialize the goal tree
    set_goal_uncompleted(json_name["goal_tree"])
    app.run(debug=True)