# 🇩🇪 German Translation Game

An interactive German language learning application built with Streamlit and powered by the cutting-edge [Datapizza-AI](https://github.com/datapizza-labs/datapizza-ai) framework. Practice translating German sentences to English (and vice versa) with AI-powered feedback and intelligent hint systems.

## 🎮 What It Does

This application provides an engaging way to learn German through interactive translation exercises:

- **Translation Practice**: Translate German sentences to English or English to German
- **AI-Powered Feedback**: Get intelligent validation of your translations using advanced language models
- **Progressive Hints**: Receive contextual hints that guide you toward the correct answer
- **Difficulty Levels**: Practice with sentences ranging from beginner (level 1) to advanced (level 5)
- **Multiple Verb Tenses**: Practice with Präsens, Präteritum, Perfekt, Konjunktiv II, and Futur
- **Score Tracking**: Monitor your progress with accuracy statistics

## 🏗️ How It Works

The application leverages the modern **Datapizza-AI framework** to provide a seamless AI experience:

1. **Structured AI Responses**: Uses Pydantic models to ensure consistent, reliable AI responses
2. **Multi-Provider Support**: Works with both local Ollama models and cloud-based Google Gemini
3. **Intelligent Validation**: AI validates translations by comparing meaning, grammar, and context
4. **Dynamic Content Generation**: Creates contextual German sentences based on verb frequency and difficulty
5. **Smart Hint System**: Provides progressive hints without additional AI calls for optimal performance

The architecture follows a clean separation of concerns:
- **Streamlit Frontend**: Interactive web interface
- **Game Logic**: Manages game state, scoring, and user interactions  
- **Datapizza-AI Integration**: Handles all AI communication with structured responses
- **Data Layer**: Loads German verbs from CSV with frequency-based difficulty

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Gemini API key (optional - for cloud AI models)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd german-ai-chatbot
   ```

2. **Set up environment variables (optional)**
   Create a `.env` file in the project root:
   ```bash
   # For Google Gemini (optional - only if you want to use cloud AI)
   GEMINI_KEY=your_google_gemini_api_key_here
   ```

3. **Start Ollama and download model (if using local AI)**
   ```bash
   # Install Ollama from https://ollama.ai/ if not already installed
   # Start Ollama server
   ollama serve
   
   # In another terminal, download the recommended model
   ollama pull gemma3:4b
   ```

4. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Open your browser**
   Navigate to `http://localhost:8505`

That's it! The application will be running in a container with all dependencies pre-installed.

### Alternative: Manual Setup (Advanced)

If you prefer to run locally without Docker:

1. **Prerequisites**: Python 3.8+, [Ollama](https://ollama.ai/) (for local AI models)
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Start Ollama**: `ollama serve`
4. **Run app**: `streamlit run app.py`
5. **Open**: `http://localhost:8501`

## ⚙️ Configuration

### Environment Variables (.env)

The `.env` file is optional and only needed if you want to use Google Gemini instead of local Ollama models:

```bash
# Google Gemini API Key (optional)
GEMINI_KEY=your_actual_api_key_here
```

**Note**: 
- If you don't provide a `GEMINI_KEY`, the application will default to using Ollama with local models
- The Docker setup automatically mounts your `.env` file into the container
- The app runs on port 8505 (mapped from container port 8501)

### AI Provider Options

**Local (Ollama)** - Default, no API key required:
- `gemma3:4b` - Fast, lightweight model (preferred)
- `gemma3:12b` - More capable, larger model  
- `deepseek-r1:8b` - Advanced reasoning model
- `llama3.2` - Meta's latest model

**Cloud (Google Gemini)** - Requires API key:
- `gemini-2.5-flash` - Fast and efficient
- `gemini-2.0-flash` - Balanced performance
- `gemini-2.0-flash-lite` - Ultra-fast responses (preferred)

## 🎯 Usage

1. **Configure Settings**: Choose your difficulty level (1-5), verb tense, and AI provider
2. **Start Game**: Click "Start New Game" to begin
3. **Translate**: Type your translation in the input field
4. **Get Feedback**: Receive immediate AI-powered validation
5. **Use Hints**: Click "Get Hint" for progressive assistance
6. **Track Progress**: Monitor your accuracy in the sidebar

## 📁 Project Structure

```
├── app.py                          # Streamlit main application
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (optional)
├── data/                          # German language data
│   ├── verbi.csv                  # German verbs with frequency data
│   ├── nomi.csv                   # German nouns
│   └── aggettivi.csv              # German adjectives
└── src/
    ├── ai/                        # AI integration layer
    │   ├── api.py                 # Abstract AI interface
    │   └── datapizza_api.py       # Datapizza-AI implementation
    ├── functionalities/          # Game logic
    │   ├── base.py                # Base functionality class
    │   ├── translation_game.py     # German→English game
    │   └── inverse_translation_game.py # English→German game
    ├── data/                      # Data processing
    │   └── verb_loader.py         # CSV data loader
    └── utils/                     # Utility functions
        └── text_diff.py           # Text comparison utilities
```

## 🔧 Technology Stack

- **Frontend**: Streamlit for interactive web interface
- **AI Framework**: [Datapizza-AI](https://github.com/datapizza-labs/datapizza-ai) for structured AI responses
- **AI Models**: Ollama (local) + Google Gemini (cloud)
- **Data Processing**: Pandas for CSV handling
- **Validation**: Pydantic for structured data validation
- **Language Data**: Custom German verb/noun/adjective datasets

## 🤝 Contributing

Contributions are welcome! Whether it's:
- 🐛 Bug fixes
- 💡 New features  
- 📚 Documentation improvements
- 🎨 UI enhancements

Feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ using the Datapizza-AI framework** 🍕
