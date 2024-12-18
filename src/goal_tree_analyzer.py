from langchain_core.messages import HumanMessage
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_ollama import OllamaLLM
from goal_tree_utils import *

# Importing goal_tree and prompts
with open("json_docs/json_name.json", "r", encoding="utf-8") as f:
    json_name = json.load(f)

def goal_tree_analyzer(user_prompt):
    goal_array = []  # List to contain only the goals that satisfy the criteria
    responses = [] # List to contain only the responses of the LLM
    informations = [] # List to contain only the infos gathered from the user_prompt

    # Rescuing selected_model and its parameters from 'models.json'
    with open('json_docs/models.json', 'r') as f:
        prompt_data = json.load(f)

    selected_model_name = prompt_data["selected_model"]
    model_params = prompt_data["models"][selected_model_name]

    model_params.pop("model", None)

    # Definition of the LLM
    llm = OllamaLLM(model=selected_model_name, **model_params)

    # Function to load the sub-goals of each goal
    def load_id(goal):
        if 'children' in goal:
            for child in goal['children']:
                if child['status'] == 'uncompleted' and not any(c['status'] == 'uncompleted' for c in child.get('children', [])):
                    goal_array.append({
                        'goal_name': child['goal_name'],
                        'description': child.get('description', ''),
                        'goal_link': child.get('goal_link', ''),
                        'score': child.get('score', 0),
                        'information': child.get('information', ''),
                        'goal_type': child['goal_type']
                    })
        if 'children' in goal:
            for child in goal['children']:
                load_id(child)

    # Loading 'prompt_data' value to provide the prompt specific examples.
    with open('json_docs/prompts.json', 'r') as f:
        prompt_data = json.load(f)

    # Invoking 'load_goal_tree' to load the goal tree
    goal_tree = load_goal_tree(json_name["goal_tree"])

    # Invoking 'load_id' to load the goals
    for root_goal in goal_tree['goals']:
        load_id(root_goal)

    # Invoking the LLM on each goal in 'goal_array'
    for goal in goal_array:
        verification_goal_status_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"Your task is to evaluate whether the {user_prompt} explicitly mentions, refers to, or negates the goal named '{goal['goal_name']}'."
                    "\n\n### Stricter Evaluation Rules:"
                    "\n1. **Mark as 'completed'** only if all of the following conditions are met:"
                    f"\n   - The goal '{goal['goal_name']}' is explicitly mentioned in {user_prompt} using the exact term, precise synonyms, or clearly equivalent and unambiguous descriptions."
                    f"\n   - OR the goal is explicitly negated (e.g., 'I don’t want {goal['goal_name']}') with clear and direct language."
                    "\n   - The reference to the goal must be specific and leave no room for interpretation."
                    "\n   - There is no ambiguity, vagueness, or partial mention of the goal."
                    "\n2. **Mark as 'uncompleted'** if any of the following are true:"
                    f"\n   - The {user_prompt} does not clearly and explicitly mention, describe, or negate the goal '{goal['goal_name']}'."
                    f"\n   - The {user_prompt} only partially mentions or vaguely references the goal, leaving room for interpretation."
                    f"\n   - The {user_prompt} is unrelated, ambiguous, or generic, even if it hints at the goal without being specific."
                    f"\n   - The {user_prompt} includes broad or generic statements without sufficient detail to confirm alignment with '{goal['goal_name']}'."
                    "\n\n### Response Format:"
                    "\n- Respond with exactly one of the following:"
                    "\n  `completed`: if the goal is explicitly and unambiguously mentioned, described, or negated."
                    "\n  `uncompleted`: if the goal is not explicitly mentioned, described, or negated, or if there is any ambiguity."
                    "\n\n### Examples:"
                    f"\n- **Example 1 (Explicit Confirmation):** {prompt_data['goal_tree_analyzer_positive_example']}"
                    f"\n  **Output:** completed"
                    f"\n- **Example 2 (Ambiguity or Irrelevance):** {prompt_data['goal_tree_analyzer_negative_example']}"
                    f"\n  **Output:** uncompleted"
                    "\n\n### Notes:"
                    "\n- Treat ambiguous, generic, or partial mentions as 'uncompleted.'"
                    "\n- Negations must explicitly and directly reference the goal to qualify as 'completed.'"
                    f"\n- Do not infer intent or meaning beyond the explicit text in {user_prompt}."
                    "\n- Output only 'completed' or 'uncompleted'—no other text or characters."
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        chain = verification_goal_status_prompt | llm
        query = chain.invoke(
            {
                "'goal_name'": goal['goal_name'],
                "messages": [HumanMessage(content=user_prompt)],
            }
        )

        responses.append(query.strip())

        # Invoking the LLM to generate infos related to the goals extracted from the user_prompt
        information_extractor_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"Your task is to identify text in {user_prompt} that mentions or refers to the goal named {goal['goal_name']}."
                    "\n\nRules:"
                    f"\n1.Consider the goal **mentioned** if it appears exactly as {goal['goal_name']}, or if its concept is expressed through synonyms, definitions, or equivalent descriptions."
                    f"\n2.Ignore content unrelated to {goal['goal_name']}. Do not consider other goals unless explicitly related."
                    "\n3.Respond with the following format:"
                    f"\n'The user wants to' followed by your output if {goal['goal_name']} is mentioned."
                    f"\n'not mentioned' if {goal['goal_name']} is not mentioned."
                    "\n4.Do **not** provide explanations or additional text."
                    f"\n\nExample: {prompt_data['goal_tree_analyzer_prompt_2']}."
                    "\n\nFollow these rules strictly for accurate output."
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        chain = information_extractor_prompt | llm
        query_informations = chain.invoke(
            {
                "'goal_name'": goal['goal_name'],
                "messages": [HumanMessage(content=user_prompt)],
            }
        )

        informations.append(query_informations)

    # Updating the goal tree with the new responses
    update_goal_tree_from_responses(goal_tree, responses, informations, [], goal_array, flag=False)

    # Evaluating and updating the status of the entire goal tree
    for goal in goal_tree['goals']:
        evaluate_goal_status(goal, goal_tree)

    tmp_list = goal_array[:] # Temporary list that allow us to iterate goal_array

    for i, response in enumerate(responses[:]):
        if response == 'completed':
            goal_array.remove(tmp_list[i])
            responses.remove(response)

    print(len(goal_array)) # Print goal_array's len for debug
    print(responses) # Print responses for debug

    return goal_array