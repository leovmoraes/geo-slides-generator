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

    def run(self, user_prompt: str, user_token: Optional[str] = None) -> WorkflowResult:
        start_time = time.time()
        logger.info(f"=== [INICIANDO WORKFLOW MULTI-AGENTE ADK] ===")
        logger.info(f"Prompt do Usuário: '{user_prompt}'")

        # 1. Agente 1: Planeja o conteúdo e a estrutura visual
        logger.info("--> [ETAPA 1/2]: Executando Agente 1 (Content & Design Planner)...")
        spec = self.planner.plan_presentation(user_prompt)

        # 2. Agente 2: Constrói os slides determinísticos clonando a matriz oficial
        logger.info("--> [ETAPA 2/2]: Executando Agente 2 (Slide Master Builder)...")
        builder = BuilderAgent(user_token=user_token) if user_token else self.builder
        presentation_url = builder.build_presentation(spec)

        # 3. Extrai presentation_id da URL
        presentation_id = presentation_url.split("/d/")[1].split("/edit")[0]
        elapsed = time.time() - start_time

        logger.info(f"=== [WORKFLOW CONCLUÍDO EM {elapsed:.2f}s] ===")
        return WorkflowResult(
            presentation_url=presentation_url,
            presentation_id=presentation_id,
            title=spec.title,
            client_name=spec.client_name,
            slide_count=len(spec.slides) + 1,
            execution_time_seconds=elapsed
        )
