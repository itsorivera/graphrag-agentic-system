from typing import Any, Dict, List, Optional
from src.core.ports.agent_port import AgentPort
from src.core.ports.llm_provider_port import LLMProviderPort
from src.core.langgraph.nodes import NodeFunctions
from src.core.langgraph.states import AgentState
import logging
from langchain_core.tools import BaseTool
from src.core.ports.graph_strategy_port import GraphStrategyPort


class LanggraphAgentAdapter(AgentPort):
    def _init_(
            self,
            agent_name: str,
            llm_port: LLMProviderPort,
            model_id: str,
            system_prompt: str,
            checkpointer_port: Any = None,
            tools: List[BaseTool] = None,
            graph_strategy: Optional[GraphStrategyPort] = None,
    ): 

        self.agent_name = agent_name
        self.llm_port = llm_port
        self.model_id = model_id
        self.system_prompt = system_prompt
        self.checkpointer_port = checkpointer_port
        self.tools = tools
        self.agent_graph_compiled = None
        self.graph_strategy = graph_strategy
        self.logger = logging.getLogger(__name__)
    
    async def create_agent(self) -> Any:
        self.logger.info(f"Iniciando creación del agente {self.agent_name}")
        
        # Imprimir nombres de las herramientas inyectadas
        tool_names = [tool.name for tool in self.tools]
        self.logger.info(f"Herramientas disponibles para {self.agent_name}: ({len(self.tools)}) >> {tool_names}")
        
        # Configurar LLM con el model_id inyectado
        llm = self.llm_port.get_llm(self.model_id)
        self.logger.info(f"LLM configurado: {self.model_id} para {self.agent_name}")
        
        models = {"conversation_llm": llm}
        
        # Crear funciones de nodos
        self.logger.info(f"Creando funciones de nodos para {self.agent_name}...")
        node_funcs = NodeFunctions(models, system_prompt=self.system_prompt, tools=self.tools)
        node_functions = {
            "call_model": node_funcs.call_model,
            "tool_node": node_funcs.tool_node,
            "should_continue": node_funcs.should_continue
        }
        
        # Construir grafo (reutilizamos el builder, en producción podrías crear uno específico)
        self.logger.info(f"Construyendo grafo del agente {self.agent_name}...")
        #agent_graph = build_react_agent_graph(
        #    state_schema=AgentState,
        #    node_functions=node_functions,
        #)
        agent_graph = self.graph_strategy.build_graph(
            state_schema=AgentState,
            node_functions=node_functions,
        )
        
        self.logger.info("Compilando grafo con checkpointer...")
        checkpointer = await self.checkpointer_port.get_checkpointer()
        self.agent_graph_compiled = agent_graph.compile(checkpointer=checkpointer)
        
        self.logger.info(f"Agente {self.agent_name} creado exitosamente")
        return self.agent_graph_compiled

    async def process_message(self, message: str, thread_id: str) -> Dict[str, Any]:
        if not self.agent_graph_compiled:
            raise RuntimeError("El agente no ha sido inicializado. Llama a create_agent() primero.")
        
        self.logger.info(f"Procesando solicitud de agente {self.agent_name} en thread {thread_id}")
        self.logger.debug(f"Mensaje de usuario: {message}")
        
        config = {"configurable": {"thread_id": thread_id}}
        result = await self.agent_graph_compiled.ainvoke({"messages_tools": message}, config)

        self.logger.debug(f"Respuesta final generada de agente {self.agent_name}: {result['messages'][-1].content}")
        return result
    
    async def cleanup(self) -> None:
        self.logger.info(f"Limpiando recursos del agente {self.agent_name}...")
        
        try:
            await self.checkpointer_port.cleanup()
            self.logger.info("Checkpointer limpiado")
        except Exception as e:
            self.logger.error(f"Error al limpiar checkpointer: {e}")
        
        try:
            self.llm_port.cleanup()
            self.logger.info("LLM provider limpiado")
        except Exception as e:
            self.logger.error(f"Error al limpiar LLM provider: {e}")
        
        self.logger.info(f"Limpieza del agente {self.agent_name} completada")