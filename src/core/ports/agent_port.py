from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.models.agent_response import AgentResponse


class AgentPort(ABC):
    """
    Puerto abstracto para agentes del sistema.
    
    Define las operaciones básicas que todo agente debe implementar:
    - Creación/inicialización del agente
    - Procesamiento de mensajes con respuesta estandarizada
    - Limpieza de recursos
    """

    @abstractmethod
    async def create_agent(self) -> Any:
        """
        Crea e inicializa el agente.
        
        Returns:
            Any: El agente compilado/configurado listo para ejecutar
            
        Raises:
            RuntimeError: Si hay un error durante la inicialización
        """
        pass

    @abstractmethod
    async def process_message(self, message: str, thread_id: str) -> AgentResponse:
        """
        Procesa un mensaje utilizando el agente.
        
        Args:
            message: El mensaje de entrada a procesar
            thread_id: Identificador único del hilo de conversación
            
        Returns:
            AgentResponse: Respuesta estandarizada del agente
            
        Raises:
            RuntimeError: Si el agente no ha sido inicializado
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Limpia los recursos utilizados por el agente.
        
        Debe liberar:
        - Conexiones a bases de datos (persistencia)
        - Recursos del proveedor de LLM
        - Clientes MCP u otros servicios externos
        """
        pass
    
    def get_agent_name(self) -> str:
        """
        Retorna el nombre del agente.
        
        Returns:
            Nombre identificador del agente
        """
        return getattr(self, 'agent_name', 'unknown_agent')


class HierarchicalAgentPort(AgentPort):
    """
    Puerto extendido para agentes con soporte de sub-agentes.
    
    Extiende AgentPort para soportar jerarquías de agentes,
    donde un agente raíz puede delegar tareas a sub-agentes especializados.
    
    Útil para arquitecturas multi-agente como las soportadas por ADK.
    """
    
    @abstractmethod
    def add_sub_agent(self, agent: "AgentPort") -> None:
        """
        Agrega un sub-agente a la jerarquía.
        
        Args:
            agent: Agente a agregar como sub-agente
        """
        pass
    
    @abstractmethod
    def remove_sub_agent(self, agent_name: str) -> bool:
        """
        Remueve un sub-agente de la jerarquía.
        
        Args:
            agent_name: Nombre del agente a remover
            
        Returns:
            True si se removió, False si no existía
        """
        pass
    
    @abstractmethod
    def get_sub_agents(self) -> List["AgentPort"]:
        """
        Obtiene la lista de sub-agentes.
        
        Returns:
            Lista de sub-agentes registrados
        """
        pass
    
    @abstractmethod
    def get_sub_agent(self, agent_name: str) -> Optional["AgentPort"]:
        """
        Obtiene un sub-agente por nombre.
        
        Args:
            agent_name: Nombre del sub-agente
            
        Returns:
            El sub-agente si existe, None si no
        """
        pass


class StreamingAgentPort(AgentPort):
    """
    Puerto extendido para agentes con soporte de streaming.
    
    Permite procesar mensajes con respuestas en streaming,
    útil para interfaces de usuario en tiempo real.
    """
    
    @abstractmethod
    async def process_message_stream(
        self, 
        message: str, 
        thread_id: str
    ):
        """
        Procesa un mensaje con respuesta en streaming.
        
        Args:
            message: El mensaje de entrada a procesar
            thread_id: Identificador único del hilo de conversación
            
        Yields:
            AgentMessage: Mensajes parciales conforme se generan
        """
        pass