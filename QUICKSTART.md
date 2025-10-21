# Quick Start Guide

## Getting Started in 5 Minutes

### 1. Run the Chatbot

```bash
python main.py
```

### 2. Try These Commands

```
> help                          # See all available commands
> list                          # See available functionalities
> select grammar                # Choose the grammar functionality
> ask What is the plural of Haus?    # Ask a question
> history                       # View conversation history
> quit                          # Exit
```

## Replacing Mock AI with Real Implementation

### Step 1: Create Your AI Implementation

Create a new file `my_ai_implementation.py`:

```python
from ai_chatbot_api import AIChatbotAPI
from typing import Dict, Any

class MyAI(AIChatbotAPI):
    def __init__(self):
        # Initialize your AI model/API
        pass
    
    def receive_question(self, question: str) -> Dict[str, Any]:
        # Process the question
        return {"question": question, "processed": True}
    
    def generate_answer(self, question: str, context: Dict[str, Any] = None) -> str:
        # Your AI logic here
        return "Your AI-generated answer"
    
    def check_answer(self, question: str, user_answer: str) -> Dict[str, Any]:
        # Validate the answer
        return {
            "is_correct": True,
            "feedback": "Great job!"
        }
    
    def respond_with_error(self, error_message: str, correct_answer: str) -> str:
        return f"❌ {error_message}\n✓ {correct_answer}"
```

### Step 2: Update main.py

Replace these lines in `main.py`:

```python
# OLD:
from mock_ai_api import MockAIChatbotAPI
api = MockAIChatbotAPI()

# NEW:
from my_ai_implementation import MyAI
api = MyAI()
```

### Step 3: Run Your Custom Chatbot

```bash
python main.py
```

## Creating Custom Functionalities

Create a new file `my_functionality.py`:

```python
from functionality import Functionality
from typing import Dict, Any

class MyCustomFunctionality(Functionality):
    def get_name(self) -> str:
        return "my_custom_feature"
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Your functionality logic
        question = context.get("question")
        answer = context.get("answer")
        
        # Do something with the question/answer
        result = f"Processed: {question}"
        
        return {
            "functionality": "my_custom_feature",
            "status": "executed",
            "result": result
        }
```

Then add it to `main.py`:

```python
from my_functionality import MyCustomFunctionality

# In the main() function:
chat.add_functionality(MyCustomFunctionality())
```

## Integration Examples

### Example 1: Using OpenAI API

```python
import openai
from ai_chatbot_api import AIChatbotAPI

class OpenAIChatbot(AIChatbotAPI):
    def __init__(self, api_key: str):
        openai.api_key = api_key
    
    def generate_answer(self, question: str, context=None):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        return response.choices[0].message.content
    
    # Implement other methods...
```

### Example 2: Using Hugging Face

```python
from transformers import pipeline
from ai_chatbot_api import AIChatbotAPI

class HuggingFaceChatbot(AIChatbotAPI):
    def __init__(self):
        self.translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-de")
    
    def generate_answer(self, question: str, context=None):
        result = self.translator(question)
        return result[0]['translation_text']
    
    # Implement other methods...
```

## Tips

1. **Start Simple**: Begin with the mock implementation to understand the structure
2. **Test Incrementally**: Test each method of your AI implementation separately
3. **Use Type Hints**: Follow the type hints in the abstract classes
4. **Handle Errors**: Add try-except blocks in your implementation
5. **Log Everything**: Consider adding logging for debugging

## Need Help?

Check the full README.md for detailed documentation and API reference.
