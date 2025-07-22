"""Azure AI LLM initialization."""

import os
from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from .config import config

# Disable LangSmith tracing and suppress warnings
os.environ["LANGCHAIN_TRACING_V2"] = "false"

def create_azure_llm(model: str="Phi-4", temperature: float = 0.0) -> AzureAIChatCompletionsModel:
    """Create an Azure AI chat model instance."""
    return AzureAIChatCompletionsModel(
        endpoint=config.azure_ai_endpoint,
        model=model,
        api_version=config.azure_ai_api_version,
        credential=config.azure_ai_api_key,
        temperature=temperature,
    )


# Pre-configured LLM instances for different use cases
manager_llm = create_azure_llm(model = "DeepSeek-R1-0528", temperature=0.0)
planner_llm = create_azure_llm(model = "DeepSeek-R1-0528", temperature=0.1)
programmer_llm = create_azure_llm(model = "DeepSeek-R1-0528", temperature=0.0)
