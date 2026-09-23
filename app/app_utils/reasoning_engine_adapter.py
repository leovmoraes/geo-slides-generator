# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Serve the reasoning_engine contract over HTTP."""

import inspect
import json
import logging

from agentplatform.agent_engines.templates.adk import AdkApp
from fastapi import FastAPI, HTTPException, Request, encoders, responses
from starlette.concurrency import iterate_in_threadpool, run_in_threadpool

from app.app_utils import services
from src.services.auth_service import set_request_user_token

logger = logging.getLogger(__name__)

def _no_op_instrumentor_builder(project_id: str) -> None:
    return None

def _extract_token_from_request_and_body(request: Request, body: dict) -> None:
    """Extrai token OAuth delegado do usuário final a partir dos cabeçalhos HTTP
    ou do payload JSON enviado pelo Gemini Enterprise / Agent Engine.
    
    NOTA: O cabeçalho genérico 'authorization' NÃO deve ser capturado como token do Workspace,
    pois ele contém o token IAM da infraestrutura GCP / Vertex AI que causa RefreshError
    ao ser enviado para as APIs do Google Workspace (Drive/Slides).
    """
    token = None

    # 1. Inspecionar cabeçalhos específicos de autenticação de usuário
    for h in ["x-goog-user-token", "x-user-oauth-token", "x-goog-authenticated-user-token"]:
        val = request.headers.get(h)
        if val:
            if val.lower().startswith("bearer "):
                val = val[7:].strip()
            token = val
            logger.info(f"Token de usuário delegado detectado no cabeçalho '{h}' (prefixo: {token[:10]}...)")
            break

    # 2. Inspecionar payload JSON do Gemini Enterprise (request_json -> authorizations)
    if not token and isinstance(body, dict):
        kwargs = body.get("input") or {}
        req_json_str = kwargs.get("request_json")
        if req_json_str:
            try:
                req_data = json.loads(req_json_str) if isinstance(req_json_str, str) else req_json_str
                if isinstance(req_data, dict):
                    authorizations = req_data.get("authorizations") or {}
                    logger.info(f"Autorizações recebidas em request_json: {list(authorizations.keys())}")
                    for auth_id, auth_obj in authorizations.items():
                        tok = None
                        if isinstance(auth_obj, dict):
                            tok = auth_obj.get("access_token") or auth_obj.get("accessToken") or auth_obj.get("token")
                        elif isinstance(auth_obj, str):
                            tok = auth_obj
                        if tok:
                            token = tok
                            logger.info(f"Token OAuth extraído com sucesso de authorizations['{auth_id}'] (prefixo: {token[:10]}...)")
                            break
            except Exception as e:
                logger.warning(f"Erro ao analisar authorizations do request_json: {e}")

        # 3. Inspecionar authorizations diretamente no body ou em input
        if not token:
            for container in [body, kwargs]:
                auths = container.get("authorizations")
                if isinstance(auths, dict):
                    for auth_id, auth_obj in auths.items():
                        tok = None
                        if isinstance(auth_obj, dict):
                            tok = auth_obj.get("access_token") or auth_obj.get("accessToken") or auth_obj.get("token")
                        elif isinstance(auth_obj, str):
                            tok = auth_obj
                        if tok:
                            token = tok
                            logger.info(f"Token OAuth extraído de container direto authorizations['{auth_id}'] (prefixo: {token[:10]}...)")
                            break
                if token:
                    break

    if token:
        set_request_user_token(token)
    else:
        logger.info("Nenhum token OAuth de usuário delegado foi detectado nesta requisição.")
        set_request_user_token(None)

def attach_reasoning_engine_routes(app: FastAPI) -> None:
    """Register reasoning_engine routes that dispatch to an AdkApp."""
    runtime: AdkApp | None = None
    streaming_methods: set[str] = set()
    sync_methods: set[str] = set()

    def get_runtime() -> AdkApp:
        nonlocal runtime, streaming_methods, sync_methods
        if runtime is None:
            from app.agent import app as adk_app

            runtime = AdkApp(
                app=adk_app,
                session_service_builder=services.get_session_service,
                artifact_service_builder=services.get_artifact_service,
                instrumentor_builder=_no_op_instrumentor_builder,
            )
            runtime.set_up()
            operations = runtime.register_operations()
            streaming_methods = set(operations.get("stream", [])) | set(
                operations.get("async_stream", [])
            )
            sync_methods = set(operations.get("", [])) | set(
                operations.get("async", [])
            )
        return runtime

    def resolve_method(class_method: str, *, streaming: bool):
        rt = get_runtime()
        allowed = streaming_methods if streaming else sync_methods
        if class_method not in allowed:
            raise HTTPException(
                status_code=404,
                detail=f"Unsupported reasoning_engine method: {class_method!r}",
            )
        return getattr(rt, class_method)

    @app.post("/api/stream_reasoning_engine")
    async def stream_query(request: Request) -> responses.StreamingResponse:
        body = await request.json()
        _extract_token_from_request_and_body(request, body)
        method = resolve_method(body["class_method"], streaming=True)
        kwargs = body.get("input") or {}
        stream = (
            await method(**kwargs)
            if inspect.iscoroutinefunction(method)
            else method(**kwargs)
        )

        async def generator():
            if hasattr(stream, "__aiter__"):
                async for event in stream:
                    yield json.dumps(encoders.jsonable_encoder(event)) + "\n"
            else:
                async for event in iterate_in_threadpool(stream):
                    yield json.dumps(encoders.jsonable_encoder(event)) + "\n"

        return responses.StreamingResponse(
            content=generator(), media_type="application/json"
        )

    @app.post("/api/reasoning_engine")
    async def query(request: Request) -> responses.JSONResponse:
        body = await request.json()
        _extract_token_from_request_and_body(request, body)
        method = resolve_method(body["class_method"], streaming=False)
        kwargs = body.get("input") or {}
        if inspect.iscoroutinefunction(method):
            output = await method(**kwargs)
        else:
            output = await run_in_threadpool(method, **kwargs)
        return responses.JSONResponse(
            content=encoders.jsonable_encoder({"output": output})
        )
