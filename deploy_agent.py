"""
Script de Deploy para o Vertex AI Agent Runtime (Deployments on Agent Runtime).
Publica o agente diretamente no projeto geo-gemini-enterprise.
"""

import os
import vertexai
from vertexai.preview import reasoning_engines
from src.app import SlideAgentApp
from src.config import GCP_PROJECT_ID

# Configurações do Deploy
DEPLOY_LOCATION = "us-central1"  # Região padrão dos agentes na Agent Platform
DISPLAY_NAME = "Gerador de Apresentações Geoambiente"
DESCRIPTION = "Agente corporativo para criação automática de apresentações e propostas no Google Slides via Gemini 3.7 Flash."

# Dependências que o runtime do Vertex AI instalará no container gerenciado
REQUIREMENTS = [
    "google-genai>=2.0.0",
    "google-api-python-client>=2.0.0",
    "google-auth>=2.0.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0"
]

def deploy():
    print("=== [INICIANDO DEPLOY NO VERTEX AI AGENT RUNTIME] ===")
    print(f"Projeto: {GCP_PROJECT_ID}")
    print(f"Região: {DEPLOY_LOCATION}")
    print(f"Nome do Agente: {DISPLAY_NAME}")

    # Inicializa o SDK do Vertex AI
    vertexai.init(
        project=GCP_PROJECT_ID,
        location=DEPLOY_LOCATION
    )

    app = SlideAgentApp()

    # Cria o deployment gerenciado no Agent Runtime
    print("\nCriando o Reasoning Engine / Agent Deployment no Vertex AI...")
    remote_agent = reasoning_engines.ReasoningEngine.create(
        reasoning_engine=app,
        requirements=REQUIREMENTS,
        display_name=DISPLAY_NAME,
        description=DESCRIPTION,
        extra_packages=["./src"]
    )

    print("\n============================================================")
    print("  ✅ AGENTE PUBLICADO NO AGENT RUNTIME COM SUCESSO!")
    print("============================================================")
    print(f"Resource Name: {remote_agent.resource_name}")
    print(f"Display Name:  {DISPLAY_NAME}")
    print("\nEle já está visível na tela 'Deployments on Agent Runtime'!")
    print("============================================================\n")

if __name__ == "__main__":
    deploy()
