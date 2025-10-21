# Architecture Overview

## System Design

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py (CLI)                       │
│  - Interactive command-line interface                       │
│  - Command parsing (list, select, ask, check, etc.)        │
│  - User interaction loop                                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ uses
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                       Chat Class                            │
│  - Manages functionalities                                  │
│  - Handles interactions                                     │
│  - Maintains conversation history                           │
│  - Coordinates between API and functionalities              │
└───────────┬─────────────────────────────┬───────────────────┘
            │                             │
            │ uses                        │ uses
            ▼                             ▼
┌────────────────────────┐    ┌────────────────────────────┐
│   AIChatbotAPI         │    │   Functionality            │
│   (Abstract Base)      │    │   (Abstract Base)          │
│                        │    │                            │
│  - receive_question()  │    │  - get_name()              │
│  - generate_answer()   │    │  - execute()               │
│  - check_answer()      │    │                            │
│  - respond_with_error()│    │                            │
└───────┬────────────────┘    └──────┬─────────────────────┘
        │                             │
        │ implemented by              │ implemented by
        ▼                             ▼
┌────────────────────────┐    ┌────────────────────────────┐
│  MockAIChatbotAPI      │    │  Example Functionalities   │
│  (Mock Implementation) │    │  - TranslationFunctionality│
│                        │    │  - GrammarFunctionality    │
│  For testing/demo      │    │  - VocabularyFunctionality │
│  Replace with real AI  │    │  - ConversationFunc...     │
└────────────────────────┘    └────────────────────────────┘
        ▲                             ▲
        │                             │
        │ example                     │ example
        │                             │
┌────────────────────────┐    ┌────────────────────────────┐
│  CustomAIChatbotAPI    │    │  Your Custom               │
│  (Your Implementation) │    │  Functionalities           │
│                        │    │                            │
│  - OpenAI integration  │    │  - Define your own         │
│  - HuggingFace models  │    │  - Extend Functionality    │
│  - Custom AI logic     │    │  - Add domain logic        │
└────────────────────────┘    └────────────────────────────┘
```

## Data Flow

### 1. User Asks a Question

```
User Input → main.py → Chat.handle_interaction()
                           ↓
                     API.receive_question()
                           ↓
                     API.generate_answer()
                           ↓
                     Functionality.execute()
                           ↓
                     Store in history
                           ↓
                     Return to user
```

### 2. User Submits an Answer

```
User Answer → main.py → Chat.check_user_response()
                            ↓
                      API.check_answer()
                            ↓
                      if incorrect:
                        API.respond_with_error()
                            ↓
                      Return validation result
```

## Key Design Patterns

### 1. Strategy Pattern
- Different functionalities can be swapped at runtime
- `Chat` class uses the selected `Functionality` object

### 2. Abstract Factory Pattern
- `AIChatbotAPI` and `Functionality` are abstract base classes
- Concrete implementations can be created without modifying core code

### 3. Template Method Pattern
- Abstract base classes define the interface
- Concrete classes implement specific behavior

## Extension Points

### Adding New AI Backend

1. Create a class implementing `AIChatbotAPI`
2. Implement all required methods
3. Replace `MockAIChatbotAPI` in `main.py`

### Adding New Functionality

1. Create a class extending `Functionality`
2. Implement `get_name()` and `execute()`
3. Add instance to `Chat` using `add_functionality()`

### Modifying CLI

1. Edit `main.py`
2. Add new command parsing in the main loop
3. Call appropriate `Chat` methods

## File Responsibilities

| File | Responsibility |
|------|----------------|
| `chat.py` | Core chat management, functionality coordination |
| `ai_chatbot_api.py` | AI interface definition |
| `functionality.py` | Functionality interface definition |
| `main.py` | CLI implementation and user interaction |
| `mock_ai_api.py` | Mock AI for testing/demo |
| `example_functionalities.py` | Sample functionality implementations |
| `custom_ai_example.py` | Template for custom AI implementation |

## Typical Usage Flow

```python
# 1. Initialize
api = MockAIChatbotAPI()  # or your custom API
chat = Chat(api)

# 2. Add functionalities
chat.add_functionality(GrammarFunctionality())
chat.add_functionality(TranslationFunctionality())

# 3. Select a functionality
chat.select_functionality("grammar")

# 4. Interact
result = chat.handle_interaction("What is the plural of Haus?")
print(result['answer'])

# 5. Validate answer
validation = chat.check_user_response("What is...", "Häuser")
if validation['is_correct']:
    print("Correct!")
else:
    print(validation['error_response'])

# 6. Review history
for item in chat.get_conversation_history():
    print(f"Q: {item['user_input']}")
    print(f"A: {item['answer']}")
```

## Security Considerations

1. **API Keys**: Store API keys in environment variables, not in code
2. **Input Validation**: Validate user input before processing
3. **Error Handling**: Don't expose internal errors to users
4. **Rate Limiting**: Consider rate limiting for API calls

## Performance Tips

1. **Caching**: Cache frequent translations/answers
2. **Async Operations**: Use async for API calls if needed
3. **Lazy Loading**: Load functionalities on demand
4. **Session Management**: Persist chat history to database for long sessions

## Testing Strategy

1. **Unit Tests**: Test each class independently
2. **Integration Tests**: Test Chat + API + Functionality together
3. **CLI Tests**: Automate CLI testing with piped input
4. **Mock Testing**: Use MockAIChatbotAPI for testing without real AI

## Future Enhancements

- [ ] Add database persistence for conversation history
- [ ] Implement multi-user support
- [ ] Add voice input/output support
- [ ] Create web interface using Flask/FastAPI
- [ ] Add analytics and learning progress tracking
- [ ] Implement plugin system for dynamic functionality loading
- [ ] Add support for multiple languages
- [ ] Create mobile app wrapper
