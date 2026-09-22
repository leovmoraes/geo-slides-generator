"""
Modelos Pydantic para Estruturação Estrita das Apresentações Geoambiente
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CardSpec(BaseModel):
    """Especificação de um Cartão Individual dentro do Slide"""
    tag: str = Field(
        default="01",
        description="Identificador visual em Laranja Geoambiente (#F58120), ex: '01', 'PILAR', 'BENEFÍCIO'"
    )
    title: str = Field(
        ...,
        description="Título principal do cartão em Azul Google Cloud (#1A73E8)"
    )
    points: List[str] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Lista de 2 a 4 tópicos explicativos"
    )
    bullets: Optional[List[str]] = Field(
        default=None,
        description="Alias opcional para tópicos explicativos"
    )


class SlideSpec(BaseModel):
    """Especificação de um Slide Estruturado em Cartões"""
    section_title: str = Field(
        default="VISÃO GERAL",
        description="Categoria ou nome da seção em caixa alta no cabeçalho (#F58120)"
    )
    section_category: Optional[str] = Field(
        default=None,
        description="Alias opcional para categoria de seção"
    )
    title: str = Field(
        ...,
        description="Título principal do slide em Poppins (#202124)"
    )
    cards: List[CardSpec] = Field(
        ...,
        min_length=1,
        max_length=4,
        description="Lista de 1 a 4 cartões de conteúdo para o slide"
    )


class WelcomeSlideSpec(BaseModel):
    """Slide de boas-vindas / contexto inicial"""
    objective: str = Field(
        default="Apresentar soluções estratégicas corporativas",
        description="Objetivo principal da apresentação"
    )
    agenda_items: List[str] = Field(
        default_factory=list,
        description="Tópicos da agenda"
    )


class PresentationSpec(BaseModel):
    """Especificação Completa da Apresentação Corporativa Homologada"""
    title: str = Field(
        ...,
        description="Título principal da apresentação na Capa oficial"
    )
    subtitle: str = Field(
        default="Soluções Corporativas Geoambiente & Google Cloud",
        description="Subtítulo ou objetivo da apresentação"
    )
    client: Optional[str] = Field(
        default=None,
        description="Nome do cliente ou parceiro de negócios"
    )
    client_name: Optional[str] = Field(
        default=None,
        description="Alias opcional para nome do cliente"
    )
    author: str = Field(
        default="Equipe Especialista Geoambiente",
        description="Nome do autor ou departamento responsável"
    )
    date: Optional[str] = Field(
        default=None,
        description="Data da apresentação no formato DD/MM/AAAA"
    )
    welcome_slide: Optional[SlideSpec] = Field(
        default=None,
        description="Slide opcional de Boas-vindas / Contexto e Agenda"
    )
    slides: List[SlideSpec] = Field(
        ...,
        min_length=1,
        description="Lista de slides intermediários estruturados em cartões"
    )
