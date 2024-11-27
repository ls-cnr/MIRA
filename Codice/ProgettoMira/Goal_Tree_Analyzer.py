from queryMaker import *

#WIP
def goal():
    arr = []
    def load_goal_tree(file_path):
        with open(file_path, 'r') as file:
            goal_tree = json.load(file)
        return goal_tree

    def load_id(goal_tree):
        def recursive_filter(goal):
            if 'goal' in goal['goal_id']:
                arr.append(goal['goal_id'])
            if 'children' in goal:
                for child in goal['children']:
                    recursive_filter(child)

        for goal in goal_tree['goals']:
            recursive_filter(goal)

    goal_tree = load_goal_tree('goal_tree.json')
    load_id(goal_tree)
    return arr