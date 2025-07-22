"""LLM integration for the agent system."""

from typing import Optional
from langchain_azure_ai import ChatAzureAI
from src.config import config


def get_llm(temperature: float = 0.1) -> ChatAzureAI:
    """Get configured LLM instance."""
    
    return ChatAzureAI(
        azure_endpoint=config.azure_ai_endpoint,
        api_key=config.azure_ai_api_key,
        api_version=config.azure_ai_api_version,
        deployment_name=config.azure_ai_deployment_name,
        temperature=temperature,
        max_tokens=2000,
    )