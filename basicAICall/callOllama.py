import requests


def call_ollama(model, prompt):
    """Simple function to call Ollama with a prompt"""
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"Error: {e}"


def list_models():
    """List available models"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        models = response.json()["models"]
        return [model["name"] for model in models]
    except:
        return []


if __name__ == "__main__":
    # Test the basic functionality
    print("Available models:", list_models())
    
    # Simple test
    result = call_ollama("llama3.1:8b", "What is 2+2?")
    print("Response:", result)
