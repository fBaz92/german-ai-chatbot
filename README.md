# German AI Chatbot

A command-line chatbot boilerplate for German language learning with pluggable functionality system.

## Overview

This project provides a boilerplate for a command-line AI chatbot with a modular architecture. The chatbot allows you to:

- Choose from various learning functionalities (translation, grammar, vocabulary, conversation)
- Handle interactive chat sessions
- Check answers with AI validation
- Track conversation history

## Architecture

The project is organized into several key components:

### Core Classes

- **`Chat`** (`chat.py`): Main chat class that manages functionalities and handles interactions
- **`AIChatbotAPI`** (`ai_chatbot_api.py`): Abstract interface for AI chatbot logic
- **`Functionality`** (`functionality.py`): Abstract base class for chatbot functionalities

### Implementations

- **`MockAIChatbotAPI`** (`mock_ai_api.py`): Mock implementation of the AI API (replace with your actual AI logic)
- **Example Functionalities** (`example_functionalities.py`):
  - `TranslationFunctionality`
  - `GrammarFunctionality`
  - `VocabularyFunctionality`
  - `ConversationFunctionality`

### Entry Point

- **`main.py`**: Command-line interface for interacting with the chatbot

## Installation

1. Clone the repository:
```bash
git clone https://github.com/fBaz92/german-ai-chatbot.git
cd german-ai-chatbot
```

2. No external dependencies required for the basic boilerplate (uses only Python standard library)

## Usage

### Running the Chatbot

```bash
python main.py
```

Or make it executable:
```bash
chmod +x main.py
./main.py
```

### Available Commands

- `list` - List available functionalities
- `select <name>` - Select a functionality (e.g., `select grammar`)
- `ask <question>` - Ask a question to the chatbot
- `check <answer>` - Check your answer to the last question
- `history` - Show conversation history
- `clear` - Clear conversation history
- `help` - Show help message
- `quit` or `exit` - Exit the chatbot

### Example Session

```
> list
Available functionalities:
   translation
   grammar
   vocabulary
   conversation

> select grammar
Selected functionality: grammar

> ask What is the correct article for "Haus"?
Answer: Mock answer for: 'What is the correct article for "Haus"?'
Functionality: Grammar functionality executed

> check das Haus
✓ Good answer!

> history
Conversation History:
--------------------------------------------------
1. Question: What is the correct article for "Haus"?
   Answer: Mock answer for: 'What is the correct article for "Haus"?'
   Time: 2024-01-01T12:00:00.000000
```

## Implementing Your Own AI Logic

### 1. Implement the AI Chatbot API

Replace `MockAIChatbotAPI` with your actual AI implementation:

```python
from ai_chatbot_api import AIChatbotAPI

class MyAIChatbotAPI(AIChatbotAPI):
    def receive_question(self, question: str):
        # Your implementation
        pass
    
    def generate_answer(self, question: str, context=None):
        # Your implementation
        pass
    
    def check_answer(self, question: str, user_answer: str):
        # Your implementation
        pass
    
    def respond_with_error(self, error_message: str, correct_answer: str):
        # Your implementation
        pass
```

### 2. Create Custom Functionalities

Extend the `Functionality` class:

```python
from functionality import Functionality

class MyCustomFunctionality(Functionality):
    def get_name(self):
        return "my_functionality"
    
    def execute(self, context):
        # Your implementation
        return {"status": "executed", "result": "..."}
```

### 3. Update main.py

Replace the mock API with your implementation:

```python
from my_ai_api import MyAIChatbotAPI

api = MyAIChatbotAPI()
chat = Chat(api)
```

## Project Structure

```
german-ai-chatbot/
├── README.md                      # This file
├── main.py                        # CLI entry point
├── chat.py                        # Main Chat class
├── ai_chatbot_api.py             # AI API interface
├── functionality.py              # Functionality base class
├── mock_ai_api.py                # Mock AI implementation
└── example_functionalities.py    # Example functionality implementations
```

## API Reference

### Chat Class

```python
chat = Chat(api)
chat.add_functionality(functionality)      # Add a functionality
chat.select_functionality(name)            # Select active functionality
chat.handle_interaction(user_input)        # Process user input
chat.check_user_response(question, answer) # Validate answer
chat.get_conversation_history()            # Get history
chat.clear_history()                       # Clear history
```

### AIChatbotAPI Interface

All methods must be implemented:

- `receive_question(question)` - Process incoming question
- `generate_answer(question, context)` - Generate AI response
- `check_answer(question, user_answer)` - Validate answer
- `respond_with_error(error_message, correct_answer)` - Format error response

### Functionality Interface

All methods must be implemented:

- `get_name()` - Return functionality name
- `execute(context)` - Execute functionality logic

## Contributing

Feel free to add more functionalities or improve the AI implementation!

## License

MIT License