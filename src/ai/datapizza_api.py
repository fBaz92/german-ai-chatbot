"""
Thin wrapper for Datapizza AI clients (Ollama and Google Gemini).
Provides unified interface for initializing and accessing AI models.
"""
import os
from pathlib import Path
from typing import Literal, Optional
from dotenv import load_dotenv
from datapizza.clients.openai_like import OpenAILikeClient
from datapizza.clients.google import GoogleClient

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class DatapizzaAPI:
    """
    Thin wrapper for Datapizza AI clients.
    Provides unified interface for initializing Ollama (local) or Google Gemini (cloud).
    """

    def __init__(
        self,
        provider: Literal["ollama", "google"] = "ollama",
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:11434/v1",
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize the Datapizza API client.

        Args:
            provider: "ollama" for local or "google" for Google Gemini
            api_key: API key (for Google, reads from GEMINI_KEY env if None)
            base_url: Base URL for Ollama API
            model: Model to use (defaults: gemma3:1b for Ollama, gemini-2.5-flash for Google)
            system_prompt: Optional system prompt for the AI (default: None)
        """
        self.provider = provider

        if provider == "google":
            # Google Gemini client
            if api_key is None:
                api_key = os.getenv("GEMINI_KEY")

            if not api_key:
                raise ValueError("GEMINI_KEY not found in environment. Set it with: export GEMINI_KEY='your-key'")

            self.model = model or "gemini-2.5-flash"
            self.client = GoogleClient(
                api_key=api_key,
                model=self.model,
                system_prompt=system_prompt,
            )

        else:  # ollama
            # Ollama local client
            self.model = model or "gemma3:1b"
            self.client = OpenAILikeClient(
                api_key="",  # Ollama doesn't require an API key
                model=self.model,
                system_prompt=system_prompt,
                base_url=base_url
            )
