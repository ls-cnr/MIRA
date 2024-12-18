## How to Use Your Custom Goal Tree

#### 1. **Load your Goal Structure in a .json file**
   Example snippet from `goal_tree_ex.json`:
   ```json
   {
     "goal_id": "course_goal",
     "goal_type": "EpistemicGoal",
     "goal_name": "Course selection",
     "description": "Does the student select the appropriate courses for their program?",
     "status": "uncompleted",
     "children": [
       {
         "goal_name": "Major-specific courses",
         "status": "uncompleted"
       },
       {
         "goal_name": "Elective courses",
         "status": "uncompleted"
       }
     ]
   }
   ```

#### 2. **Load your Prompts in another .json file**
   Example snippet from `prompts_ex.json`:
   ```json
  {
    "name": "Mira",
    "conversation_prompt": "an expert university orientation advisor",
    "language": "English",
    "query_maker_prompt": "f\" - If {goal} is 'Course selection', aim to clarify the specific courses the student needs. Ask if they have considered major courses, electives, or prerequisites.\"\n                    f\" - If {goal} is 'Accommodation arrangements', inquire whether the student prefers on-campus or off-campus housing and if they need help finding accommodation.\"\n                    f\" - If {goal} is 'Budget management', ask about the student's budget for tuition, living expenses, or miscellaneous costs. Clarify if they need estimates or advice.\"\n                    f\" - If {goal} is 'Student experience', explore the student's interest in extracurricular activities, work opportunities, or academic projects.\"\n                    f\" - If {goal} is 'Program duration', ask the student if they have a preferred timeline for completing the program. Clarify whether they are considering short, medium, or long durations.\"\n                    f\" Examples for {goal}:\"\n                    f\" - For {goal} 'Course selection', ask: 'Have you decided on the courses for your major?' or 'Do you need help choosing electives or prerequisites?'\"\n                    f\" - For {goal} 'Accommodation arrangements', ask: 'Are you looking for on-campus housing or something off-campus?' or 'Do you need help finding accommodation?'\"\n                    f\" - For {goal} 'Budget management', ask: 'What is your budget for tuition and living expenses?' or 'Do you need advice on managing university expenses?'\"\n                    f\" - For {goal} 'Student experience', ask: 'Are you interested in joining clubs, internships, or research projects?'\"\n                    f\" - For {goal} 'Program duration', ask: 'How long are you planning to take to complete your program?' or 'Are you looking for a short-term or long-term program duration?'\"\n",
    "goal_tree_analyzer_positive_example": "if user_prompt is 'I want to take courses for my major and electives.' and goal['goal_name'] is 'Course selection', the response must be 'completed'. If user_prompt is 'I need advice on choosing courses.', the response must be 'uncompleted'.",
    "goal_tree_analyzer_negative_example": "if user_prompt is 'I do not need off-campus housing.' and goal['goal_name'] is 'Off-campus accommodation', the response must be 'completed'.",
    "goal_tree_analyzer_prompt_2": "If user_prompt is 'I want to focus on my academic experience by participating in research.' and goal['goal_name'] is 'Student experience', the output must be something like 'The student is interested in academic experiences such as research.'",
    "social_practice": "Act like the personality you resemble. Furthermore, address the user politely and offer detailed advice to guide them through the university orientation process.",
    "personality": "A determined, kind woman"
  }
   ```

#### 3. **Edit the `json_name.json` file with the paths of your example**
```json
  {
    "goal_tree": "json_docs/goal_tree_ex.json",
    "prompts": "json_docs/prompts_ex.json"
  }
   ```
#### 4. **Run the `main.py` file**