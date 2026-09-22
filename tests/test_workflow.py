from unittest.mock import MagicMock
from src.workflow.orchestrator import SlideMasterWorkflow
from src.models.presentation_spec import PresentationSpec, SlideSpec, CardSpec

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
    mock_builder.build_presentation.return_value = "https://docs.google.com/presentation/d/test_presentation_123/edit"

    workflow = SlideMasterWorkflow(
        planner=mock_planner,
        builder=mock_builder
    )

    result = workflow.run("Prompt de teste")

    assert result.title == "Modernização de Dados no GCP"
    assert result.client_name == "Cliente Teste"
    assert result.presentation_id == "test_presentation_123"
    assert result.presentation_url == "https://docs.google.com/presentation/d/test_presentation_123/edit"
