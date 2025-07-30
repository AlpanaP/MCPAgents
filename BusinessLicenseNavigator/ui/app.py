# ui/app.py
import streamlit as st
import sys
import os

# Add the parent directory to the path so we can import agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import run_agent

st.title("Business License Navigator")

st.markdown("Enter a brief description of your business and where it's located.")

user_input = st.text_area("Business Description", placeholder="e.g., I run a home bakery in Austin, TX")

if st.button("Find My License Path"):
    with st.spinner("Consulting agent..."):
        try:
            response = run_agent(user_input)
            st.success("Done!")
            st.write(response)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Make sure Ollama is running locally with llama3.1:8b model")
