from scipy.spatial.distance import cosine
import numpy as np
from sklearn.preprocessing import normalize
from embedding import *
import json

# Funzione per normalizzare gli embedding (normalizzazione L2)
def normalize_embedding(embedding):
    return normalize([embedding])[0]

# Funzione per calcolare la similarità coseno con controllo per vettori nulli
def cosine_similarity(embedding1, embedding2):
    # Verifica se uno dei vettori è nullo (tutti gli elementi sono zero)
    if np.all(embedding1 == 0) or np.all(embedding2 == 0):
        return 0.0  # Similarità coseno per vettori nulli è 0

    return 1 - cosine(embedding1, embedding2)


def finalEvaluation(file, messaggio, reactive_query, proactive_query):
    # Inizializziamo il modello di embeddings
    embeddings_model = OllamaEmbeddings(model="llama3.2")

    # Creiamo gli embeddings per il file (normalizzati)
    embedding(file)

    # Carichiamo gli embeddings salvati
    with open("embedded_data.json", "r", encoding="utf-8") as f:
        embedded_data = json.load(f)

    # Estraiamo contenuti ed embeddings dai dati caricati
    documents = [
        {"content": data["content"], "embedding": normalize_embedding(data["embedding"])}
        for data in embedded_data
    ]

    # Lista per accumulare tutti i risultati
    all_results = []

    # Normalizzazione dei query
    reactive_query_embedding = normalize_embedding(embeddings_model.embed_query(reactive_query))
    messaggio_embedding = normalize_embedding(embeddings_model.embed_query(messaggio))

    # Fase 'Reactive Thought': calcolo della similarità coseno tra query1 e messaggio
    similarity_score = cosine_similarity(reactive_query_embedding, messaggio_embedding)
    all_results.append({
        "content": messaggio,
        "metadata": f"Reactive: {reactive_query}",
        "similarity_score": similarity_score
    })

    # Troviamo la query con il punteggio massimo
    max_result = (similarity_score, reactive_query)

    # Fase 'Proactive Thought': calcolo della similarità coseno per ogni query2
    for e in proactive_query:
        proactive_query_embedding = normalize_embedding(embeddings_model.embed_query(e))

        # Calcoliamo la similarità coseno per ogni documento
        for doc in documents:
            doc_embedding = doc["embedding"]
            doc_similarity = cosine_similarity(proactive_query_embedding, doc_embedding)

            all_results.append({
                "content": doc["content"],
                "metadata": f"Proactive: {e}",
                "similarity_score": doc_similarity
            })

            # Aggiorniamo il miglior risultato
            if doc_similarity > max_result[0]:
                max_result = (doc_similarity, e)

    # Salviamo tutti i risultati in un file JSON
    with open("vector_data.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)

    return max_result[1]