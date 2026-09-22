"""
Serviço de Autenticação com Google Workspace e GCP
Suporta OAuth2 do Usuário Final (Token de delegação do Gemini Enterprise),
OAuth2 do Projeto (credentials.json/token.json), Service Account e ADC.
"""

import os
import logging
from typing import Optional
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

def get_google_credentials(user_token: Optional[str] = None):
    """
    Obtém credenciais válidas:
    1. Token de acesso OAuth do Usuário Final (repassado pelo Gemini Enterprise via OIDC/OAuth)
    2. token.json / credentials.json (OAuth interno da Geoambiente)
    3. Service Account Key File (GOOGLE_APPLICATION_CREDENTIALS)
    4. Application Default Credentials (ADC)
    """
    # 1. Se recebemos o token OAuth do usuário final (Gemini Enterprise)
    if user_token:
        logger.info("Utilizando credencial OAuth delegada do usuário final...")
        return Credentials(token=user_token, scopes=SCOPES)

    creds = None

    # 2. Tentar token.json existente
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

    # 3. Se houver credentials.json (OAuth do projeto geo-gemini-enterprise), executar fluxo
    if os.path.exists(CREDENTIALS_PATH):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())
            return creds
        except Exception as oauth_err:
            logger.debug(f"OAuth local não executado em ambiente sem display: {oauth_err}")

    # 4. Tentar Service Account Key
    service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if service_account_file and os.path.exists(service_account_file):
        logger.info(f"Carregando credenciais de Service Account: {service_account_file}")
        return service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES
        )

    # 5. Tentar ADC
    try:
        creds, _ = google.auth.default(scopes=SCOPES)
        return creds
    except Exception as adc_err:
        logger.warning(f"ADC warning: {adc_err}")

    return creds

def get_drive_service(user_token: Optional[str] = None):
    """Retorna cliente autenticado da Google Drive API v3"""
    credentials = get_google_credentials(user_token=user_token)
    return build("drive", "v3", credentials=credentials)

def get_slides_service(user_token: Optional[str] = None):
    """Retorna cliente autenticado da Google Slides API v1"""
    credentials = get_google_credentials(user_token=user_token)
    return build("slides", "v1", credentials=credentials)
