import os
from typing import Any
from langchain_openai import ChatOpenAI
from ai-service.utils.logging import get_logger

logger = get_logger("ai_service.llm")


class LLMService:
    """Enterprise LLM Service abstraction managing OpenRouter, OpenAI, and custom providers."""

    def __init__(self, model_name: str = None, temperature: float = 0.1):
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if not model_name:
            model_name = os.getenv("LLM_MODEL", "mistralai/mistral-large-2411")

        self.model_name = model_name

        if openrouter_key and openrouter_key != "your_openrouter_api_key_here":
            logger.info("Initializing OpenRouter LLM Client", model=model_name)
            self.llm = ChatOpenAI(
                model=model_name,
                openai_api_key=openrouter_key,
                openai_api_base="https://openrouter.ai/api/v1",
                temperature=temperature,
                max_retries=3,
                request_timeout=60.0,
            )
        elif openai_key and openai_key != "your_openai_api_key_optional":
            logger.info("Initializing Direct OpenAI LLM Client", model="gpt-4o")
            self.llm = ChatOpenAI(
                model="gpt-4o",
                openai_api_key=openai_key,
                temperature=temperature,
                max_retries=3,
            )
        else:
            logger.warning("No live API keys found for LLM. Operating in fallback mock mode.")
            self.llm = None

    def invoke(self, prompt_text: str) -> str:
        """Invokes LLM with system/user prompt string."""
        if not self.llm:
            logger.warning("LLM client not configured. Returning structured mock response.")
            return '{"risk_score": "HIGH", "recommended_action": "NOTICE_TO_QUIT", "reasoning": "Mock fallback reasoning"}'

        try:
            response = self.llm.invoke(prompt_text)
            return response.content
        except Exception as e:
            logger.error("LLM invocation error", error=str(e))
            raise e
