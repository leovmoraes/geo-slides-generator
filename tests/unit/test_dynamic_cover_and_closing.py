from unittest.mock import MagicMock
from src.models.presentation_spec import PresentationSpec, SlideSpec, CardSpec
from src.services.slides_service import SlidesService
from src.services.drive_service import DriveService

def test_cover_requests_replacement():
    spec = PresentationSpec(
        title="Modernização Digital",
        lead_name="AgroTech Brasil",
        send_date="15/10/2026",
        presenter_name="Leonardo Moraes",
        presenter_email="leonardo.moraes@geoambiente.com.br",
        slides=[
            SlideSpec(
                title="Visão Geral",
                cards=[CardSpec(tag="01", title="Cloud", points=["Ponto 1"])]
            )
        ]
    )
    
    service = SlidesService(slides_client=MagicMock())
    requests = service._build_cover_requests("slide_0", spec)
    
    replaced_texts = {r["replaceAllText"]["containsText"]["text"]: r["replaceAllText"]["replaceText"] for r in requests if "replaceAllText" in r}
    
    assert replaced_texts["Nome do Lead"] == "AgroTech Brasil"
    assert replaced_texts["[Data de Envio]"] == "15/10/2026"
    assert replaced_texts["Data de Envio"] == "15/10/2026"

def test_closing_requests_replacement():
    spec = PresentationSpec(
        title="Proposta Corporativa",
        presenter_name="Leonardo Moraes",
        presenter_email="leonardo.moraes@geoambiente.com.br",
        slides=[
            SlideSpec(
                title="Visão Geral",
                cards=[CardSpec(tag="01", title="Cloud", points=["Ponto 1"])]
            )
        ]
    )
    
    service = SlidesService(slides_client=MagicMock())
    requests = service._build_closing_requests("slide_last", spec)
    
    replaced_texts = {r["replaceAllText"]["containsText"]["text"]: r["replaceAllText"]["replaceText"] for r in requests if "replaceAllText" in r}
    
    assert replaced_texts["Nome Sobrenome"] == "Leonardo Moraes"
    assert replaced_texts["email@geoambiente.com.br"] == "leonardo.moraes@geoambiente.com.br"

def test_drive_service_user_info_parsing():
    mock_client = MagicMock()
    mock_client.about().get().execute.return_value = {
        "user": {
            "displayName": "Leonardo Vieira de Moraes",
            "emailAddress": "leonardo.moraes@geoambiente.com.br"
        }
    }
    
    drive_service = DriveService(drive_client=mock_client)
    info = drive_service.get_user_info()
    
    assert info["name"] == "Leonardo Vieira de Moraes"
    assert info["email"] == "leonardo.moraes@geoambiente.com.br"

def test_format_geoambiente_email():
    from src.services.drive_service import format_geoambiente_email
    assert format_geoambiente_email("Leonardo Moraes") == "leonardo.moraes@geoambiente.com.br"
    assert format_geoambiente_email("Leonardo Vieira de Moraes") == "leonardo.moraes@geoambiente.com.br"
    assert format_geoambiente_email("Idenilson Oliveira") == "idenilson.oliveira@geoambiente.com.br"
    assert format_geoambiente_email("leonardo.moraes@geoambiente.com.br") == "leonardo.moraes@geoambiente.com.br"
    assert format_geoambiente_email("") == "contato@geoambiente.com.br"

def test_presenter_resolution_and_fallback():
    # Caso 1: Nome informado sem e-mail -> deriva e-mail institucional
    spec1 = PresentationSpec(
        title="Proposta",
        presenter_name="Leonardo Moraes",
        slides=[SlideSpec(title="S", cards=[CardSpec(title="C", points=["P"])])]
    )
    assert spec1.resolved_presenter_name == "Leonardo Moraes"
    assert spec1.resolved_presenter_email == "leonardo.moraes@geoambiente.com.br"

    # Caso 2: Nome genérico do LLM -> limpa e não assume placeholder
    spec2 = PresentationSpec(
        title="Proposta",
        presenter_name="Geoambiente Cloud Solutions",
        slides=[SlideSpec(title="S", cards=[CardSpec(title="C", points=["P"])])]
    )
    assert spec2.resolved_presenter_name == "Equipe Geoambiente"
    assert spec2.resolved_presenter_email == "contato@geoambiente.com.br"

def test_builder_overrides_generic_llm_placeholder():
    from src.agents.builder_agent import BuilderAgent
    
    spec = PresentationSpec(
        title="Proposta",
        presenter_name="Geoambiente Cloud Solutions",
        presenter_email="contato@geoambiente.com.br",
        slides=[SlideSpec(title="S", cards=[CardSpec(title="C", points=["P"])])]
    )
    
    mock_drive = MagicMock()
    mock_drive.get_user_info.return_value = {
        "name": "Leonardo Vieira de Moraes",
        "email": "leonardo.moraes@geoambiente.com.br"
    }
    mock_drive.clone_matrix_template.return_value = "fake_id"
    mock_slides = MagicMock()
    mock_slides.apply_presentation_spec.return_value = "https://docs.google.com/presentation/d/fake_id/edit"
    
    builder = BuilderAgent(drive_service=mock_drive, slides_service=mock_slides)
    builder.build_presentation(spec)
    
    assert spec.presenter_name == "Leonardo Vieira de Moraes"
    assert spec.presenter_email == "leonardo.moraes@geoambiente.com.br"


def test_dynamic_content_starts_at_slide_6():
    """Valida que slides dinâmicos são inseridos a partir do índice 5 (Slide 6)."""
    mock_client = MagicMock()
    # Simula apresentação com 14 slides (como a matriz oficial)
    mock_client.presentations().get().execute.return_value = {
        "slides": [{"objectId": f"slide_{i}"} for i in range(14)]
    }
    
    spec = PresentationSpec(
        title="Proposta",
        slides=[
            SlideSpec(title="Slide Dinâmico 1", cards=[CardSpec(title="C1", points=["P1"])]),
            SlideSpec(title="Slide Dinâmico 2", cards=[CardSpec(title="C2", points=["P2"])]),
        ]
    )
    
    service = SlidesService(slides_client=mock_client)
    service.apply_presentation_spec("test_presentation_id", spec)
    
    # Verifica chamadas ao batchUpdate
    assert mock_client.presentations().batchUpdate.called
    call_args = mock_client.presentations().batchUpdate.call_args[1]
    requests = call_args["body"]["requests"]
    
    create_slide_requests = [r["createSlide"] for r in requests if "createSlide" in r]
    assert len(create_slide_requests) == 2
    # Slide 1 deve ser inserido no insertionIndex 5 (ou seja, Slide 6 na apresentação)
    assert create_slide_requests[0]["insertionIndex"] == 5
    # Slide 2 deve ser inserido no insertionIndex 6 (Slide 7 na apresentação)
    assert create_slide_requests[1]["insertionIndex"] == 6


