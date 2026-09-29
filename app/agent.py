"""
Agente oficial do ADK para geração de apresentações corporativas Geoambiente & Google Cloud.
Suporta autenticação delegada do Usuário Final via OAuth do Gemini Enterprise.
"""

import logging
from typing import Optional, Dict, Any, List
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

def generate_slides_presentation(
    prompt: str, 
    lead_name: Optional[str] = None, 
    presenter_name: Optional[str] = None,
    presenter_email: Optional[str] = None,
    send_date: Optional[str] = None, 
    tool_context=None
) -> str:
    """
    Gera uma apresentação corporativa completa e editável no Google Slides seguindo a identidade visual oficial da Geoambiente e Google Cloud.
    
    Args:
        prompt: Briefing da apresentação, tema, pilares estratégicos e escopo desejado.
        lead_name: Nome do Lead / Cliente corporativo destinatário da proposta comercial (substitui 'Nome do Lead' na capa oficial).
        presenter_name: Nome do consultor / apresentador corporativo Geoambiente responsável pela proposta (substitui 'Nome Sobrenome' no slide final).
        presenter_email: E-mail corporativo do consultor Geoambiente (ex: nome.sobrenome@geoambiente.com.br). Se omitido, é derivado automaticamente do presenter_name.
        send_date: Data de envio da proposta no formato DD/MM/AAAA ou mês/ano (substitui '[Data de Envio]' na capa oficial). Se omitido, utiliza a data corrente.
        tool_context: Contexto do ADK contendo a autenticação delegada do usuário final.
        
    Returns:
        Uma mensagem formatada com o título, cliente e o link editável do Google Slides pronto.
    """
    logger.info(f"Tool generate_slides_presentation chamada. Lead: '{lead_name}', Apresentador: '{presenter_name}' ({presenter_email}), Data: '{send_date}', Prompt: {prompt}")
    
    # 1. Extração do Token OAuth do Usuário Final (repassado pelo Gemini Enterprise)
    user_token = None

    # 1.1 ContextVar propagado pelo adaptador HTTP da Reasoning Engine
    try:
        from src.services.auth_service import _request_user_token
        ctx_token = _request_user_token.get()
        if ctx_token:
            user_token = ctx_token
            logger.info(f"Token OAuth obtido via ContextVar da requisição (prefixo: {user_token[:10]}...)")
    except Exception as ctx_err:
        logger.debug(f"Erro ao ler ContextVar de token: {ctx_err}")

    # 1.2 Inspecionar tool_context.state (onde AdkApp armazena request.authorizations)
    if not user_token and tool_context and hasattr(tool_context, "state") and tool_context.state:
        try:
            logger.info(f"Inspecionando tool_context.state. Chaves disponíveis: {list(tool_context.state.keys())}")
            for k, v in tool_context.state.items():
                tok = None
                if isinstance(v, str) and (v.startswith("ya29.") or "auth" in k.lower() or "token" in k.lower()):
                    tok = v
                elif isinstance(v, dict):
                    tok = v.get("access_token") or v.get("accessToken") or v.get("token")
                if tok:
                    user_token = tok
                    logger.info(f"Token OAuth extraído com sucesso de tool_context.state['{k}'] (prefixo: {user_token[:10]}...)")
                    break
        except Exception as state_err:
            logger.warning(f"Erro ao inspecionar tool_context.state: {state_err}")

    # 1.3 Inspecionar _invocation_context e outros atributos do tool_context
    if not user_token and tool_context:
        try:
            inv_ctx = getattr(tool_context, "_invocation_context", None)
            if inv_ctx and hasattr(inv_ctx, "credential_by_key"):
                for k, c in inv_ctx.credential_by_key.items():
                    if hasattr(c, "oauth2") and c.oauth2:
                        user_token = getattr(c.oauth2, "access_token", None) or getattr(c.oauth2, "token", None)
                        if user_token:
                            logger.info(f"Token OAuth do usuário extraído de credential_by_key['{k}']")
                            break
                    if hasattr(c, "http") and c.http and hasattr(c.http, "credentials"):
                        user_token = getattr(c.http.credentials, "token", None)
                        if user_token:
                            logger.info(f"Token Bearer do usuário extraído de credential_by_key['{k}']")
                            break
                    if isinstance(c, dict):
                        user_token = c.get("access_token") or c.get("token") or (c.get("oauth2", {}).get("access_token") if isinstance(c.get("oauth2"), dict) else None)
                        if user_token:
                            logger.info(f"Token de usuário extraído de dict em credential_by_key['{k}']")
                            break

            # 1.4 Tentar chaves comuns usando get_credential(key)
            if not user_token and hasattr(tool_context, "get_credential"):
                for candidate_key in ["slides-agent-auth", "google-slides-oauth", "oauth2", "google", "default", "auth"]:
                    try:
                        c = tool_context.get_credential(candidate_key)
                        if c:
                            if hasattr(c, "oauth2") and c.oauth2:
                                user_token = getattr(c.oauth2, "access_token", None) or getattr(c.oauth2, "token", None)
                            elif hasattr(c, "http") and c.http and hasattr(c.http, "credentials"):
                                user_token = getattr(c.http.credentials, "token", None)
                            elif isinstance(c, dict):
                                user_token = c.get("access_token") or c.get("token")
                            elif isinstance(c, str):
                                user_token = c
                            if user_token:
                                logger.info(f"Token de usuário extraído via get_credential('{candidate_key}')")
                                break
                    except Exception as get_err:
                        logger.debug(f"Tentativa com chave '{candidate_key}' falhou: {get_err}")

            # 1.5 Tentar atributos diretos em tool_context
            if not user_token:
                for attr in ["credentials", "credential", "auth_response", "auth"]:
                    val = getattr(tool_context, attr, None)
                    if val and not callable(val):
                        if isinstance(val, dict):
                            user_token = val.get("access_token") or val.get("token")
                        elif isinstance(val, str):
                            user_token = val
                        if user_token:
                            logger.info(f"Token extraído via atributo '{attr}'!")
                            break
        except Exception as e:
            logger.warning(f"Aviso ao extrair credencial do tool_context: {e}")

    if not user_token:
        from src.services.auth_service import TOKEN_PATH
        import os
        if os.path.exists(TOKEN_PATH):
            logger.info("user_token não veio no request, mas token.json local está disponível para desenvolvimento.")
        else:
            logger.error("Nenhum token OAuth de usuário delegado foi detectado na chamada em ambiente de produção.")
            return (
                "⚠️ **Autorização do Google Workspace necessária**\n\n"
                "Para criar a apresentação corporativa oficial diretamente no seu Google Drive seguindo o padrão oficial da Geoambiente, "
                "é necessário autorizar o agente no Gemini Enterprise (autorização `slides-agent-auth`).\n\n"
                "Por favor, autorize a extensão na barra de ferramentas ou configurações do Gemini Enterprise e envie sua solicitação novamente."
            )

    # 2. Execução do Workflow
    workflow = _get_workflow()
    result = workflow.run(
        prompt, 
        user_token=user_token,
        lead_name=lead_name,
        send_date=send_date,
        presenter_name=presenter_name,
        presenter_email=presenter_email
    )
    
    return (
        f"### ✅ Apresentação gerada com sucesso no padrão oficial Geoambiente!\n\n"
        f"- **Título:** {result.title}\n"
        f"- **Lead / Cliente:** {result.client_name}\n"
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

[PRÉ-REQUISITOS OBRIGATÓRIOS ANTES DE GERAR A APRESENTAÇÃO]:
Para personalizar a proposta comercial com precisão institucional, você DEVE coletar os seguintes dados antes de acionar a ferramenta:

1. **Nome do Lead (Cliente / Empresa)**:
   - Se o usuário NÃO informou a empresa ou cliente destinatário no pedido/briefing, PERGUNTE educadamente: "Para qual cliente ou empresa lead será esta proposta comercial?".

2. **Apresentador / Consultor Geoambiente (Slide Final de Contato)**:
   - Como nem sempre a pessoa que gera a apresentação é quem vai apresentá-la (pode ser gerada para outro executivo de contas ou colega de equipe), PERGUNTE: "Quem será o consultor/apresentador responsável por esta proposta? (Informe o Nome e E-mail, ou confirme se deseja usar o seu próprio contato)".
   - Se o usuário disser que é para ele mesmo (ou confirmar), chame a ferramenta deixando `presenter_name` vazio (None), e o sistema detectará automaticamente a identidade dele via Google Workspace OAuth.
   - Se o usuário informar o nome (ex: "Leonardo Moraes"), passe em `presenter_name`. O e-mail corporativo será gerado automaticamente no padrão `nome.sobrenome@geoambiente.com.br` caso não seja explicitado um e-mail diferente.

3. **Data de Envio**:
   - Se o usuário especificou uma data (ex: '29/09/2026' ou 'Outubro/2026'), use-a. Se não especificou, você pode sugerir ou usar a data atual.

[DIRETRIZES DE EXECUÇÃO]:
1. Assim que tiver o briefing e os pré-requisitos alinhados com o usuário (Lead e Apresentador), acione IMEDIATAMENTE a ferramenta `generate_slides_presentation` passando:
   - `prompt`: O briefing completo da proposta comercial.
   - `lead_name`: O nome do lead / cliente identificado.
   - `presenter_name`: O nome do consultor/apresentador informado pelo usuário (ou None se for usar o próprio usuário).
   - `presenter_email`: O e-mail do consultor (se informado).
   - `send_date`: A data de envio informada ou desejada (se omitida, o sistema usará a data de hoje).
2. Após a execução da ferramenta, responda ao usuário de forma executiva, cordial e sucinta, fornecendo o link direto do Google Slides retornado pela ferramenta.""",
    tools=[generate_slides_presentation],
)

app = App(
    root_agent=root_agent,
    name="app",
)
