import json
from unittest.mock import MagicMock
from app.app_utils.reasoning_engine_adapter import _extract_token_from_request_and_body
from src.services.auth_service import _request_user_token, set_request_user_token

def test_extract_token_from_request_json_authorizations():
    request = MagicMock()
    request.headers = {}
    
    body = {
        "class_method": "streaming_agent_run_with_events",
        "input": {
            "request_json": json.dumps({
                "message": {"role": "user", "parts": [{"text": "Gerar proposta comercial"}]},
                "authorizations": {
                    "slides-agent-auth": {
                        "access_token": "ya29.test_token_123456"
                    }
                }
            })
        }
    }
    
    _extract_token_from_request_and_body(request, body)
    assert _request_user_token.get() == "ya29.test_token_123456"
    
    # Reset
    set_request_user_token(None)

def test_extract_token_from_header():
    request = MagicMock()
    request.headers = {"x-goog-user-token": "Bearer ya29.header_token_abcdef"}
    body = {"class_method": "query", "input": {}}
    
    _extract_token_from_request_and_body(request, body)
    assert _request_user_token.get() == "ya29.header_token_abcdef"
    
    # Reset
    set_request_user_token(None)
