# Business License Navigator

An AI-powered application that helps entrepreneurs navigate business license requirements using local Ollama models.

## 🚀 Streamlit Deployment

### Option 1: Deploy to Streamlit Cloud

1. **Fork this repository** to your GitHub account
2. **Go to [Streamlit Cloud](https://share.streamlit.io/)**
3. **Connect your GitHub account**
4. **Deploy the app**:
   - Repository: `your-username/MCPAgents`
   - Main file path: `BusinessLicenseNavigator/streamlit_app.py`
   - Python version: 3.11

### Option 2: Local Development

1. **Install dependencies**:
   ```bash
   cd BusinessLicenseNavigator
   pip install -r requirements.txt
   ```

2. **Install Ollama**:
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. **Pull the model**:
   ```bash
   ollama pull llama3.1:8b
   ```

4. **Start Ollama server**:
   ```bash
   ollama serve
   ```

5. **Run the Streamlit app**:
   ```bash
   streamlit run streamlit_app.py
   ```

## 📁 Project Structure

```
BusinessLicenseNavigator/
├── streamlit_app.py      # Main Streamlit app
├── agent.py             # Ollama integration
├── requirements.txt     # Dependencies
├── .streamlit/         # Streamlit config
│   └── config.toml
└── ui/                 # Alternative UI
    └── app.py
```

## 🔧 Configuration

### Streamlit Configuration
The app is configured in `.streamlit/config.toml`:
- Headless mode enabled
- CORS disabled
- Usage stats disabled

### Requirements
- Python 3.11+
- Streamlit 1.47.1+
- Requests 2.31.0+
- Ollama with llama3.1:8b model

## 🐛 Troubleshooting

### Common Issues

1. **Import Error**: Make sure you're running from the correct directory
2. **Ollama Connection Error**: Ensure Ollama server is running
3. **Model Not Found**: Pull the model with `ollama pull llama3.1:8b`

### Deployment Issues

1. **Requirements.txt**: All dependencies are listed
2. **Python Version**: Use Python 3.11 for best compatibility
3. **File Path**: Use `streamlit_app.py` as the main file

## 📝 Usage

1. Enter your business description (e.g., "I run a home bakery in Austin, TX")
2. Click "Find My License Path"
3. Get personalized guidance on licenses and permits

## 🤝 Contributing

Feel free to submit issues and enhancement requests!
