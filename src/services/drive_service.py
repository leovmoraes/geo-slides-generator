"""
Serviço de Operações no Google Drive
"""

import logging
from typing import Optional
from src.config import TEMPLATE_PRESENTATION_ID
from src.services.auth_service import get_drive_service

logger = logging.getLogger(__name__)

class DriveService:
    def __init__(self, drive_client=None):
        self.client = drive_client or get_drive_service()

    def clone_matrix_template(self, title: str, folder_id: Optional[str] = "root") -> str:
        """
        Clona a apresentação matriz oficial para o Drive do usuário.
        Por padrão grava na raiz 'root' (Meu Drive) para evitar problemas de permissão em diretórios somente leitura.
        """
        logger.info(f"Clonando template matriz {TEMPLATE_PRESENTATION_ID} como '{title}'...")

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
        logger.info(f"Apresentação clonada com sucesso! Novo ID: {new_id}")
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