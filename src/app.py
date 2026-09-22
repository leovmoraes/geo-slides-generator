"""
Wrapper do Agente para o Vertex AI Agent Runtime (Reasoning Engine / ADK).
Expõe o método query padronizado consumido pelo Gemini Enterprise.
"""

import logging
from typing import Dict, Any
from src.workflow.orchestrator import SlideMasterWorkflow

logger = logging.getLogger(__name__)

class SlideAgentApp:
    """Aplicação compatível com Vertex AI Agent Runtime / Reasoning Engine."""

    def __init__(self):
        self.workflow = None

    def set_up(self):
        """Inicialização executada no runtime gerenciado do Vertex AI."""
        self.workflow = SlideMasterWorkflow()

    def query(self, prompt: str) -> Dict[str, Any]:
        """
        Ponto de entrada chamado pelo Gemini Enterprise / Agent Platform.
        """
        if not self.workflow:
            self.set_up()

        result = self.workflow.run(prompt)

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
