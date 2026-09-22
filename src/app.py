"""
Wrapper do Agente compatível com todos os protocolos de invocação:
- ADK Agent Runtime (streaming_agent_run_with_events, agent_run_with_events, agent_run, streaming_agent_run)
- Vertex AI Reasoning Engine (stream_query, query)
"""

import logging
from typing import Dict, Any, Optional
from src.workflow.orchestrator import SlideMasterWorkflow

logger = logging.getLogger(__name__)

class SlideAgentApp:
    """Aplicação completa compatível com Gemini Enterprise e Google ADK."""

    def __init__(self):
        self.workflow = None

    def set_up(self):
        """Inicialização executada no runtime gerenciado do Vertex AI."""
        self.workflow = SlideMasterWorkflow()

    def _extract_prompt(self, *args, **kwargs) -> str:
        """Extrai o texto do briefing a partir de qualquer formato do Gemini Enterprise/ADK."""
        if args and args[0]:
            return str(args[0])
        
        # Procura em campos comuns do ADK / Gemini Enterprise
        for key in ["prompt", "message", "query", "input", "text", "content", "user_message"]:
            if key in kwargs and kwargs[key]:
                val = kwargs[key]
                if isinstance(val, dict):
                    return val.get("content", val.get("text", str(val)))
                if isinstance(val, list) and val:
                    first = val[0]
                    if isinstance(first, dict):
                        return first.get("content", first.get("text", str(first)))
                    return str(first)
                return str(val)

        # Se kwargs contiver mensagens em formato de lista (messages=[...])
        if "messages" in kwargs and kwargs["messages"]:
            last_msg = kwargs["messages"][-1]
            if isinstance(last_msg, dict):
                return last_msg.get("content", last_msg.get("text", str(last_msg)))
            return str(last_msg)

        if kwargs:
            return " ".join(f"{k}: {v}" for k, v in kwargs.items())
        return "Gerar proposta comercial corporativa no padrão Geoambiente"

    def _execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execução unificada do pipeline."""
        if not self.workflow:
            self.set_up()

        user_prompt = self._extract_prompt(*args, **kwargs)
        logger.info(f"Executando workflow para o prompt: {user_prompt}")
        result = self.workflow.run(user_prompt)

        response_text = (
            f"### ✅ Apresentação gerada com sucesso!\n\n"
            f"**Título:** {result.title}\n"
            f"**Cliente:** {result.client_name}\n"
            f"**Total de Slides:** {result.slide_count}\n\n"
            f"🔗 **[Clique aqui para abrir no Google Slides]({result.presentation_url})**"
        )

        return {
            "output": response_text,
            "text": response_text,
            "content": response_text,
            "title": result.title,
            "client_name": result.client_name,
            "presentation_id": result.presentation_id,
            "presentation_url": result.presentation_url,
            "slide_count": result.slide_count,
            "execution_time_seconds": round(result.execution_time_seconds, 2)
        }

    # 1. Métodos ADK / Gemini Enterprise
    def streaming_agent_run_with_events(self, *args, **kwargs):
        """Método de streaming chamado nativamente pelo Gemini Enterprise (ADK)."""
        res = self._execute(*args, **kwargs)
        yield res

    def agent_run_with_events(self, *args, **kwargs):
        """Método síncrono com eventos do ADK."""
        return self._execute(*args, **kwargs)

    def streaming_agent_run(self, *args, **kwargs):
        """Método de streaming padrão do ADK."""
        res = self._execute(*args, **kwargs)
        yield res

    def agent_run(self, *args, **kwargs):
        """Método síncrono padrão do ADK."""
        return self._execute(*args, **kwargs)

    # 2. Métodos Vertex AI Reasoning Engine padrão
    def stream_query(self, *args, **kwargs):
        """Método stream_query do Reasoning Engine."""
        res = self._execute(*args, **kwargs)
        yield res

    def query(self, *args, **kwargs) -> Dict[str, Any]:
        """Método query do Reasoning Engine."""
        return self._execute(*args, **kwargs)
