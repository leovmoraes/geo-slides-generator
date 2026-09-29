"""
Agente 1: Content & Design Planner (LLM Gemini + Persona Geoambiente)
Responsável por interpretar o briefing do usuário e gerar a especificação estruturada dos slides.
"""

import os
import json
import logging
from typing import Optional
from google import genai
from google.genai import types

from src.models.presentation_spec import PresentationSpec
from src.config import GCP_PROJECT_ID, GCP_REGION, DEFAULT_GEMINI_MODEL

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """
Você é o "Gerador de Apresentações Corporativas da Geoambiente" - Especialista em Design Estratégico e Conteúdo Corporativo.

Sua missão é transformar qualquer briefing, solicitação ou tema fornecido pelo usuário em uma estrutura de apresentação corporativa de alto impacto no padrão oficial Geoambiente & Google Cloud.

[DIRETRIZES DE CONTEÚDO E DESIGN]:
1. ESTRUTURA DOS SLIDES:
   - Capa (Title, Subtitle, Client, Author, Date).
   - Slide de Boas-vindas / Contexto (welcome_slide): Apresenta o objetivo estratégico e agenda.
   - Slides de Conteúdo (slides): Cada slide DEVE conter entre 2 e 4 cartões (cards).
   - Cada cartão deve possuir uma tag de numeração ou pilar (ex: '01', '02', 'PILAR', 'BENEFÍCIO'), um título claro em Azul Google Cloud e 2 a 4 tópicos explicativos claros e profundos.

2. REGRAS VISUAIS INQUEBRÁVEIS:
   - Fundo claro sempre.
   - Seções categorizadas em caixa alta (ex: 'VISÃO GERAL', 'ARQUITETURA & PILARES', 'VALOR AGREGADO', 'CASOS DE SUCESSO').
   - Linguagem profissional, executiva e precisa.

Gere SEMPRE uma saída 100% válida e aderente ao schema PresentationSpec.
"""

class PlannerAgent:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
        self.client = genai.Client(
            vertexai=True,
            project=GCP_PROJECT_ID,
            location=GCP_REGION
        ) if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "true").lower() == "true" else genai.Client()

    def plan_presentation(
        self, 
        user_prompt: str, 
        lead_name: Optional[str] = None, 
        send_date: Optional[str] = None,
        presenter_name: Optional[str] = None,
        presenter_email: Optional[str] = None
    ) -> PresentationSpec:
        """
        Interpreta o briefing do usuário e gera a especificação completa da apresentação.
        """
        logger.info(f"Agente 1 (Planner) gerando conteúdo usando modelo '{self.model_name}'...")
        prompt_with_context = user_prompt
        if lead_name:
            prompt_with_context += f"\n[INFORMAÇÃO MANDATÓRIA]: O Nome do Lead / Cliente corporativo é: '{lead_name}'."
        if send_date:
            prompt_with_context += f"\n[INFORMAÇÃO MANDATÓRIA]: A Data de Envio da proposta é: '{send_date}'."
        if presenter_name:
            prompt_with_context += f"\n[INFORMAÇÃO MANDATÓRIA]: O Consultor/Apresentador responsável é: '{presenter_name}'."
        if presenter_email:
            prompt_with_context += f"\n[INFORMAÇÃO MANDATÓRIA]: O E-mail do Consultor/Apresentador é: '{presenter_email}'."

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt_with_context,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=PresentationSpec,
                temperature=0.2
            )
        )

        raw_text = response.text
        logger.info("Agente 1 gerou resposta estruturada. Validando schema Pydantic...")

        # Converte e valida estritamente com Pydantic
        spec_data = json.loads(raw_text)
        spec = PresentationSpec.model_validate(spec_data)
        if lead_name:
            spec.lead_name = lead_name
            spec.client_name = lead_name
            spec.client = lead_name
        if send_date:
            spec.send_date = send_date
            spec.date = send_date

        generic_names = {
            "equipe comercial geoambiente", 
            "equipe geoambiente", 
            "geoambiente cloud solutions", 
            "equipe especialista geoambiente",
            "especialista geoambiente"
        }

        if presenter_name:
            spec.presenter_name = presenter_name
        elif spec.presenter_name and spec.presenter_name.strip().lower() in generic_names:
            spec.presenter_name = None

        if presenter_email:
            spec.presenter_email = presenter_email
        elif spec.presenter_email and spec.presenter_email.strip().lower() in {"contato@geoambiente.com.br", "email@geoambiente.com.br"}:
            spec.presenter_email = None

        logger.info(f"Especificação validada: '{spec.title}' para o lead '{spec.resolved_lead_name}' na data '{spec.resolved_send_date}'. Apresentador: '{spec.resolved_presenter_name}' ({spec.resolved_presenter_email})")
        return spec