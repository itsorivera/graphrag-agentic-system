import os
from typing import Optional

from google.adk.models.lite_llm import LiteLlm
import logging

from src.core.ports.llm_provider_port import LLMProviderPort


class LiteLLMProviderAdapter(LLMProviderPort):    
    def __init__(
        self,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        aws_region: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        azure_api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None
    ):
        self.logger = logging.getLogger(__name__)
        
        # Configurar credenciales AWS para Bedrock
        self.aws_access_key_id = aws_access_key_id or os.getenv('aws_access_key_id')
        self.aws_secret_access_key = aws_secret_access_key or os.getenv('aws_secret_access_key')
        self.aws_session_token = aws_session_token or os.getenv('aws_session_token')
        self.aws_region = aws_region or os.getenv('aws_region', 'us-east-1')
        
        # Configurar credenciales para otros proveedores
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.azure_api_key = azure_api_key or os.getenv('AZ_KEY')
        self.azure_endpoint = azure_endpoint or os.getenv('AZ_ENDPOINT')
        self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        
        self._setup_environment()
    
    def _setup_environment(self) -> None:
        """Configura las variables de entorno necesarias para LiteLLM"""
        # AWS Bedrock
        if self.aws_access_key_id:
            os.environ['AWS_ACCESS_KEY_ID'] = self.aws_access_key_id
        if self.aws_secret_access_key:
            os.environ['AWS_SECRET_ACCESS_KEY'] = self.aws_secret_access_key
        if self.aws_session_token:
            os.environ['AWS_SESSION_TOKEN'] = self.aws_session_token
        if self.aws_region:
            os.environ['AWS_REGION'] = self.aws_region
        
        # OpenAI
        if self.openai_api_key:
            os.environ['OPENAI_API_KEY'] = self.openai_api_key
        
        # Azure
        if self.azure_api_key:
            os.environ['AZURE_API_KEY'] = self.azure_api_key
        if self.azure_endpoint:
            os.environ['AZURE_API_BASE'] = self.azure_endpoint
        
        # Anthropic
        if self.anthropic_api_key:
            os.environ['ANTHROPIC_API_KEY'] = self.anthropic_api_key
        
        # Groq
        if self.groq_api_key:
            os.environ['GROQ_API_KEY'] = self.groq_api_key
        
        self.logger.info("Variables de entorno configuradas para LiteLLM")
    
    def get_llm(
        self, 
        model_id: str,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        **kwargs
    ) -> LiteLlm:
        """
        Crea una instancia de LiteLlm para uso con google.adk.Agent
        """
        self.logger.info(f"Creando LiteLLM con modelo: {model_id}")
        
        llm = LiteLlm(
            model=model_id,
            **kwargs
        )
        
        self.logger.info(f"LiteLLM creado exitosamente para modelo: {model_id}")
        return llm
    
    def get_bedrock_llm(
        self,
        model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0",
        **kwargs
    ) -> LiteLlm:
        full_model_id = f"bedrock/{model_id}"
        return self.get_llm(model_id=full_model_id, **kwargs)
    
    def get_openai_llm(
        self,
        model_id: str = "gpt-4",
        **kwargs
    ) -> LiteLlm:
        full_model_id = f"openai/{model_id}"
        return self.get_llm(model_id=full_model_id, **kwargs)
    
    def get_anthropic_llm(
        self,
        model_id: str = "claude-3-sonnet-20240229",
        **kwargs
    ) -> LiteLlm:
        full_model_id = f"anthropic/{model_id}"
        return self.get_llm(model_id=full_model_id, **kwargs)
    
    def get_groq_llm(
        self,
        model_id: str = "llama-3.3-70b-versatile",
        **kwargs
    ) -> LiteLlm:
        """
        Crea una instancia de LiteLlm para Groq
        """
        full_model_id = f"groq/{model_id}"
        return self.get_llm(model_id=full_model_id, **kwargs)

    def validate_credentials(self) -> bool:
        try:
            has_aws = bool(self.aws_access_key_id and self.aws_secret_access_key)
            has_openai = bool(self.openai_api_key)
            has_azure = bool(self.azure_api_key and self.azure_endpoint)
            has_anthropic = bool(self.anthropic_api_key)
            has_groq = bool(self.groq_api_key)
            
            if has_aws:
                self.logger.info("Credenciales AWS Bedrock disponibles")
            if has_openai:
                self.logger.info("Credenciales OpenAI disponibles")
            if has_azure:
                self.logger.info("Credenciales Azure disponibles")
            if has_anthropic:
                self.logger.info("Credenciales Anthropic disponibles")
            if has_groq:
                self.logger.info("Credenciales Groq disponibles")
            
            is_valid = has_aws or has_openai or has_azure or has_anthropic or has_groq
            
            if not is_valid:
                self.logger.warning("No se encontraron credenciales configuradas para ningún proveedor")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Error validando credenciales: {str(e)}")
            return False
    
    def cleanup(self) -> None:
        """Limpia recursos (no aplica para LiteLLM)"""
        self.logger.info("Recursos LiteLLM liberados")