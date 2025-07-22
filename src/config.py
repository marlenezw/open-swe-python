"""Configuration management for Python Open SWE."""

import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Config(BaseModel):
    """Application configuration."""
    
    # Azure AI settings
    azure_ai_api_key: str = os.getenv("AZURE_AI_API_KEY", "")
    azure_ai_endpoint: str = os.getenv("AZURE_AI_ENDPOINT", "")
    azure_ai_api_version: str = os.getenv("AZURE_AI_API_VERSION", "2024-02-15-preview")
    azure_ai_deployment_name: str = os.getenv("AZURE_AI_DEPLOYMENT_NAME", "")

    # LangSmith tracing (optional)
    langchain_tracing_v2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "false"
    langchain_api_key: Optional[str] = os.getenv("LANGCHAIN_API_KEY")
    langchain_project: str = os.getenv("LANGCHAIN_PROJECT", "python-open-swe")
    
    # Application settings
    log_level: str = os.getenv("LOG_LEVEL", "ERROR")
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "10"))
    
    def validate_required(self) -> None:
        """Validate required configuration fields."""
        if not self.azure_ai_api_key:
            raise ValueError("AZURE_AI_API_KEY is required")
        if not self.azure_ai_endpoint:
            raise ValueError("AZURE_AI_ENDPOINT is required")
        if not self.azure_ai_deployment_name:
            raise ValueError("AZURE_AI_DEPLOYMENT_NAME is required")


config = Config()