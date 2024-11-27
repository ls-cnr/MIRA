from langchain_ollama import OllamaEmbeddings
import task
import json

def embedding(file):
    # Inizializziamo il modello di Embedding
    embeddings_model = OllamaEmbeddings(model="llama3.2")
    
    # Leggiamo il file JSON
    txt = task.reading(file, "r", "", "")
    a = task.extract_json_from_text(txt)
    
    # Estraiamo i contenuti dei topic, ignorando quelli vuoti
    topics = a.get('topics', [])
    topic_contents = [topic['content'] for topic in topics if topic.get('content', '').strip()]
    
    # Generiamo gli embeddings solo per i contenuti validi
    embeddings = embeddings_model.embed_documents(topic_contents)
    
    # Salviamo i contenuti e gli embeddings in un file JSON
    embedded_data = [{"content": content, "embedding": embedding} for content, embedding in zip(topic_contents, embeddings)]
    
    with open("embedded_data.json", "w", encoding="utf-8") as f:
        json.dump(embedded_data, f, ensure_ascii=False, indent=4)