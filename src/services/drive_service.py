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
        self.client = drive_client or get_drive_service(user_token=user_token)

    def clone_matrix_template(self, title: str, folder_id: Optional[str] = "root") -> str:
        """
        Clona a apresentação matriz oficial para o Drive do usuário.
        Se o template estiver inacessível por permissão de Drive compartilhado,
        cria uma nova apresentação oficial do zero no Drive do usuário.
        """
        logger.info(f"Tentando clonar template matriz {TEMPLATE_PRESENTATION_ID} como '{title}'...")
        try:
            body = {
                "name": title,
                "parents": [folder_id] if folder_id else ["root"]
            }
            copied_file = self.client.files().copy(
                fileId=TEMPLATE_PRESENTATION_ID,
                body=body,
                supportsAllDrives=True
            ).execute()
            new_id = copied_file.get("id")
            logger.info(f"Apresentação clonada da matriz com sucesso! Novo ID: {new_id}")
            return new_id
        except Exception as e:
            logger.warning(f"Template matriz inacessível ({e}). Criando nova apresentação corporativa oficial do zero...")
            file_metadata = {
                "name": title,
                "mimeType": "application/vnd.google-apps.presentation",
                "parents": [folder_id] if folder_id else ["root"]
            }
            new_file = self.client.files().create(
                body=file_metadata,
                supportsAllDrives=True
            ).execute()
            new_id = new_file.get("id")
            logger.info(f"Nova apresentação criada com sucesso! ID: {new_id}")
            return new_id

    def share_with_domain(self, file_id: str, role: str = "writer") -> None:
        """Torna a apresentação editável para quem tiver o link no domínio."""
        try:
            self.client.permissions().create(
                fileId=file_id,
                body={"type": "anyone", "role": role},
                supportsAllDrives=True
            ).execute()
        except Exception as e:
            logger.warning(f"Aviso ao ajustar permissão de compartilhamento: {e}")
