from unittest.mock import MagicMock
from src.agents.builder_agent import BuilderAgent
from src.models.presentation_spec import PresentationSpec, SlideSpec, CardSpec

def test_builder_agent_execution_and_share():
    mock_drive = MagicMock()
    mock_drive.clone_matrix_template.return_value = "pres_123"
    
    mock_slides = MagicMock()
    mock_slides.apply_presentation_spec.return_value = "https://docs.google.com/presentation/d/pres_123/edit"
    
    builder = BuilderAgent(drive_service=mock_drive, slides_service=mock_slides)
    
    # Spec without client_name, but with client
    spec = PresentationSpec(
        title="Proposta IA",
        client="GeoCliente",
        slides=[
            SlideSpec(
                title="Slide 1",
                cards=[CardSpec(title="Card 1", points=["Ponto 1"])]
            )
        ]
    )
    
    url = builder.build_presentation(spec)
    
    # Verify title used resolved client
    mock_drive.clone_matrix_template.assert_called_once_with(title="Proposta IA - GeoCliente")
    # Verify spec applied
    mock_slides.apply_presentation_spec.assert_called_once_with(presentation_id="pres_123", spec=spec)
    # Verify share_with_domain called
    mock_drive.share_with_domain.assert_called_once_with("pres_123", role="writer")
    assert url == "https://docs.google.com/presentation/d/pres_123/edit"
