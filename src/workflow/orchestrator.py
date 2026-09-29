"""
Orquestrador do Workflow Multi-Agente
Coordena a passagem de bastão entre o Agente 1 (Planner) e o Agente 2 (Builder).
"""

import time
import logging
from typing import Optional
from dataclasses import dataclass
from src.agents.planner_agent import PlannerAgent
from src.agents.builder_agent import BuilderAgent

logger = logging.getLogger(__name__)

@dataclass
class WorkflowResult:
    presentation_url: str
    presentation_id: str
    title: str
    client_name: str
    slide_count: int
    execution_time_seconds: float

class SlideMasterWorkflow:
    def __init__(self, planner: Optional[PlannerAgent] = None, builder: Optional[BuilderAgent] = None, user_token: Optional[str] = None):
        self.planner = planner or PlannerAgent()
        self.builder = builder or BuilderAgent(user_token=user_token)

    def run(
        self, 
        user_prompt: str, 
        user_token: Optional[str] = None,
        lead_name: Optional[str] = None,
        send_date: Optional[str] = None,
        presenter_name: Optional[str] = None,
        presenter_email: Optional[str] = None
    ) -> WorkflowResult:
        start_time = time.time()
        logger.info(f"=== [INICIANDO WORKFLOW MULTI-AGENTE ADK] ===")
        logger.info(f"Prompt do Usuário: '{user_prompt}'")
        if lead_name:
            logger.info(f"Nome do Lead informado: '{lead_name}'")
        if send_date:
            logger.info(f"Data de Envio informada: '{send_date}'")
        if presenter_name:
            logger.info(f"Apresentador informado: '{presenter_name}'")
        if presenter_email:
            logger.info(f"E-mail do Apresentador informado: '{presenter_email}'")

        # 1. Agente 1: Planeja o conteúdo e a estrutura visual
        logger.info("--> [ETAPA 1/2]: Executando Agente 1 (Content & Design Planner)...")
        spec = self.planner.plan_presentation(
            user_prompt, 
            lead_name=lead_name, 
            send_date=send_date,
            presenter_name=presenter_name,
            presenter_email=presenter_email
        )

        # 2. Agente 2: Constrói os slides determinísticos clonando a matriz oficial
        logger.info("--> [ETAPA 2/2]: Executando Agente 2 (Slide Master Builder)...")
        builder = BuilderAgent(user_token=user_token) if user_token else self.builder
        presentation_url = builder.build_presentation(spec)

        # 3. Extrai presentation_id da URL e dados de saída
        presentation_id = presentation_url.split("/d/")[1].split("/edit")[0]
        resolved_client = getattr(spec, "resolved_lead_name", None) or getattr(spec, "client_name", None) or getattr(spec, "client", None) or "Cliente Corporativo"
        elapsed = time.time() - start_time

        logger.info(f"=== [WORKFLOW CONCLUÍDO EM {elapsed:.2f}s] ===")
        return WorkflowResult(
            presentation_url=presentation_url,
            presentation_id=presentation_id,
            title=spec.title,
            client_name=resolved_client,
            slide_count=len(spec.slides) + 1,
            execution_time_seconds=elapsed
        )
