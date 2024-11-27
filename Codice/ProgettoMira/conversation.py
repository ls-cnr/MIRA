from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from Goal_Tree_Analyzer import *
from userPromptToJson import *
from finalEvaluation import *

# Definizione del LLM
llm = ChatOllama(model="llama3.2")

# Gestione della cronologia dei messaggi
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Configurazione di sessione
config = {"configurable": {"session_id": "sessione_ragionamento"}}

# Inizio della conversazione
while True:
    messaggio = input("\nChiedimi ciò che vuoi:\n")
    if messaggio == "chiudi":
        break

    chat_prompt_with_cot = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert travel agent."
                f"Your task is to analyze {messaggio}, understand the user's travel requests, and provide the best response based on these.",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    chain = chat_prompt_with_cot | llm

    # Creazione dell'istanza `RunnableWithMessageHistory` per mantenere la cronologia
    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="messages",
    )

    # Applicazione del ragionamento e stampa della risposta
    risposta = with_message_history.invoke(
        {
            "query": messaggio,
            "messages": [HumanMessage(content=messaggio)],
        },
        config=config,
    )

    question = query_maker(messaggio, goal())

    # Scelta del pensiero migliore sulla base della 'finalEvaluation'
    finalThought = finalEvaluation(toJson(messaggio), messaggio, risposta.content, question)

    # Stampa del contenuto della risposta
    if isinstance(finalThought, str):
        print(finalThought)
    else:
        print("Tipo di risposta inaspettato:", type(finalThought))