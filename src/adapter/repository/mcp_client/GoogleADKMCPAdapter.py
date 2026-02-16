from typing import Any, Dict, List, Optional
import logging

from src.core.ports.mcp_client_port import MCPClientPort


class GoogleADKMCPAdapter(MCPClientPort):
    """
    Adaptador MCP usando Google ADK MCPToolset con transporte SSE.
    
    Implementa la interfaz MCPClientPort para servidores MCP que
    requieren conexión mediante Server-Sent Events.
    
    Attributes:
        server_url: URL del servidor MCP
        server_name: Nombre identificador del servidor
        _toolset: Instancia del MCPToolset de Google ADK
        _tools: Cache de herramientas cargadas
    """
    
    TRANSPORT_TYPE = "sse"
    
    def __init__(self, server_url: str, server_name: str = "default"):
        """
        Inicializa el adaptador Google ADK MCP.
        
        Args:
            server_url: URL del servidor MCP (debe soportar SSE)
            server_name: Nombre identificador para logging y referencia
        """
        self.server_url = server_url
        self.server_name = server_name
        self._toolset: Optional[Any] = None
        self._tools: Optional[List[Any]] = None
        self._is_connected: bool = False
        self.logger = logging.getLogger(f"{__name__}.GoogleADKMCPAdapter")
    
    async def _initialize_client(self) -> None:
        """
        Inicializa el MCPToolset si no está inicializado.
        
        Realiza lazy initialization del cliente para evitar
        conexiones innecesarias al instanciar el adaptador.
        
        Raises:
            ImportError: Si google.adk no está instalado
            ConnectionError: Si no se puede conectar al servidor
        """
        if self._toolset is not None and self._is_connected:
            return
        
        try:
            # Import dinámico para evitar dependencia obligatoria
            from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
        except ImportError as e:
            self.logger.error(
                "google-adk no está instalado. "
                "Instala con: pip install google-adk"
            )
            raise ImportError(
                "Dependencia google-adk requerida para GoogleADKMCPAdapter. "
                "Ejecuta: pip install google-adk"
            ) from e
        
        try:
            self.logger.info(
                f"Inicializando Google ADK MCP client para servidor: "
                f"{self.server_name} con URL: {self.server_url}"
            )
            
            # Crear conexión SSE
            connection_params = SseConnectionParams(url=self.server_url)
            self._toolset = MCPToolset(connection_params=connection_params)
            
            # Entrar al context manager manualmente para mantener conexión activa
            await self._toolset.__aenter__()
            self._is_connected = True
            
            # Cargar herramientas
            self._tools = await self._toolset.load_tools()
            self.logger.info(
                f"Cargadas {len(self._tools)} herramientas desde "
                f"servidor MCP: {self.server_name}"
            )
            
        except Exception as e:
            self.logger.error(
                f"Error al inicializar Google ADK MCP client para "
                f"{self.server_name}: {str(e)}"
            )
            self._tools = []
            self._is_connected = False
            raise ConnectionError(
                f"No se pudo conectar al servidor MCP {self.server_name}: {str(e)}"
            ) from e
    
    async def get_tools(self) -> List[Any]:
        """
        Obtiene las herramientas disponibles desde el servidor MCP.
        
        Returns:
            Lista de herramientas compatibles con Google ADK/LangChain
        """
        try:
            if self._tools is None:
                await self._initialize_client()
            
            return list(self._tools) if self._tools else []
            
        except Exception as e:
            self.logger.error(
                f"Error obteniendo herramientas del servidor MCP "
                f"{self.server_name}: {str(e)}"
            )
            return []
    
    async def execute_tool(
        self, 
        tool_name: str, 
        tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecuta una herramienta específica en el servidor MCP.
        
        Args:
            tool_name: Nombre de la herramienta a ejecutar
            tool_input: Parámetros de entrada para la herramienta
            
        Returns:
            Diccionario con 'result' si éxito o 'error' si falla
        """
        try:
            if self._tools is None:
                await self._initialize_client()
            
            if not self._tools:
                self.logger.warning(
                    f"No hay herramientas disponibles para servidor MCP "
                    f"{self.server_name}"
                )
                return {
                    "error": f"No hay herramientas disponibles para "
                             f"servidor MCP {self.server_name}"
                }
            
            # Buscar herramienta por nombre
            for tool in self._tools:
                if tool.name == tool_name:
                    self.logger.info(
                        f"Ejecutando herramienta {tool_name} en servidor MCP "
                        f"{self.server_name}"
                    )
                    try:
                        # Google ADK tools usan invoke o run
                        if hasattr(tool, 'ainvoke'):
                            result = await tool.ainvoke(tool_input)
                        elif hasattr(tool, 'run'):
                            result = await tool.run(tool_input)
                        else:
                            result = tool(tool_input)
                        
                        self.logger.info(
                            f"Herramienta {tool_name} ejecutada exitosamente"
                        )
                        return {"result": result}
                        
                    except Exception as tool_error:
                        self.logger.error(
                            f"Error ejecutando herramienta {tool_name}: "
                            f"{str(tool_error)}"
                        )
                        return {
                            "error": f"Error ejecutando herramienta "
                                     f"{tool_name}: {str(tool_error)}"
                        }
            
            self.logger.warning(
                f"Herramienta {tool_name} no encontrada en servidor MCP "
                f"{self.server_name}"
            )
            return {
                "error": f"Herramienta {tool_name} no encontrada en "
                         f"servidor MCP {self.server_name}"
            }
            
        except Exception as e:
            self.logger.error(
                f"Error en execute_tool para {self.server_name}: {str(e)}"
            )
            return {"error": f"Error ejecutando herramienta {tool_name}: {str(e)}"}
    
    async def close(self) -> None:
        """
        Cierra la conexión con el servidor MCP y libera recursos.
        """
        if self._toolset and self._is_connected:
            try:
                self.logger.info(
                    f"Cerrando conexión con servidor MCP: {self.server_name}"
                )
                await self._toolset.__aexit__(None, None, None)
                self._is_connected = False
                self._toolset = None
                self._tools = None
                self.logger.info(
                    f"Conexión cerrada exitosamente para: {self.server_name}"
                )
            except Exception as e:
                self.logger.error(
                    f"Error al cerrar conexión MCP {self.server_name}: {str(e)}"
                )
    
    def get_server_name(self) -> str:
        """Retorna el nombre del servidor MCP."""
        return self.server_name
    
    def get_transport_type(self) -> str:
        """Retorna el tipo de transporte (SSE)."""
        return self.TRANSPORT_TYPE
    
    async def __aenter__(self) -> "GoogleADKMCPAdapter":
        """Soporte para uso como context manager async."""
        await self._initialize_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cierra recursos al salir del context manager."""
        await self.close()