#!/usr/bin/env python3
"""
Command-line interface for the German AI Chatbot.
"""
import sys
from chat import Chat
from mock_ai_api import MockAIChatbotAPI
from example_functionalities import (
    TranslationFunctionality,
    GrammarFunctionality,
    VocabularyFunctionality,
    ConversationFunctionality
)


def print_banner():
    """Print welcome banner."""
    print("=" * 50)
    print("  German AI Chatbot - Command Line Interface")
    print("=" * 50)
    print()


def print_help():
    """Print available commands."""
    print("\nAvailable commands:")
    print("  list              - List available functionalities")
    print("  select <name>     - Select a functionality")
    print("  ask <question>    - Ask a question to the chatbot")
    print("  check <answer>    - Check your answer to the last question")
    print("  history           - Show conversation history")
    print("  clear             - Clear conversation history")
    print("  help              - Show this help message")
    print("  quit/exit         - Exit the chatbot")
    print()


def main():
    """Main entry point for the CLI chatbot."""
    print_banner()
    
    # Initialize the chatbot with mock API
    # Replace MockAIChatbotAPI with your actual implementation
    api = MockAIChatbotAPI()
    chat = Chat(api)
    
    # Add example functionalities
    chat.add_functionality(TranslationFunctionality())
    chat.add_functionality(GrammarFunctionality())
    chat.add_functionality(VocabularyFunctionality())
    chat.add_functionality(ConversationFunctionality())
    
    print("\nChatbot initialized with example functionalities.")
    print_help()
    
    last_question = None
    
    # Main interaction loop
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
            
            # Parse command
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if command in ["quit", "exit"]:
                print("\nGoodbye!")
                break
            
            elif command == "help":
                print_help()
            
            elif command == "list":
                functionalities = chat.list_functionalities()
                print("\nAvailable functionalities:")
                for func in functionalities:
                    marker = "→" if chat.active_functionality and chat.active_functionality.get_name() == func else " "
                    print(f"  {marker} {func}")
            
            elif command == "select":
                if not args:
                    print("Usage: select <functionality_name>")
                else:
                    chat.select_functionality(args)
            
            elif command == "ask":
                if not args:
                    print("Usage: ask <your question>")
                else:
                    last_question = args
                    result = chat.handle_interaction(args)
                    print(f"\nAnswer: {result['answer']}")
                    if result.get('functionality_result'):
                        print(f"Functionality: {result['functionality_result'].get('message', '')}")
            
            elif command == "check":
                if not args:
                    print("Usage: check <your answer>")
                elif not last_question:
                    print("No question asked yet. Use 'ask' command first.")
                else:
                    result = chat.check_user_response(last_question, args)
                    if result['is_correct']:
                        print(f"✓ {result.get('feedback', 'Correct!')}")
                    else:
                        print(result.get('error_response', 'Incorrect'))
            
            elif command == "history":
                history = chat.get_conversation_history()
                if not history:
                    print("\nNo conversation history yet.")
                else:
                    print("\nConversation History:")
                    print("-" * 50)
                    for i, item in enumerate(history, 1):
                        print(f"\n{i}. Question: {item['user_input']}")
                        print(f"   Answer: {item['answer']}")
                        print(f"   Time: {item['timestamp']}")
            
            elif command == "clear":
                chat.clear_history()
                print("Conversation history cleared.")
            
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
