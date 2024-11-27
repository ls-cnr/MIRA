from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Definizione del modello
llm = ChatOllama(model="llama3.2")

def query_maker(messaggio, arr):
    responses = []

    # Esegue il ciclo per ottenere le risposte
    for elemento in arr:
        chat_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"Carefully analyze the user's input ({messaggio}) and focus on identifying the specific request related to {elemento}."
                    f" Your primary objective is to gather detailed information about the {elemento}."
                    f" Based on the content of the user's message, you should choose one of the following approaches:"
                    f" 1) Answer the user's potential question related to {elemento},"
                    f" 2) Ask the user a clarifying question to better understand the {elemento},"
                    f" 3) Provide a hybrid response combining both a question and an answer to guide the user in revealing more details about the {elemento}."
                    f" Your response should always be directly relevant to {elemento} and must not stray from this focus."
                    f" Specific guidelines:"
                    f" - If {elemento} is 'location', aim to clarify the exact destination the user has in mind. Ask for specific details such as city, country, or region."
                    f" - If {elemento} is 'budget', inquire about the user's budget range for the trip. Ask for an estimated amount or range they are willing to spend."
                    f" - If {elemento} is 'experience', probe to uncover what kind of activities the user is looking for, such as adventure sports (e.g., hiking, snorkeling, skiing), cultural experiences, or relaxation."
                    f" - If {elemento} is 'duration', clarify the length of the trip the user is planning. Ask how many days or weeks they intend to travel."
                    f" Examples for {elemento}:"
                    f" - For {elemento} 'location', ask: 'Where would you like to go?' or 'Which destination are you considering?'"
                    f" - For {elemento} 'budget', ask: 'What is your budget range for this trip?' or 'How much would you like to spend on this trip?'"
                    f" - For {elemento} 'experience', ask: 'What kind of activities or experiences are you interested in?' or 'Are you looking for something more adventurous, like hiking or diving?'"
                    f" - For {elemento} 'duration', ask: 'How long would you like your trip to be?' or 'What is the duration you are thinking of for your trip?'"
                    f" Only provide responses that are related to the {elemento}, and ensure you don’t introduce irrelevant information."
                    f" For 'experience', only respond if the message explicitly mentions activities like excursions, water sports, or similar experiences."
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        chain = chat_prompt | llm

        query = chain.invoke(
            {
                "arr": elemento,
                "query": messaggio,
                "messages": [HumanMessage(content=messaggio)],
            }
        )

        responses.append(query.content)

    # Scriviamo tutte le risposte nel file JSON
    result_list = []  # Crea una lista per raccogliere i risultati
    res = []
    for i, e in zip(arr, responses):  # Itera su arr e responses contemporaneamente
        result = {
            "content": i,  # La risposta
            "metadata": e  # Il goal_id corrispondente
        }
        result_list.append(result)
        res.append(e)

    # Scriviamo tutti i risultati nel file JSON, una sola volta
    with open("response.json", "w", encoding="utf-8") as f:
        json.dump(result_list, f, ensure_ascii=False, indent=4)

    return res