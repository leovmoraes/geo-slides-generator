"""
Agente oficial do ADK para geração de apresentações corporativas Geoambiente & Google Cloud.
Suporta autenticação delegada do Usuário Final via OAuth do Gemini Enterprise.
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

def generate_slides_presentation(prompt: str, tool_context=None) -> str:
    """
    Gera uma apresentação corporativa completa e editável no Google Slides seguindo a identidade visual oficial da Geoambiente e Google Cloud.
    
    Args:
        prompt: Briefing da apresentação, tema, cliente, pilares estratégicos e escopo desejado.
        tool_context: Contexto do ADK contendo a autenticação delegada do usuário final.
        
    Returns:
        Uma mensagem formatada com o título, cliente e o link editável do Google Slides pronto.
    """
    logger.info(f"Tool generate_slides_presentation chamada com prompt: {prompt}")
    
    # 1. Extração do Token OAuth do Usuário Final (se fornecido pelo Gemini Enterprise)
    user_token = None
    if tool_context:
        try:
            if hasattr(tool_context, "get_credential") and tool_context.get_credential():
                cred = tool_context.get_credential()
                if isinstance(cred, dict):
                    user_token = cred.get("token") or cred.get("access_token")
                elif isinstance(cred, str):
                    user_token = cred
            elif hasattr(tool_context, "get_auth_response") and tool_context.get_auth_response():
                auth_resp = tool_context.get_auth_response()
                if isinstance(auth_resp, dict):
                    user_token = auth_resp.get("access_token") or auth_resp.get("token")
        except Exception as e:
            logger.debug(f"Aviso ao extrair credencial do tool_context: {e}")

    # 2. Execução do Workflow
    workflow = _get_workflow()
    result = workflow.run(prompt, user_token=user_token)
    
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
