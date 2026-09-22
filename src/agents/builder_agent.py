"""
Agente 2: Slide Master Builder (Automação Determinística via Drive & Slides API)
"""

import logging
from typing import Optional
from src.models.presentation_spec import PresentationSpec
from src.services.drive_service import DriveService
from src.services.slides_service import SlidesService

logger = logging.getLogger(__name__)

class BuilderAgent:
    def __init__(self, drive_service: Optional[DriveService] = None, slides_service: Optional[SlidesService] = None, user_token: Optional[str] = None):
        self.drive_service = drive_service or DriveService(user_token=user_token)
        self.slides_service = slides_service or SlidesService(user_token=user_token)

    def build_presentation(self, spec: PresentationSpec) -> str:
        """
        Executa a montagem completa da apresentação:
        1. Clona a apresentação matriz oficial para o Drive do usuário.
        2. Atualiza a capa, sumário e slides institucionais.
        3. Insere os slides de conteúdo com cards, cores e tipografia oficiais.
        4. Retorna a URL final da apresentação editável.
        """
        file_name = f"{spec.title} - {spec.client_name}"
        logger.info(f"Agente 2 (Builder) iniciando construção de '{file_name}'...")

        # 1. Clonar Template Matriz
        presentation_id = self.drive_service.clone_matrix_template(title=file_name)

        # 2. Aplicar especificações visuais e de conteúdo
        final_url = self.slides_service.apply_presentation_spec(
            presentation_id=presentation_id,
            spec=spec
        )

        logger.info(f"Agente 2 concluiu a montagem com sucesso! URL: {final_url}")
        return final_url
