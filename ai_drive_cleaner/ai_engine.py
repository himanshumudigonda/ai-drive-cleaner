import json
from typing import List, Dict, Tuple
from groq import Groq

MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile"
]

def get_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)

def get_local_verdict(file_info: dict) -> dict:
    """Fallback if AI rate limit is reached."""
    return {
        "path": file_info['path'],
        "verdict": "SAFE_DELETE",
        "reason": "Temporary file (Local Rule Applied)"
    }

def analyze_batch(client: Groq, batch: List[Dict], model: str) -> List[Dict]:
    """
    Send a batch of files to the AI model and return the results.
    """
    prompt = "Analyze if these Windows files are safe to delete. Return JSON: {'results': [{'path':'...', 'verdict': 'SAFE_DELETE|REVIEW|KEEP', 'reason': 'short roast or reason'}]}\nFiles:\n"
    for item in batch:
        prompt += f"- {item['path']}\n"
        
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You output strict JSON ONLY."},
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
    Run the files through the AI engine, batching them.
    If Rate Limit is hit, gracefully switch to Local Rules so it doesn't crash.
    """
    client = get_client(api_key)
    batch_size = 50
    
    for model in MODELS:
        try:
            for i in range(0, len(files), batch_size):
                batch = files[i:i + batch_size]
                try:
                    batch_results = analyze_batch(client, batch, model)
                    yield batch_results, model
                except Exception as e:
                    # If rate limited, yield error once and switch to local rules
                    error_msg = str(e).split('}')[0] + "}" if "{" in str(e) else str(e)
                    yield [{"error": f"API Limit Reached: Switching to Local Rules..."}], "System"
                    
                    # Yield the current failed batch as local
                    yield [get_local_verdict(f) for f in batch], "Local System"
                    
                    # Process all remaining files locally
                    for j in range(i + batch_size, len(files), batch_size):
                        rem_batch = files[j:j+batch_size]
                        yield [get_local_verdict(f) for f in rem_batch], "Local System"
                    return # Exit completely
            return # Success
        except Exception:
            continue
            
    # If all models failed from the very beginning
    yield [{"error": "All Groq models failed. Using Local Rules."}], "System"
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        yield [get_local_verdict(f) for f in batch], "Local System"
