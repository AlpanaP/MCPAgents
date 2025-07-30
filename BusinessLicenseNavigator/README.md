# Business License Navigator

An AI-powered application that helps entrepreneurs navigate business license requirements using Google's Gemini AI or local Ollama models.

## 🚀 Streamlit Deployment

### Option 1: Deploy to Streamlit Cloud (Recommended)

1. **Fork this repository** to your GitHub account
2. **Get a Gemini API key** from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **Go to [Streamlit Cloud](https://share.streamlit.io/)**
4. **Connect your GitHub account**
5. **Deploy the app**:
   - Repository: `your-username/MCPAgents`
   - Main file path: `BusinessLicenseNavigator/streamlit_app.py`
   - Python version: 3.11
6. **Add environment variable**:
   - Key: `GEMINI_API_KEY`
   - Value: Your Gemini API key

### Option 2: Local Development

1. **Install dependencies**:
   ```bash
   cd BusinessLicenseNavigator
   pip install -r requirements.txt
   ```

2. **Set up Gemini AI (Recommended)**:
   ```bash
   # Get API key from https://makersuite.google.com/app/apikey
   export GEMINI_API_KEY=your_key_here
   streamlit run streamlit_app.py
   ```

3. **Or set up Ollama (Local only)**:
   ```bash
   # Install Ollama
   brew install ollama  # macOS
   # OR
   curl -fsSL https://ollama.ai/install.sh | sh  # Linux
   
   # Pull the model
   ollama pull llama3.1:8b
   
   # Start Ollama server
   ollama serve
   
   # Run the app
   streamlit run streamlit_app.py
   ```

## 📁 Project Structure

```
BusinessLicenseNavigator/
├── streamlit_app.py      # Main Streamlit app
├── agent.py             # AI integration (Gemini + Ollama)
├── requirements.txt     # Dependencies
├── .streamlit/         # Streamlit config
│   └── config.toml
└── ui/                 # Alternative UI
    └── app.py
```

## 🔧 Configuration

### AI Options

1. **Gemini AI (Recommended)**
   - Works in cloud deployment
   - Powered by Google's Gemini 1.5 Flash
   - Requires API key from Google AI Studio
   - Free tier available

2. **Local Ollama**
   - Works locally only
   - Uses llama3.1:8b model
   - No API key required
   - Requires local Ollama installation

3. **Fallback Mode**
   - No AI required
   - Rule-based guidance
   - Always available

### Streamlit Configuration
The app is configured in `.streamlit/config.toml`:
- Headless mode enabled
- CORS disabled
- Usage stats disabled

### Requirements
- Python 3.11+
- Streamlit 1.47.1+
- Requests 2.31.0+
- Google Generative AI 0.3.0+
- Gemini API key (for AI features)

## 🐛 Troubleshooting

### Common Issues

1. **Gemini API Error**: Check your API key and quota
2. **Ollama Connection Error**: Ensure Ollama server is running
3. **Import Error**: Make sure you're running from the correct directory

### Deployment Issues

1. **Requirements.txt**: All dependencies are listed
2. **Python Version**: Use Python 3.11 for best compatibility
3. **File Path**: Use `streamlit_app.py` as the main file
4. **Environment Variables**: Set `GEMINI_API_KEY` in Streamlit Cloud

## 📝 Usage

1. **Set up AI** (optional):
   - Get Gemini API key from Google AI Studio
   - Or install Ollama locally
   
2. **Use the app**:
   - Enter your business description
   - Click "Find My License Path"
   - Get personalized guidance

3. **Get guidance**:
   - AI-powered responses (with Gemini/Ollama)
   - Fallback guidance (without AI)
   - Always verify with local authorities

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 🔗 Links

- [Google AI Studio](https://makersuite.google.com/app/apikey) - Get Gemini API key
- [Ollama](https://ollama.ai/) - Local AI models
- [Streamlit Cloud](https://share.streamlit.io/) - Deploy your app
