"""
Testes Unitários do Orquestrador de Workflow Multi-Agente
"""

from unittest.mock import MagicMock
from src.models.presentation_spec import CardSpec, SlideSpec, PresentationSpec
from src.workflow.orchestrator import SlideMasterWorkflow

def test_workflow_orchestration():
    mock_spec = PresentationSpec(
        title="Modernização de Dados no GCP",
        subtitle="Soluções Corporativas Geoambiente & Google Cloud",
        client="Cliente Teste",
        author="Equipe Geoambiente",
        slides=[
            SlideSpec(
                section_title="VISÃO GERAL",
                title="Destaques da Solução",
                cards=[
                    CardSpec(tag="01", title="Card Teste", points=["Ponto 1", "Ponto 2"])
                ]
            )
        ]
    )

    mock_planner = MagicMock()
    mock_planner.plan_presentation.return_value = mock_spec

    mock_builder = MagicMock()
    mock_builder.build_presentation.return_value = {
        "presentation_id": "test_presentation_123",
        "url": "https://docs.google.com/presentation/d/test_presentation_123/edit",
        "title": mock_spec.title,
        "client": mock_spec.client,
        "total_content_slides": 1
    }

    workflow = SlideMasterWorkflow(
        planner_agent=mock_planner,
        builder_agent=mock_builder
    )

    result = workflow.run("Gerar apresentação sobre Modernização para Cliente Teste")

    assert result["status"] == "success"
    assert result["presentation_id"] == "test_presentation_123"
    assert result["url"] == "https://docs.google.com/presentation/d/test_presentation_123/edit"
    assert result["title"] == "Modernização de Dados no GCP"
    assert result["client"] == "Cliente Teste"
    assert result["total_content_slides"] == 1

    mock_planner.plan_presentation.assert_called_once_with("Gerar apresentação sobre Modernização para Cliente Teste")
    mock_builder.build_presentation.assert_called_once_with(mock_spec)