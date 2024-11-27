import json
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from cot_utils import safe_json_extraction

def toJson(msg):
    # Schema definitions
    ANALYZE_GOAL_MODEL_SCHEMA = {
        "type": "object",
        "required": ["topics"],
        "properties": {
            "topics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["topic_name", "content"],
                    "properties": {
                        "topic_name": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "additionalProperties": False
                }
            }
        },
        "additionalProperties": False
    }

    @safe_json_extraction(max_retries=3, schema=ANALYZE_GOAL_MODEL_SCHEMA)
    def analyze_user_prompt(user_prompt, model):
        """Analyze the user prompt and extract topics"""

        llm = OllamaLLM(
            model = model,
            temperature=0.1,  # Bassa temperatura per risposte più deterministiche
            repeat_penalty=1.2,  # Riduce le ripetizioni
            top_p=0.9,  # Mantiene una buona diversità preservando la coerenza
            num_ctx=4096,  # Contesto ampio per gestire interviste lunghe
            #reset=True, # Reset del contesto
            #seed=42 # Per risultati riproducibili
        )

        template = (
            "IMPORTANT: This is a new conversation. Ignore all previous context and history.\n\n"
            "You are an expert travel agent responsible for analyzing the following user prompt.\n\n"
            "{user_prompt}\n\n"
            "Your goal is to identify and separate references to the following specific topics in the user's prompt: 'Location,' 'Budget,' 'Experience,' and 'Duration'.\n"
            "Please break the prompt into these four distinct topics. For each topic, transcribe the exact text segment that refers to it without summarizing or paraphrasing.\n"
            "For, and only, the budget information, transcribe only the budget information, without adding unnecessary information.\n"
            "If a segment relates to more than one topic, break it down into more specific sub-topics, ensuring that each segment is categorized appropriately.\n"
            "IMPORTANT NOTE: If a location is mentioned in the context of something that the user **does not** want (e.g., 'I do not want to go to Paris'), do **not** include it as part of the 'Location' topic. Only include locations the user wants to visit.\n\n"
            "Instructions:\n"
            "1. Identify and extract text segments that correspond to each of the four topics: 'Location,' 'Budget,' 'Experience,' and 'Duration'.\n"
            "2. For each identified topic, provide the unaltered text segment.\n"
            "3. If a text segment belongs to multiple topics, split it into specific sub-topics, each with a unique reference.\n"
            "4. Do not summarize or paraphrase the text; transcribe it exactly as it appears in the user prompt.\n"
            "5. If a location is mentioned in a context that expresses a negative preference (e.g., 'I do not want to go to [Location]'), do **not** include that location under the 'Location' topic.\n\n"
            "Provide the output in the following JSON format:\n"
            "{{\n"
            "  \"topics\": [\n"
            "    {{\n"
            "      \"topic_name\": \"Location\", \n"
            "      \"content\": \"Exact text segment related to Location\",\n"
            "    }},\n"
            "    {{\n"
            "      \"topic_name\": \"Budget\",\n"
            "      \"content\": \"Exact text segment related to Budget\",\n"
            "    }},\n"
            "    {{\n"
            "      \"topic_name\": \"Experience\",\n"
            "      \"content\": \"Exact text segment related to Experience\",\n"
            "    }},\n"
            "    {{\n"
            "      \"topic_name\": \"Duration\",\n"
            "      \"content\": \"Exact text segment related to Duration\",\n"
            "    }}\n"
            "  ]\n"
            "}}\n\n"
        )

        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm | StrOutputParser()

        return chain.invoke({
            "user_prompt": user_prompt,
        })

    user_prompt_name = msg

    model_name = "llama3.2"

    # Analyze the interview
    result = analyze_user_prompt(user_prompt_name, model_name)

    # Save the result as a JSON file with UTF-8 encoding
    output_file = "user_prompt_analysis_output.json"
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)

    return output_file