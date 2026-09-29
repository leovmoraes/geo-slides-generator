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
        generic_names = {
            "equipe comercial geoambiente", 
            "equipe geoambiente", 
            "geoambiente cloud solutions", 
            "equipe especialista geoambiente",
            "especialista geoambiente"
        }
        
        # Identificar dados do consultor / apresentador corporativo
        has_valid_name = bool(spec.presenter_name and spec.presenter_name.strip().lower() not in generic_names)
        has_valid_email = bool(spec.presenter_email and spec.presenter_email.strip().lower() not in {"contato@geoambiente.com.br", "email@geoambiente.com.br"})

        if not has_valid_name or not has_valid_email:
            user_info = self.drive_service.get_user_info()
            if not has_valid_name and user_info.get("name"):
                spec.presenter_name = user_info.get("name")
            if not has_valid_email and user_info.get("email"):
                spec.presenter_email = user_info.get("email")

        # Se presenter_name é válido mas email ainda não, deriva automaticamente no padrão Geoambiente
        if spec.presenter_name and (not spec.presenter_email or spec.presenter_email.strip().lower() in {"contato@geoambiente.com.br", "email@geoambiente.com.br"}):
            from src.services.drive_service import format_geoambiente_email
            spec.presenter_email = format_geoambiente_email(spec.presenter_name)

        resolved_client = getattr(spec, "resolved_lead_name", None) or getattr(spec, "client_name", None) or getattr(spec, "client", None) or "Corporativo"
        file_name = f"{spec.title} - {resolved_client}"
        logger.info(f"Agente 2 (Builder) iniciando construção de '{file_name}' para {spec.resolved_presenter_name} ({spec.resolved_presenter_email})...")

        # 1. Clonar Template Matriz (ou criar nova se inacessível)
        presentation_id = self.drive_service.clone_matrix_template(title=file_name)

        # 2. Aplicar especificações visuais e de conteúdo
        final_url = self.slides_service.apply_presentation_spec(
            presentation_id=presentation_id,
            spec=spec
        )

        # 3. Garantir compartilhamento com permissão de edição para o usuário / domínio
        logger.info(f"Agente 2 configurando permissão de edição da apresentação {presentation_id}...")
        self.drive_service.share_with_domain(presentation_id, role="writer")

        logger.info(f"Agente 2 concluiu a montagem com sucesso! URL: {final_url}")
        return final_url
