"""
Script de Deploy oficial para o Vertex AI Agent Runtime usando Google ADK.
Publica o agente oficial diretamente no projeto geo-gemini-enterprise.
"""

import os
import vertexai
from vertexai.preview import reasoning_engines
from app.agent import root_agent
from src.config import GCP_PROJECT_ID
from src.services.auth_service import get_google_credentials

# Configurações do Deploy
DEPLOY_LOCATION = "us-central1"
STAGING_BUCKET = "gs://geo-gemini-artifacts-presales"
DISPLAY_NAME = "Gerador de Apresentações Geoambiente"
DESCRIPTION = "Agente corporativo oficial para criação automática de apresentações no Google Slides via Gemini 3.5 Flash e Google ADK."

# Dependências completas para o Agent Runtime do Vertex AI
REQUIREMENTS = [
    "google-adk>=2.9.0",
    "google-genai>=2.0.0",
    "google-api-python-client>=2.0.0",
    "google-auth>=2.0.0",
    "google-auth-oauthlib>=1.0.0",
    "google-auth-httplib2>=0.2.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "cloudpickle>=3.0.0"
]

def deploy():
    print("=== [INICIANDO DEPLOY NO VERTEX AI AGENT RUNTIME (GOOGLE ADK)] ===")
    print(f"Projeto:        {GCP_PROJECT_ID}")
    print(f"Região:         {DEPLOY_LOCATION}")
    print(f"Staging Bucket: {STAGING_BUCKET}")
    print(f"Nome do Agente: {DISPLAY_NAME}")

    # Inicializa o SDK do Vertex AI
    creds = get_google_credentials()
    vertexai.init(
        project=GCP_PROJECT_ID,
        location=DEPLOY_LOCATION,
        staging_bucket=STAGING_BUCKET,
        credentials=creds
    )

    # Cria o deployment do Agente ADK no Agent Runtime
    print("\nCriando o deployment oficial do ADK no Agent Runtime...")
    remote_agent = reasoning_engines.ReasoningEngine.create(
        reasoning_engine=root_agent,
        requirements=REQUIREMENTS,
        display_name=DISPLAY_NAME,
        description=DESCRIPTION,
        extra_packages=["./src", "./app"]
    )

    print("\n============================================================")
    print("  ✅ AGENTE ADK PUBLICADO COM SUCESSO NO AGENT RUNTIME!")
    print("============================================================")
    print(f"Resource Name: {remote_agent.resource_name}")
    print(f"Display Name:  {DISPLAY_NAME}")
    print("\nEle já está pronto e compatível nativamente com o Gemini Enterprise!")
    print("============================================================\n")

if __name__ == "__main__":
    deploy()
