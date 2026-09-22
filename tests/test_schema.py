"""
Testes Unitários dos Modelos Pydantic (PresentationSpec)
"""

import pytest
from pydantic import ValidationError
from src.models.presentation_spec import CardSpec, SlideSpec, PresentationSpec

def test_card_spec_valid():
    card = CardSpec(
        tag="01",
        title="BigQuery & Analytics",
        points=["Data warehouse serverless", "Escala petabyte", "Integração Gemini"]
    )
    assert card.tag == "01"
    assert card.title == "BigQuery & Analytics"
    assert len(card.points) == 3

def test_card_spec_empty_points_fails():
    with pytest.raises(ValidationError):
        CardSpec(tag="01", title="Título", points=[])

def test_slide_spec_valid():
    slide = SlideSpec(
        section_title="ARQUITETURA",
        title="Pilares da Solução",
        cards=[
            CardSpec(tag="01", title="Card 1", points=["Ponto 1", "Ponto 2"]),
            CardSpec(tag="02", title="Card 2", points=["Ponto 3", "Ponto 4"])
        ]
    )
    assert slide.section_title == "ARQUITETURA"
    assert len(slide.cards) == 2

def test_slide_spec_max_cards():
    cards = [
        CardSpec(tag=f"0{i}", title=f"Card {i}", points=["Ponto"])
        for i in range(1, 5)
    ]
    slide = SlideSpec(title="Slide Teste", cards=cards)
    assert len(slide.cards) == 4

    # Mais de 4 cartões deve falhar a validação
    with pytest.raises(ValidationError):
        SlideSpec(
            title="Slide Excedente",
            cards=cards + [CardSpec(tag="05", title="Card 5", points=["Ponto"])]
        )

def test_presentation_spec_full():
    spec = PresentationSpec(
        title="Proposta Comercial de Dados & IA",
        subtitle="Soluções Corporativas Geoambiente & Google Cloud",
        client="AgroTech Brasil",
        author="Leonardo Moraes",
        welcome_slide=SlideSpec(
            section_title="CONTEXTO",
            title="Objetivo da Reunião",
            cards=[CardSpec(tag="01", title="Agenda", points=["Introdução", "Proposta", "Prazos"])]
        ),
        slides=[
            SlideSpec(
                section_title="SOLUÇÃO",
                title="Pilares da Proposta",
                cards=[
                    CardSpec(tag="01", title="Modernização", points=["Nuvem ágil", "Google Cloud"]),
                    CardSpec(tag="02", title="Governança", points=["Segurança total", "Padrão oficial"])
                ]
            )
        ]
    )
    assert spec.title == "Proposta Comercial de Dados & IA"
    assert spec.client == "AgroTech Brasil"
    assert spec.welcome_slide is not None
    assert len(spec.slides) == 1