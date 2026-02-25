from typing import Any, Dict, List, Optional, Callable
from src.core.ports.agent_port import AgentPort, HierarchicalAgentPort
from src.core.ports.llm_provider_port import LLMProviderPort
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.genai import types
import logging

class ADKSubAgentConfig:
    def __init__(
        self,
        name: str,
        description: str,
        instruction: str,
        tools: List[Callable] = None,
        model: Optional[str] = None
    ):
        self.name = name
        self.description = description
        self.instruction = instruction
        self.tools = tools or []
        self.model = model


class ADKAgentAdapter(HierarchicalAgentPort):
    def __init__(
        self,
        agent_name: str,
        model: str,
        instruction: str,
        global_instruction: str = "",
        sub_agent_configs: List[ADKSubAgentConfig] = None,
        tools: List[Callable] = None,
        llm_port: Optional[LLMProviderPort] = None,
        app_name: str = "adk_agent_app",
        user_id: str = "default_user"
    ):
        self.agent_name = agent_name
        self.model = model
        self.instruction = instruction
        self.global_instruction = global_instruction
        self.sub_agent_configs = sub_agent_configs or []
        self.tools = tools or []
        self.llm_port = llm_port
        self.app_name = app_name
        self.user_id = user_id
        
        self.root_agent: Optional[Agent] = None
        self.runner: Optional[Runner] = None
        self.session_service: Optional[InMemorySessionService] = None
        self.sessions: Dict[str, Session] = {}
        
        self.logger = logging.getLogger(__name__)
    
    def _build_sub_agents(self) -> List[Agent]:
        sub_agents = []
        
        for config in self.sub_agent_configs:
            agent_model_id = config.model or self.model
            
            # Resolve model instance if port is available
            model_instance = agent_model_id
            if self.llm_port:
                self.logger.debug(f"Resolviendo instancia de modelo para sub-agente {config.name}: {agent_model_id}")
                model_instance = self.llm_port.get_llm(agent_model_id)
            
            sub_agent = Agent(
                model=model_instance,
                name=config.name,
                description=config.description,
                instruction=config.instruction,
                tools=config.tools
            )
            
            sub_agents.append(sub_agent)
            self.logger.info(f"Sub-agente creado: {config.name}")
        
        return sub_agents
    
    async def create_agent(self) -> Any:
        self.logger.info(f"Iniciando creación del agente ADK: {self.agent_name}")
        
        try:
            # Construir sub-agentes
            sub_agents = self._build_sub_agents()
            self.logger.info(f"Construidos {len(sub_agents)} sub-agentes")
            
            # Resolve root model instance if port is available
            root_model_instance = self.model
            if self.llm_port:
                self.logger.debug(f"Resolviendo instancia de modelo raíz: {self.model}")
                root_model_instance = self.llm_port.get_llm(self.model)

            # Crear agente raíz
            self.root_agent = Agent(
                model=root_model_instance,
                name=self.agent_name,
                global_instruction=self.global_instruction,
                instruction=self.instruction,
                tools=self.tools,
                sub_agents=sub_agents if sub_agents else None
            )
            self.logger.info(f"Agente raíz creado: {self.agent_name}")
            
            # Configurar servicio de sesiones
            self.session_service = InMemorySessionService()
            
            # Crear runner
            self.runner = Runner(
                agent=self.root_agent,
                app_name=self.app_name,
                session_service=self.session_service
            )
            
            self.logger.info(f"Runner ADK configurado para {self.agent_name}")
            return self.runner
            
        except Exception as e:
            self.logger.error(f"Error creando agente ADK: {e}")
            raise RuntimeError(f"Error inicializando agente ADK: {e}") from e
    
    def _get_or_create_session(self, thread_id: str) -> Session:
        if thread_id not in self.sessions:
            session = self.session_service.create_session(
                app_name=self.app_name,
                user_id=self.user_id,
                session_id=thread_id
            )
            self.sessions[thread_id] = session
            self.logger.info(f"Nueva sesión creada para thread: {thread_id}")
        
        return self.sessions[thread_id]
    
    async def process_message(self, message: str, thread_id: str) -> Dict[str, Any]:
        if not self.runner:
            raise RuntimeError(
                "El agente no ha sido inicializado. Llama a create_agent() primero."
            )
        
        self.logger.info(f"Procesando mensaje en thread {thread_id}")
        self.logger.debug(f"Mensaje: {message}")
        
        try:
            # Obtener o crear sesión
            session = self._get_or_create_session(thread_id)
            
            # Crear contenido del mensaje
            content = types.Content(
                role="user",
                parts=[types.Part(text=message)]
            )
            
            # Ejecutar agente y recolectar respuestas
            responses = []
            final_response = None
            
            async for event in self.runner.run_async(
                user_id=self.user_id,
                session_id=thread_id,
                new_message=content
            ):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response = event.content.parts[0].text
                        responses.append({
                            "role": "assistant",
                            "content": final_response,
                            "agent": event.author if hasattr(event, 'author') else self.agent_name
                        })
                elif event.content:
                    # Capturar respuestas intermedias de sub-agentes
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            responses.append({
                                "role": "agent_step",
                                "content": part.text,
                                "agent": event.author if hasattr(event, 'author') else "unknown"
                            })
            
            self.logger.info(f"Procesamiento completado para thread {thread_id}")
            
            return {
                "messages": responses,
                "final_response": final_response,
                "thread_id": thread_id,
                "agent_name": self.agent_name
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando mensaje: {e}")
            raise
    
    async def cleanup(self) -> None:
        self.logger.info(f"Limpiando recursos del agente ADK: {self.agent_name}")
        
        # Limpiar sesiones
        self.sessions.clear()
        self.logger.info("Sesiones limpiadas")
        
        # Limpiar LLM provider si existe
        if self.llm_port:
            try:
                self.llm_port.cleanup()
                self.logger.info("LLM provider limpiado")
            except Exception as e:
                self.logger.error(f"Error limpiando LLM provider: {e}")
        
        # Reset referencias
        self.root_agent = None
        self.runner = None
        self.session_service = None
        
        self.logger.info(f"Limpieza del agente ADK {self.agent_name} completada")