from jsonschema import validate, ValidationError
import json

def extract_json_from_text(text):
    """
    Estrae la prima struttura JSON valida dal testo.
    Gestisce sia JSON su singola riga che su più righe.
    """
    def find_matching_bracket(s, start):
        """Trova la graffa chiusa corrispondente"""
        count = 1
        pos = start
        while count > 0 and pos < len(s):
            if s[pos] == '{':
                count += 1
            elif s[pos] == '}':
                count -= 1
            pos += 1
        return pos if count == 0 else -1

    try:
        #print("extracting JSON from: ",text)
        # Prima prova: cerca di parsare direttamente il testo come JSON
        return json.loads(text)
    except json.JSONDecodeError:

        # Seconda prova: cerca oggetti JSON nel testo
        pos = 0
        while True:
            # Trova la prossima graffa aperta
            start = text.find('{', pos)
            if start == -1:
                break

            # Trova la graffa chiusa corrispondente
            end = find_matching_bracket(text, start + 1)
            if end == -1:
                pos = start + 1
                continue

            # Prova a parsare questo sottotesto
            try:
                json_str = text[start:end]
                return json.loads(json_str)
            except json.JSONDecodeError:
                pos = start + 1
                continue

        # Terza prova: cerca di estrarre tutto ciò che è tra la prima graffa aperta
        # e l'ultima graffa chiusa
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > 0:
                json_str = text[start:end]
                return json.loads(json_str)
        except:
            pass

        raise ValueError("No valid JSON object found in text")

def validate_json_schema(data, schema):
    """
    Valida un JSON contro uno schema

    Args:
        data: il JSON da validare
        schema: lo schema JSON contro cui validare
    """
    try:
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)

def safe_json_extraction(max_retries=3, schema=None):
    """
    Decorator per gestire in modo sicuro l'estrazione e validazione del JSON
    dalle risposte LLM, con tentativi multipli in caso di errore

    Args:
        max_retries: numero massimo di tentativi
        schema: schema JSON da usare per la validazione
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if schema is None:
                raise ValueError("Schema must be provided")

            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    # Se la funzione restituisce già un dict, validiamo direttamente
                    if isinstance(result, dict):
                        json_data = result
                    else:
                        # Altrimenti, proviamo a estrarre e parsare il JSON
                        json_data = extract_json_from_text(result)

                    # Valida il JSON contro lo schema
                    is_valid, error = validate_json_schema(json_data, schema)
                    if is_valid:
                        return json_data
                    else:
                        #print(f"Invalid JSON structure: {error}")
                        #print(f"Received: {json_data}")
                        raise ValidationError(f"JSON schema validation failed: {error}")

                except Exception as e:
                    if attempt < max_retries - 1:
                        #print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                        continue
                    else:
                        #print(f"All {max_retries} attempts failed. Last error: {str(e)}")
                        raise

        return wrapper
    return decorator
