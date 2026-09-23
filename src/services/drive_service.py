"""
Serviço de Operações no Google Drive
"""

import logging
from typing import Optional
from src.config import TEMPLATE_PRESENTATION_ID
from src.services.auth_service import get_drive_service

logger = logging.getLogger(__name__)

class DriveService:
    def __init__(self, drive_client=None, user_token: Optional[str] = None):
        from src.services.auth_service import _request_user_token
        active_tok = user_token or _request_user_token.get()
        if active_tok:
            logger.info(f"DriveService inicializado com credencial OAuth de usuário delegado (prefixo: {active_tok[:10]}...)")
        else:
            logger.info("DriveService inicializado sem token delegado (usará credenciais padrão / Service Account).")
        self.client = drive_client or get_drive_service(user_token=user_token)

    def clone_matrix_template(self, title: str, folder_id: Optional[str] = "root") -> str:
        """
        Clona a apresentação matriz oficial homologada da Geoambiente (TEMPLATE_PRESENTATION_ID)
        diretamente para o Google Drive do usuário final ("Meu Drive").
        """
        logger.info(f"Clonando apresentação matriz oficial {TEMPLATE_PRESENTATION_ID} como '{title}'...")
        body = {
            "name": title,
            "parents": [folder_id] if folder_id else ["root"]
        }
        try:
            copied_file = self.client.files().copy(
                fileId=TEMPLATE_PRESENTATION_ID,
                body=body,
                supportsAllDrives=True
            ).execute()
            new_id = copied_file.get("id")
            logger.info(f"Apresentação clonada da matriz oficial com sucesso! Novo ID: {new_id}")
            return new_id
        except Exception as e:
            logger.error(f"Erro ao clonar a apresentação matriz oficial ({TEMPLATE_PRESENTATION_ID}): {e}", exc_info=True)
            raise RuntimeError(
                f"Erro ao clonar a apresentação matriz oficial Geoambiente ({TEMPLATE_PRESENTATION_ID}): {e}. "
                f"Verifique se o usuário possui acesso de cópia e permissões ativas."
            )

    def share_with_domain(self, file_id: str, role: str = "writer") -> None:
        """Torna a apresentação editável para quem tiver o link no domínio."""
        try:
            self.client.permissions().create(
                fileId=file_id,
                body={"type": "anyone", "role": role},
                supportsAllDrives=True
            ).execute()
            logger.info(f"Permissão de acesso 'anyone' ({role}) configurada para {file_id}")
        except Exception as e:
            logger.warning(f"Não foi possível compartilhar como 'anyone' ({e}). Tentando compartilhar com 'domain'...")
            try:
                self.client.permissions().create(
                    fileId=file_id,
                    body={"type": "domain", "role": role},
                    supportsAllDrives=True
                ).execute()
                logger.info(f"Permissão de acesso 'domain' ({role}) configurada para {file_id}")
            except Exception as err2:
                logger.warning(f"Aviso ao ajustar permissão de compartilhamento: {err2}")
