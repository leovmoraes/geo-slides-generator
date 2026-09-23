"""
Serviço de Autenticação com Google Workspace e GCP
Suporta OAuth2 do Usuário Final (Token de delegação repassado via cabeçalho HTTP/ADK),
OAuth2 do Projeto (credentials.json/token.json), Service Account e ADC.
"""

import os
import logging
import contextvars
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

# ContextVar para propagar o token de autorização da requisição do Gemini Enterprise
_request_user_token: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_user_token", default=None)

def set_request_user_token(token: Optional[str]):
    """Define o token do usuário autenticado no contexto da requisição atual."""
    _request_user_token.set(token)

def get_google_credentials(user_token: Optional[str] = None, force_service_account: bool = False):
    """
    Obtém credenciais válidas:
    1. Token de acesso OAuth do Usuário Final (se não force_service_account)
    2. token.json / credentials.json (OAuth interno da Geoambiente)
    3. Service Account Key File (GOOGLE_APPLICATION_CREDENTIALS)
    4. Application Default Credentials (ADC)
    """
    if not force_service_account:
        token = user_token or _request_user_token.get()
        if token:
            logger.info("Utilizando credencial OAuth delegada do usuário final...")
            return Credentials(token=token, scopes=SCOPES)

    creds = None

    # 2. Tentar token.json existente (se não forçado a Service Account)
    if not force_service_account and os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            if creds and creds.valid:
                return creds
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(TOKEN_PATH, "w") as token_file:
                    token_file.write(creds.to_json())
                return creds
        except Exception as e:
            logger.debug(f"Erro ao carregar token.json: {e}")

    # 3. Tentar Service Account Key
    service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if service_account_file and os.path.exists(service_account_file):
        logger.info(f"Carregando credenciais de Service Account: {service_account_file}")
        return service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES
        )

    # 4. Tentar ADC (Application Default Credentials / Service Account da plataforma)
    try:
        creds, _ = google.auth.default(scopes=SCOPES)
        logger.info("Utilizando credenciais ADC (Application Default Credentials).")
        return creds
    except Exception as adc_err:
        logger.warning(f"ADC warning: {adc_err}")

    return creds

def get_drive_service(user_token: Optional[str] = None, force_service_account: bool = False):
    """Retorna cliente autenticado da Google Drive API v3"""
    credentials = get_google_credentials(user_token=user_token, force_service_account=force_service_account)
    return build("drive", "v3", credentials=credentials)

def get_slides_service(user_token: Optional[str] = None, force_service_account: bool = False):
    """Retorna cliente autenticado da Google Slides API v1"""
    credentials = get_google_credentials(user_token=user_token, force_service_account=force_service_account)
    return build("slides", "v1", credentials=credentials)
