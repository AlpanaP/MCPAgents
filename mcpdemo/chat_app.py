"""
Simple chat example using MCPAgent with built-in conversation memory.

This example demonstrates how to use the MCPAgent with its built-in
conversation history capabilities for better contextual interactions.

Available MCP Servers:
- Playwright: Browser automation and web scraping
- Fetch: Web requests and data retrieval  
- Airbnb: Airbnb data and property information

Special thanks to https://github.com/microsoft/playwright-mcp for the server.
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from mcp_use import MCPAgent, MCPClient


async def run_memory_chat():
    """Run a chat using MCPAgent's built-in conversation memory."""
    # Load environment variables for API keys
    load_dotenv()

    # Check for required API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if len(groq_api_key) == 0:
        print("❌ Error: GROQ API key not found!")
        print("\nTo fix this:")
        print("1. Get your API key from https://console.groq.com/")
        print("2. Create a .env file in this directory with:")
        print("   GROQ_API_KEY=your_actual_api_key_here")
        print("\nExample .env file content:")
        print("GROQ_API_KEY=gsk_your_actual_key_here")
        return

    # Config file path - change this to your config file
    config_file = "./browser_mcp.json"

    print("Initializing chat with MCP servers...")
    print("Available servers: Playwright (browser automation), Fetch (web requests), Airbnb (property data)")

    # Create MCP client and agent with memory enabled
    client = MCPClient.from_config_file(config_file)
    llm = ChatGroq(model="llama-3.3-70b-versatile")

    # Structured prompt for consistent response format
    structured_prompt = """You are a helpful AI assistant with access to various MCP (Model Context Protocol) servers. You MUST use these tools when appropriate to provide current, accurate information.

AVAILABLE TOOLS:
1. **Playwright Server** - Browser automation, web scraping, taking screenshots, filling forms
2. **Fetch Server** - Web requests, data retrieval, API calls
3. **Airbnb Server** - Search for Airbnb properties, get property details, pricing information

CRITICAL INSTRUCTION: You have access to powerful tools. You MUST use them when users ask for:
- Current information, prices, or availability
- Hotel recommendations or travel information
- Real-time data or recent events
- Property searches or accommodation details
- Web searches for current information

DO NOT rely on your training data for current information. Use the tools instead.

IMPORTANT RULES:
- ALWAYS use tools when searching for current information, prices, availability, or real-time data
- Use Fetch server for general web searches and information gathering
- Use Playwright server for complex web interactions, screenshots, or when you need to interact with websites
- Use Airbnb server specifically for property searches, hotel information, and accommodation details
- Only respond from your knowledge when the question is about general concepts, definitions, or historical information
- For questions about current events, prices, availability, or specific data, ALWAYS use the appropriate tool

IMPORTANT: Always format your responses using the following structure:

## Summary
[Provide a brief 1-2 sentence summary of what you accomplished or found]

## Topic
[State the main topic or question being addressed]

## Result
[Provide the detailed findings, information, or solution. This should be the main content of your response]

## Tool Used
[List the specific MCP servers you used, if any. Examples: 
- "Playwright server - browser automation and web scraping"
- "Fetch server - web requests and data retrieval" 
- "Airbnb server - property search and data"
- "No tools used - provided information from knowledge"]

EXAMPLES OF WHEN TO USE TOOLS:
- "Best hotels in Costa Rica" → Use Fetch server to search for current hotel information
- "Current weather in New York" → Use Fetch server to get real-time weather data
- "Airbnb properties in Paris" → Use Airbnb server for property search
- "Take a screenshot of google.com" → Use Playwright server for browser automation
- "What is Python programming?" → Use knowledge (no tools needed for general concepts)

Remember: When in doubt, use tools to get current, accurate information rather than relying on potentially outdated knowledge."""

    # Create agent with memory_enabled=True and custom prompt
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True,  # Enable built-in conversation memory
        system_prompt=structured_prompt,
        verbose=True,  # Enable verbose logging to see tool usage
    )

    print("\n===== Interactive MCP Chat =====")
    print("Type 'exit' or 'quit' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("Type 'servers' to see available MCP servers")
    print("==================================\n")

    try:
        # Main chat loop
        while True:
            # Get user input
            user_input = input("\nYou: ")

            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                print("Ending conversation...")
                break

            # Check for clear history command
            if user_input.lower() == "clear":
                agent.clear_conversation_history()
                print("Conversation history cleared.")
                continue

            # Check for servers command
            if user_input.lower() == "servers":
                print("\nAvailable MCP Servers:")
                print("1. Playwright - Browser automation and web scraping")
                print("2. Fetch - Web requests and data retrieval")
                print("3. Airbnb - Property search and data")
                continue

            # Get response from agent
            print("\nAssistant: ", end="", flush=True)

            try:
                # Run the agent with the user input (memory handling is automatic)
                response = await agent.run(user_input)
                print(response)

            except Exception as e:
                print(f"\nError: {e}")

    finally:
        # Clean up
        if client and client.sessions:
            await client.close_all_sessions()


if __name__ == "__main__":
    asyncio.run(run_memory_chat())