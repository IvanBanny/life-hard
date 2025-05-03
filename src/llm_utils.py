import requests

def generate_response(prompt: str) -> str:
    """Send a prompt to ollama and receive a response."""
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "gemma3:1b",
            "prompt": prompt,
            "stream": False
        }, timeout=240)  # Timeout after 240 seconds
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json().get("response")
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while calling LLM API: {e}")
        return None
