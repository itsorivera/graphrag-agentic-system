from pydantic import Field
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    APP_NAME: str = Field(default="GraphRAG Agentic System")
    API_BASE_URL: str = Field(default="http://localhost:8000")
    API_BASE_PATH: str = Field(default="/api")
    API_VERSION: str = Field(default="v1")
    HOST: str = Field(default="localhost")
    PORT: int = Field(default=8000)
    
    DEFAULT_MODEL_ID: str = Field(default="anthropic.claude-3-5-sonnet-20240620-v1:0")

    DEFAULT_MODEL_TEMPERATURE: float = Field(default=0.7)
    
    MCP_TOOLBOX_URL: str = Field(default="http://localhost:8000")
    MCP_TOOLBOX_NAME: str = Field(default="Toolbox")
    
    NEO4J_DATABASE_URL: str = Field(default="")
    NEO4J_DATABASE_USER: str = Field(default="")
    NEO4J_DATABASE_PASSWORD: str = Field(default="")
    NEO4J_DATABASE_NAME: str = Field(default="")

    AWS_ACCESS_KEY_ID: str = Field(default="")
    AWS_SECRET_ACCESS_KEY: str = Field(default="")
    AWS_REGION: str = Field(default="us-east-1")

    AZURE_OPENAI_API_KEY: str = Field(default="")
    AZURE_OPENAI_API_BASE: str = Field(default="")
    AZURE_OPENAI_API_VERSION: str = Field(default="")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = Field(default="")

    OPENAI_API_KEY: str = Field(default="")
    OPENAI_API_BASE: str = Field(default="")
    OPENAI_API_VERSION: str = Field(default="")
    OPENAI_DEPLOYMENT_NAME: str = Field(default="")

    OLLAMA_SERVICE_URL: str = Field(default="")

    HUGGINGFACE_API_KEY: str = Field(default="")

    GROQ_API_KEY: str = Field(default="")

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False

config = AppConfig()


    