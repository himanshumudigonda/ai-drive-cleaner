import json
from typing import List, Dict, Tuple
from groq import Groq

MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile"
]

def get_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)

def analyze_batch(client: Groq, batch: List[Dict], model: str) -> List[Dict]:
    """
    Send a batch of files to the AI model and return the results.
    """
    prompt = "You are an AI Drive Cleaner assistant. Your task is to analyze the following list of files found on a Windows C: drive and determine if they are safe to delete.\n"
    prompt += "Return a JSON object with a single key 'results', which contains an array of objects. Each object must have exactly three keys:\n"
    prompt += "- 'path': the exact file path provided.\n"
    prompt += "- 'verdict': one of 'SAFE_DELETE', 'REVIEW', or 'KEEP'.\n"
    prompt += "- 'reason': a one-line explanation of your verdict.\n\n"
    prompt += "Consider temporary files, cache, old logs, and crash dumps as SAFE_DELETE. If unsure, mark as REVIEW. Important files should be KEEP.\n\n"
    prompt += "Files:\n"
    
    for item in batch:
        prompt += f"- Path: {item['path']} | Size: {item['size']} bytes | Ext: {item['ext']} | Folder: {item['folder']}\n"
        
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You output strict, valid JSON ONLY. No markdown formatting."},
            {"role": "user", "content": prompt}
        ],
        model=model,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    try:
        data = json.loads(content)
        return data.get("results", [])
    except json.JSONDecodeError:
        return []

def run_ai_analysis(api_key: str, files: List[Dict]):
    """
    Run the files through the AI engine, batching them 80 at a time.
    Tries models in order of priority. Yields results back for UI updates.
    """
    client = get_client(api_key)
    
    # Try models in order
    for model in MODELS:
        try:
            active_model = model
            
            # Batch size of 20 to avoid rate limits
            batch_size = 20
            for i in range(0, len(files), batch_size):
                batch = files[i:i + batch_size]
                batch_results = analyze_batch(client, batch, model)
                yield batch_results, active_model
                
            return # Success, exit generator
        except Exception as e:
            yield [{"error": f"Model {model} failed: {e}. Trying next..."}], model
            continue
            
    raise Exception("All Groq models failed to analyze the files.")
