from callOllama import call_ollama, list_models


def main():
    print("Hello from basicaicall!")
    
    # Simple test
    print("\n--- Basic Ollama Test ---")
    
    # List available models
    models = list_models()
    print("Available models:", models)
    
    # Call Ollama
    response = call_ollama("llama3.1:8b", "What is 2+2?")
    print("Response:", response)


if __name__ == "__main__":
    main()
