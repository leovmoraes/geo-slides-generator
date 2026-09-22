"""
Wrapper do Agente para o Vertex AI Agent Runtime (Reasoning Engine / ADK).
Expõe query() e stream_query() consumidos pelo Gemini Enterprise.
"""

import logging
from typing import Dict, Any, Optional
from src.workflow.orchestrator import SlideMasterWorkflow

logger = logging.getLogger(__name__)

class SlideAgentApp:
    """Aplicação compatível com Vertex AI Agent Runtime / Reasoning Engine / Gemini Enterprise."""

    def __init__(self):
        self.workflow = None

    def set_up(self):
        """Inicialização executada no runtime gerenciado do Vertex AI."""
        self.workflow = SlideMasterWorkflow()

    def _extract_prompt(self, prompt: Optional[str] = None, message: Optional[str] = None, **kwargs) -> str:
        """Extrai o texto do briefing a partir de múltiplos formatos possíveis do Gemini Enterprise."""
        if prompt:
            return str(prompt)
        if message:
            return str(message)
        for key in ["input", "query", "text", "content"]:
            if key in kwargs and kwargs[key]:
                return str(kwargs[key])
        if kwargs:
            return " ".join(f"{k}: {v}" for k, v in kwargs.items())
        return "Gerar apresentação institucional corporativa no padrão Geoambiente"

    def query(self, prompt: Optional[str] = None, message: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Ponto de entrada síncrono."""
        if not self.workflow:
            self.set_up()

        user_prompt = self._extract_prompt(prompt=prompt, message=message, **kwargs)
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
            "title": result.title,
            "client_name": result.client_name,
            "presentation_id": result.presentation_id,
            "presentation_url": result.presentation_url,
            "slide_count": result.slide_count,
            "execution_time_seconds": round(result.execution_time_seconds, 2)
        }

    def stream_query(self, prompt: Optional[str] = None, message: Optional[str] = None, **kwargs):
        """Ponto de entrada em Streaming exigido pelo chat do Gemini Enterprise."""
        res = self.query(prompt=prompt, message=message, **kwargs)
        yield res
