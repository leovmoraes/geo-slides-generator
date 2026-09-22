"""
Serviço de Autenticação com Google Workspace e GCP
Suporta OAuth2 Interno do Projeto (credentials.json), Service Account e ADC
"""

import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.auth

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive"
]

TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "token.json")
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "credentials.json")

def get_google_credentials():
    """
    Obtém credenciais válidas do Google Workspace na seguinte ordem:
    1. token.json / credentials.json (OAuth interno da Geoambiente - sem bloqueio de app externo)
    2. Service Account Key File (GOOGLE_APPLICATION_CREDENTIALS)
    3. Application Default Credentials (ADC)
    """
    creds = None

    # 1. Tentar token.json existente
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_PATH, "w") as token:
                    token.write(creds.to_json())
                return creds
        except Exception as e:
            logger.debug(f"Erro ao carregar token.json: {e}")

    # 2. Se houver credentials.json (OAuth do projeto geo-gemini-enterprise), executar fluxo
    if os.path.exists(CREDENTIALS_PATH):
        try:
            logger.info("Iniciando fluxo OAuth2 com credentials.json do projeto...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())
            logger.info("Novo token.json gravado com sucesso!")
            return creds
        except Exception as oauth_err:
            logger.warning(f"Erro no fluxo OAuth2: {oauth_err}")

    # 3. Tentar Service Account Key
    service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if service_account_file and os.path.exists(service_account_file):
        logger.info(f"Carregando credenciais de Service Account: {service_account_file}")
        return service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES
        )

    # 4. Tentar ADC
    try:
        creds, _ = google.auth.default(scopes=SCOPES)
        return creds
    except Exception as adc_err:
        logger.warning(f"ADC warning: {adc_err}")

    return creds

def get_drive_service():
    """Retorna cliente autenticado da Google Drive API v3"""
    credentials = get_google_credentials()
    return build("drive", "v3", credentials=credentials)

def get_slides_service():
    """Retorna cliente autenticado da Google Slides API v1"""
    credentials = get_google_credentials()
    return build("slides", "v1", credentials=credentials)