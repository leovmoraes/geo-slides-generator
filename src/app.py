"""
Definição oficial do Agente usando o Google Agent Development Kit (ADK).
Compatível 100% nativo com Gemini Enterprise, Agent Platform e Agent Runtime.
"""

import logging
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from src.workflow.orchestrator import SlideMasterWorkflow

logger = logging.getLogger(__name__)

# Instância única do workflow
_workflow = None

def _get_workflow() -> SlideMasterWorkflow:
    global _workflow
    if _workflow is None:
        _workflow = SlideMasterWorkflow()
    return _workflow

def generate_slides_presentation(prompt: str) -> dict:
    """
    Gera uma apresentação completa e editável no Google Slides no padrão oficial Geoambiente & Google Cloud.
    
    Args:
        prompt: O briefing detalhado da apresentação, tema, cliente, pilares e escopo.
        
    Returns:
        Um dicionário contendo o link do Google Slides, título, cliente e número de slides.
    """
    logger.info(f"Tool generate_slides_presentation acionada com prompt: {prompt}")
    workflow = _get_workflow()
    result = workflow.run(prompt)
    return {
        "title": result.title,
        "client_name": result.client_name,
        "slide_count": result.slide_count,
        "presentation_url": result.presentation_url,
        "presentation_id": result.presentation_id,
        "execution_time_seconds": round(result.execution_time_seconds, 2)
    }

def create_root_agent() -> Agent:
    """Cria e retorna a instância oficial do Agente ADK."""
    return Agent(
        name="Gerador_Apresentacoes_Geoambiente",
        model="gemini-3.7-flash",
        description="Agente corporativo especialista na criação e automação de apresentações e propostas comerciais no Google Slides da Geoambiente e Google Cloud.",
        instruction="""Você é o Gerador de Apresentações Corporativas da Geoambiente.
Sua missão é criar apresentações e propostas comerciais executivas no padrão visual oficial Geoambiente & Google Cloud.

[DIRETRIZES]:
1. Sempre que o usuário solicitar uma proposta, apresentação, deck ou conjunto de slides, você DEVE acionar a ferramenta `generate_slides_presentation` passando o briefing fornecido pelo usuário.
2. Após a ferramenta concluir a geração dos slides, responda de maneira executiva e elegante, destacando o Título, o Cliente e disponibilizando o link direto editável do Google Slides para o usuário clicar e abrir.""",
        tools=[FunctionTool(generate_slides_presentation)]
    )

root_agent = create_root_agent()
