"""
Agente oficial do ADK para geração de apresentações corporativas Geoambiente & Google Cloud.
"""

import logging
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from src.workflow.orchestrator import SlideMasterWorkflow

logger = logging.getLogger(__name__)

MODEL = "gemini-3.7-flash"

# Instância única do workflow
_workflow = None

def _get_workflow() -> SlideMasterWorkflow:
    global _workflow
    if _workflow is None:
        _workflow = SlideMasterWorkflow()
    return _workflow

def generate_slides_presentation(prompt: str) -> str:
    """
    Gera uma apresentação corporativa completa e editável no Google Slides seguindo a identidade visual oficial da Geoambiente e Google Cloud.
    
    Args:
        prompt: Briefing da apresentação, tema, cliente, pilares estratégicos e escopo desejado.
        
    Returns:
        Uma mensagem formatada com o título, cliente e o link editável do Google Slides pronto.
    """
    logger.info(f"Tool generate_slides_presentation chamada com prompt: {prompt}")
    workflow = _get_workflow()
    result = workflow.run(prompt)
    
    return (
        f"### ✅ Apresentação gerada com sucesso no padrão oficial Geoambiente!\n\n"
        f"- **Título:** {result.title}\n"
        f"- **Cliente:** {result.client_name}\n"
        f"- **Total de Slides:** {result.slide_count}\n"
        f"- **Tempo de Criação:** {round(result.execution_time_seconds, 2)}s\n\n"
        f"🔗 **[Abrir Apresentação no Google Slides]({result.presentation_url})**"
    )

root_agent = Agent(
    name="slides_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""Você é o Gerador de Apresentações Corporativas da Geoambiente.
Sua missão é gerar apresentações, decks e propostas comerciais completas no padrão corporativo oficial Geoambiente & Google Cloud.

[INSTRUÇÕES ESSENCIAIS]:
1. Sempre que o usuário solicitar a criação de uma proposta, deck, apresentação ou conjunto de slides, acione IMEDIATAMENTE a ferramenta `generate_slides_presentation` passando o briefing do usuário.
2. Após a execução da ferramenta, responda ao usuário de forma executiva, fornecendo o link direto do Google Slides retornado pela ferramenta.""",
    tools=[generate_slides_presentation],
)

app = App(
    root_agent=root_agent,
    name="app",
)
