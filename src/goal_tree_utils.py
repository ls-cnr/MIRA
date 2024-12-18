import json

# Importing goal_tree and prompts
with open("json_docs/json_name.json", "r", encoding="utf-8") as f:
    json_name = json.load(f)

# Loading the goal tree
def load_goal_tree(file_path):
    with open(file_path, 'r') as file:
        goal_tree = json.load(file)
    return goal_tree

def set_goal_uncompleted(goal_tree_path):
    # Invoking 'load_goal_tree' to load the goal tree
    goal_tree = load_goal_tree(goal_tree_path)
    if goal_tree is None:
        print("Error: goal_tree is empty or invalid. Aborting operation.")
        return

    # Recursive function that initialize the 'status' field of goals and sub-goals
    def update_goal_status_uncompleted(goal):
        if goal['status'] == 'completed':
            print(f"Changing goal status from '{goal['goal_name']}' to 'uncompleted'.")
            goal['status'] = 'uncompleted'

        # If the goal has children (sub-goals), recursively apply the function to them
        if 'children' in goal and goal['children']:
            for child in goal['children']:
                update_goal_status_uncompleted(child)

    # Recursive function that initialize the 'information' field of goals and sub-goals
    def update_goal_information_uncompleted(goal):
        if goal['information'] != "":
            print(f"Changing goal information from '{goal['information']}' to ''.")
            goal['information'] = ""

        # If the goal has children (sub-goals), recursively apply the function to them
        if 'children' in goal and goal['children']:
            for child in goal['children']:
                update_goal_information_uncompleted(child)

    # Recursive function that initialize the 'score' field of goals and sub-goals
    def update_goal_score_uncompleted(goal):
        if goal['score'] != "":
            print(f"Changing goal score from '{goal['score']}' to ''.")
            goal['score'] = ""

        # If the goal has children (sub-goals), recursively apply the function to them
        if 'children' in goal and goal['children']:
            for child in goal['children']:
                update_goal_score_uncompleted(child)

    # Applying the recursive function to all the main goals
    for root_goal in goal_tree['goals']:
        update_goal_status_uncompleted(root_goal)
        update_goal_information_uncompleted(root_goal)
        update_goal_score_uncompleted(root_goal)

    # Saving into 'goal_tree.json'
    with open(goal_tree_path, 'w', encoding="utf-8") as file:
        json.dump(goal_tree, file, indent=2, ensure_ascii=False)
        print(f"File '{goal_tree_path}' updated.")

# Function that updates the goal tree based on the LLM's responses
def update_goal_tree_from_responses(goal_tree, responses, informations, priorities, goal_array, flag):
    # Funzione per aggiornare lo stato dei goal
    def update_goal_status_completed(goal):
        for i, response in enumerate(responses):
            goal_name = goal_array[i]['goal_name']
            if goal['goal_name'] == goal_name:
                print(f"Updating goal: {goal['goal_name']} to {response}")
                goal['status'] = "completed" if response == "completed" else "uncompleted"
        if 'children' in goal and goal['children']:
            for child in goal['children']:
                update_goal_status_completed(child)

    # Funzione per aggiornare le informazioni dei goal
    def update_goal_information(goal):
        for i, information in enumerate(informations):
            goal_name = goal_array[i]['goal_name']
            if goal['goal_name'] == goal_name:
                print(f"Updating goal information: {information}")
                goal['information'] = information
        if 'children' in goal and goal['children']:
            for child in goal['children']:
                update_goal_information(child)

    # Funzione per aggiornare le priorità dei goal
    def update_goal_score(goal):
        for i, score in enumerate(priorities):
            goal_name = goal_array[i]['goal_name']
            if goal['goal_name'] == goal_name:
                print(f"Updating goal score: {score}")
                goal['score'] = score
        if 'children' in goal and goal['children']:
            for child in goal['children']:
                update_goal_score(child)

    # Applica le modifiche in base al flag
    for root_goal in goal_tree['goals']:
        if not flag:  # Aggiorna stato e informazioni
            update_goal_status_completed(root_goal)
            update_goal_information(root_goal)
        else:  # Aggiorna priorità
            update_goal_score(root_goal)

    # Salva il file aggiornato
    with open(json_name["goal_tree"], 'w', encoding="utf-8") as file:
        json.dump(goal_tree, file, indent=2, ensure_ascii=False)
        print("File goal_tree.json updated successfully.\n")

def evaluate_goal_status(goal, goal_tree):
    children = goal.get("children", [])

    print(f"\nEvaluating Goal: {goal['goal_name']} (Current status: {goal['status']})")

    # Evaluating all children recursively
    for child in children:
        evaluate_goal_status(child, goal_tree)

    if not children:
        # If no children, the goal's status does not depend on sub-goals
        print(f"Goal '{goal['goal_name']}' has no children. Skipping evaluation.")
        return

    # Determining the status of the parent based on the children's links
    child_statuses = [child["status"] for child in children]
    child_links = [child.get("goal_link", "AND") for child in children]  # Default link is AND

    print(f"Child statuses for '{goal['goal_name']}': {child_statuses}")
    print(f"Child links for '{goal['goal_name']}': {child_links}")

    # Logic to determine the parent's status based on the children's links
    if "OR" in child_links:
        # If any child with OR is completed, the parent is completed
        goal["status"] = "completed" if any(child["status"] == "completed" for child in children) else "uncompleted"
    else:
        # All children must be completed for the parent to be completed
        goal["status"] = "completed" if all(child["status"] == "completed" for child in children) else "uncompleted"

    print(f"Updated status for '{goal['goal_name']}': {goal['status']}")

    # Special case for the root goal
    if goal.get("goal_id") == "root":
        root_child_statuses = [child["status"] for child in children]
        goal["status"] = "completed" if all(status == "completed" for status in root_child_statuses) else "uncompleted"
        print(f"Root goal '{goal['goal_name']}' evaluated: {goal['status']}")
        if goal["status"] == "completed":
            print("Booking the travel, have a nice journey! :)")

    with open(json_name["goal_tree"], 'w', encoding="utf-8") as file:
        json.dump(goal_tree, file, indent=2, ensure_ascii=False)
        print("File goal_tree.json updated successfully.\n")

# Module that set a flag to True if 'root_goal' is satisfied
def set_flag():
    goal_tree = load_goal_tree(json_name["goal_tree"])

    goal = goal_tree['goals'][0]

    if goal.get("goal_id") == "root":
        if goal["status"] == "completed":
            return True
        else:
            return False