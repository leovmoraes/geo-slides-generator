"""
Orquestrador do Workflow Multi-Agente ADK
Gerencia o fluxo sequencial: Briefing -> Agente 1 (Planner) -> Schema -> Agente 2 (Builder) -> URL
"""

import time
import logging
from typing import Dict, Any, Optional
from src.models.presentation_spec import PresentationSpec
from src.agents.planner_agent import PlannerAgent
from src.agents.builder_agent import BuilderAgent

logger = logging.getLogger(__name__)

class SlideMasterWorkflow:
    def __init__(self, planner_agent: Optional[PlannerAgent] = None, builder_agent: Optional[BuilderAgent] = None):
        self.planner = planner_agent or PlannerAgent()
        self.builder = builder_agent or BuilderAgent()

    def run(self, prompt: str) -> Dict[str, Any]:
        """
        Executa o workflow completo de ponta a ponta.
        """
        start_time = time.time()
        logger.info(f"=== [INICIANDO WORKFLOW MULTI-AGENTE ADK] ===")
        logger.info(f"Prompt do Usuário: '{prompt}'")

        # ETAPA 1: Agente 1 gera o conteúdo e estrutura em formato Pydantic
        logger.info("--> [ETAPA 1/2]: Executando Agente 1 (Content & Design Planner)...")
        spec: PresentationSpec = self.planner.plan_presentation(prompt)

        # ETAPA 2: Agente 2 clona a matriz oficial e renderiza os slides determinísticos
        logger.info("--> [ETAPA 2/2]: Executando Agente 2 (Slide Master Builder)...")
        build_result = self.builder.build_presentation(spec)

        elapsed = round(time.time() - start_time, 2)
        logger.info(f"=== [WORKFLOW CONCLUÍDO EM {elapsed}s] ===")

        return {
            "status": "success",
            "message": "Apresentação corporativa gerada com sucesso seguindo 100% o padrão Geoambiente!",
            "presentation_id": build_result["presentation_id"],
            "url": build_result["url"],
            "title": build_result["title"],
            "client": build_result["client"],
            "total_content_slides": build_result["total_content_slides"],
            "spec": spec.model_dump(),
            "elapsed_seconds": elapsed
        }