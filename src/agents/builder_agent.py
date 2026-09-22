"""
Agente 2 / Tool: Slide Master Builder (Motor Determinístico de Slides)
Responsável por clonar a matriz oficial e montar a apresentação no Google Slides API.
"""

import logging
from typing import Dict, Any
from src.models.presentation_spec import PresentationSpec
from src.services.drive_service import DriveService
from src.services.slides_service import SlidesService

logger = logging.getLogger(__name__)

class BuilderAgent:
    def __init__(self, drive_service: DriveService = None, slides_service: SlidesService = None):
        self.drive_service = drive_service or DriveService()
        self.slides_service = slides_service or SlidesService()

    def build_presentation(self, spec: PresentationSpec) -> Dict[str, Any]:
        """
        Executa a montagem determinística dos slides a partir do schema validado.
        """
        file_name = f"{spec.title} - {spec.client}" if spec.client else spec.title
        logger.info(f"Agente 2 (Builder) iniciando construção de '{file_name}'...")

        # 1. Clonar apresentação matriz oficial para o Drive
        presentation_id = self.drive_service.clone_matrix_template(title=file_name)

        # 2. Aplicar especificações de Capa, Boas-vindas, Cartões e Encerramento
        presentation_url = self.slides_service.apply_presentation_spec(
            presentation_id=presentation_id,
            spec=spec
        )

        # 3. Compartilhar com o domínio se aplicável
        self.drive_service.share_with_domain(file_id=presentation_id, role="writer")

        result = {
            "presentation_id": presentation_id,
            "url": presentation_url,
            "title": spec.title,
            "client": spec.client,
            "total_content_slides": len(spec.slides) + (1 if spec.welcome_slide else 0)
        }

        logger.info(f"Agente 2 concluiu a montagem com sucesso! URL: {presentation_url}")
        return result