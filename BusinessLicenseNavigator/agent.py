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


def run_agent(user_input):
    """Run the business license navigator agent"""
    
    # Create a prompt for business license guidance
    prompt = f"""
    You are a helpful business license navigator. A user has provided the following information about their business:
    
    {user_input}
    
    Please provide guidance on:
    1. What type of business license they might need
    2. Any specific permits required
    3. Steps they should take to obtain the necessary licenses
    4. Any additional considerations for their business type and location
    
    Be helpful, specific, and provide actionable advice.
    """
    
    # Call Ollama with the prompt
    response = call_ollama("llama3.1:8b", prompt)
    
    return response


if __name__ == "__main__":
    # Test the agent
    test_input = "I run a home bakery in Austin, TX"
    result = run_agent(test_input)
    print("Test result:")
    print(result) 