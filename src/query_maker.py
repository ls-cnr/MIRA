from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import OllamaLLM
from goal_tree_utils import *
import re

with open('json_docs/models.json', 'r') as f:
    data = json.load(f)

selected_model_name = data["selected_model"]
model_params = data["models"][selected_model_name]

model_params.pop("model", None)

# Definition of the LLM
llm = OllamaLLM(model=selected_model_name, **model_params)

# Importing goal_tree and prompts
with open("json_docs/json_name.json", "r", encoding="utf-8") as f:
    json_name = json.load(f)

def query_maker(reactive_response, user_prompt, goal_array, chat_history):
    responses = {
        'response': [],
        'goal': [],
        'score': []
    }

    responses['response'].append(reactive_response)
    responses['goal'].append('Reactive response')

    with open('json_docs/prompts.json', 'r') as f:
        prompt_data = json.load(f)

    # Module that generates proactive responses
    for goal in goal_array:
        proactive_dialog_act_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"Your task is to carefully analyze the user's input {user_prompt} and focus exclusively on identifying, using your related information {goal['information']}, the specific request related to {goal['goal_name']} ."
                    f" Your primary objective is to address or clarify any aspects of the {goal['goal_name']} in detail."
                    "\n\nBased on the content of the user's input, you must take one of the following approaches:"
                    f"\n1) Provide a clear and accurate response to the user's potential question related to {goal['goal_name']}."
                    f"\n2) If the input is unclear, ask a specific clarifying question to better understand the user's intent regarding {goal['goal_name']}."
                    f"\n3) When appropriate, provide a hybrid response that combines an answer with a question to guide the user in revealing more details about {goal['goal_name']}."
                    "\n\nYour response must meet these criteria:"
                    f"\n- Be directly relevant to {goal['goal_name']} and avoid introducing any unrelated information."
                    "\n- Stay concise, focused, and actionable based on the user's input."
                    f"\n- Avoid assumptions; base your response strictly on the content of {user_prompt} and only request clarification when necessary."
                    f"\n- Ensure your response aligns with these specific guidelines: {prompt_data['query_maker_prompt']}."
                    "\n\nAdditional Instructions:"
                    f"\n- Respond always in {prompt_data['language']}, regardless of the language of the input."
                    f"\n- Follow these personality and response style expectations: {prompt_data['personality']} and {prompt_data['social_practice']}."
                    "\n\nKeep your focus sharp and your responses accurate to ensure clear and meaningful interactions."
                    "\n\nPlease generate answers as short as you can."
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        chain = proactive_dialog_act_prompt | llm

        query = chain.invoke(
            {
                'goal': goal['goal_name'],
                "'goal[information]'": goal['information'],
                'messages': chat_history,
            }
        )

        responses['response'].append(query)
        responses['goal'].append(goal['goal_name'])

    for response, goal in zip(responses['response'], goal_array):
        # Invoking the LLM to generate the priorities of the goals from the infos extracted from the user_prompt
        score_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"Evaluate the relevance of the {response} to the {user_prompt} in relation to the goal '{goal['goal_name']}' and its {goal['goal_type']}."
                    "\n\n### Evaluation Rules:"
                    f"\n1. Focus on how the {response} aligns with the goal '{goal['goal_name']}'."
                    "\n2. Assign one of the following score levels based on relevance and depth:"
                    "\n   - **high**: The response directly addresses the goal, provides detailed alignment, and is clearly relevant."
                    "\n   - **medium**: The response moderately addresses the goal, with some alignment but lacking full detail."
                    "\n   - **low**: The response has minimal or no alignment with the goal, or is vague."
                    "\n\n### Examples:"
                    "\n- If the response explicitly mentions the goal and provides detailed support, assign 'high'."
                    "\n- If the response partially aligns but lacks clarity or depth, assign 'medium'."
                    "\n- If the response is unrelated, vague, or unclear, assign 'low'."
                    "\n\n### Output Rules:"
                    "Your output must be strictly one of the following words: 'high', 'medium', or 'low'."
                    "\n- **Do not include any punctuation marks, additional words, or symbols.**"
                    "\n- Do not use any dots, ellipses, or extra characters in your output."
                    "\n- **Provide only the word**: 'high', 'medium', or 'low'."
                    "\n- Any deviation from this format will be treated as invalid."
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        chain = score_prompt | llm
        query_priorities = chain.invoke(
            {
                "response": response,
                "messages": [HumanMessage(content=user_prompt)],
                "'goal[goal_name]'": goal['goal_name'],
                "'goal[goal_type]'": goal['goal_type']
            }
        )

        responses['score'].append(query_priorities.lower())

    goal_tree = load_goal_tree(json_name["goal_tree"])

    update_goal_tree_from_responses(goal_tree, [], [], responses['score'], goal_array, flag=True)

    # Writing all the answers in the JSON file.
    result_list = []

    for response, goal, score in zip(responses['response'], responses['goal'], responses['score']):
        result = {
            "response": response,  # The answer
            "goal": goal, # The goal
            "score": score,  # The equivalent score
        }
        result_list.append(result)

    with open("json_docs/response.json", "w", encoding="utf-8") as f:
        json.dump(result_list, f, ensure_ascii=False, indent=4)

    return responses