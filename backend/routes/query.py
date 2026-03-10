from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
from sqlmodel import Session, select

from backend.auth.deps import get_current_user
from backend.db import get_session
from backend.llm import call_model_with_retry
from backend.models.auth_models import AnalyticsEvent, Attempt, Problem, User
from backend.storage.r2 import R2ConfigurationError, upload_bytes

router = APIRouter(tags=["query"])

PROMPTS_ROOT = Path(__file__).resolve().parents[1] / "prompts" / "modes"


def _load_prompt(mode: Literal["hint", "check_solution", "reveal"]) -> str:
    prompt_path = PROMPTS_ROOT / mode / "prompt.txt"
    try:
        return prompt_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prompt file not found for mode '{mode}'",
        ) from exc


def _to_pil_image(upload: UploadFile, data: bytes) -> Image.Image:
    try:
        return Image.open(BytesIO(data))
    except UnidentifiedImageError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid image uploaded for field '{upload.filename}'",
        ) from exc


def _safe_suffix(upload: UploadFile, default: str) -> str:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix and len(suffix) <= 10:
        return suffix
    return default


def _text_or_none(value: object, max_len: int | None = None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if max_len is not None:
        return text[:max_len]
    return text


def _record_event(
    *,
    session: Session,
    user_id: UUID,
    problem_id: UUID,
    attempt_id: UUID,
    event_type: str,
    mode: str,
    verdict: str | None = None,
    metadata_json: str | None = None,
) -> None:
    session.add(
        AnalyticsEvent(
            id=uuid4(),
            user_id=user_id,
            problem_id=problem_id,
            attempt_id=attempt_id,
            event_type=event_type,
            mode=mode,
            verdict=verdict,
            metadata_json=metadata_json,
            created_at=datetime.now(timezone.utc),
        )
    )


def _as_int_or_none(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@router.post("/query")
async def query(
    request: Request,
    problem_id: UUID = Form(...),
    mode: Literal["hint", "check_solution", "reveal"] = Form(...),
    prob_image: UploadFile = File(...),
    sol_image: UploadFile = File(...),
    drawing_data: UploadFile = File(...),
    client_request_id: str | None = Form(default=None),
    session_id: str | None = Form(default=None),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    prompt = _load_prompt(mode)
    attempt_id = uuid4()
    prompt_version = _text_or_none(f"{mode}/prompt.txt", max_len=64)
    request_id = str(uuid4())

    prob_bytes = await prob_image.read()
    sol_bytes = await sol_image.read()
    drawing_data_bytes = await drawing_data.read()

    if not prob_bytes or not sol_bytes or not drawing_data_bytes:
        raise HTTPException(
            status_code=422,
            detail="prob_image, sol_image, and drawing_data are required",
        )

    prob_pil = _to_pil_image(prob_image, prob_bytes)
    sol_pil = _to_pil_image(sol_image, sol_bytes)
    problem = session.exec(
        select(Problem).where(Problem.id == problem_id, Problem.user_id == user.id)
    ).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    header_client_request_id = request.headers.get("x-client-request-id")
    header_session_id = request.headers.get("x-session-id")
    resolved_client_request_id = _text_or_none(client_request_id or header_client_request_id, max_len=128)
    resolved_session_id = _text_or_none(session_id or header_session_id, max_len=128)
    environment = _text_or_none(os.getenv("ENVIRONMENT"), max_len=64)

    trace_metadata = {
        "feature": "notebook",
        "flow": "solve_problem",
        "requestType": mode,
        "route": "POST /query",
        "problemId": str(problem.id),
        "attemptId": str(attempt_id),
        "userId": str(user.id),
        "requestId": request_id,
        "clientRequestId": resolved_client_request_id,
        "sessionId": resolved_session_id,
        "promptVersion": prompt_version,
        "environment": environment,
        "retryCount": None,
        "success": None,
    }

    try:
        result = call_model_with_retry(
            prompt=prompt,
            prob_image=prob_pil,
            sol_image=sol_pil,
            mode=mode,
            trace_name=mode,
            trace_metadata=trace_metadata,
            trace_user_id=str(user.id),
            trace_session_id=resolved_session_id,
            request_id=request_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {exc}") from exc

    if not result:
        raise HTTPException(status_code=502, detail="LLM request failed")

    if isinstance(result, dict):
        resp_text = result.get("response_text")
        model_name = _text_or_none(result.get("model_name"), max_len=128)
        latency_seconds = float(result["latency_seconds"]) if result.get("latency_seconds") is not None else None
        tokens_in = _as_int_or_none(result.get("tokens_in"))
        tokens_out = _as_int_or_none(result.get("tokens_out"))
        tokens_thoughts = _as_int_or_none(result.get("tokens_thoughts"))
        tokens_total = _as_int_or_none(result.get("tokens_total"))
        trace_id = _text_or_none(result.get("trace_id"), max_len=128)
        observation_id = _text_or_none(result.get("observation_id"), max_len=128)
        message_id = _text_or_none(result.get("message_id"), max_len=128)
        request_id = _text_or_none(result.get("request_id"), max_len=128) or request_id
        retry_count = _as_int_or_none(result.get("retry_count"))
    else:
        resp_text = result[0] if isinstance(result, tuple) else result
        model_name = _text_or_none(result[5], max_len=128) if isinstance(result, tuple) else None
        latency_seconds = float(result[7]) if isinstance(result, tuple) and result[7] is not None else None
        tokens_in = _as_int_or_none(result[8]) if isinstance(result, tuple) else None
        tokens_out = _as_int_or_none(result[9]) if isinstance(result, tuple) else None
        tokens_thoughts = _as_int_or_none(result[10]) if isinstance(result, tuple) else None
        tokens_total = _as_int_or_none(result[11]) if isinstance(result, tuple) else None
        trace_id = None
        observation_id = None
        message_id = None
        retry_count = None

    if not isinstance(resp_text, str) or not resp_text.strip():
        raise HTTPException(status_code=502, detail="LLM request failed")

    try:
        payload = json.loads(resp_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail=f"Model returned invalid JSON: {exc}") from exc

    latency_ms = int(latency_seconds * 1000) if latency_seconds is not None else None
    error_type = _text_or_none(payload.get("error_type"), max_len=64)

    base_key = f"users/{user.id}/problems/{problem.id}/attempts/{attempt_id}"
    problem_image_key = f"{base_key}/problem_image{_safe_suffix(prob_image, '.png')}"
    solution_image_key = f"{base_key}/solution_image{_safe_suffix(sol_image, '.png')}"
    drawing_data_key = f"{base_key}/drawing_data{_safe_suffix(drawing_data, '.bin')}"

    try:
        upload_bytes(
            key=problem_image_key,
            data=prob_bytes,
            content_type=prob_image.content_type or "application/octet-stream",
        )
        upload_bytes(
            key=solution_image_key,
            data=sol_bytes,
            content_type=sol_image.content_type or "application/octet-stream",
        )
        upload_bytes(
            key=drawing_data_key,
            data=drawing_data_bytes,
            content_type=drawing_data.content_type or "application/octet-stream",
        )
    except R2ConfigurationError as exc:
        raise HTTPException(status_code=500, detail=f"R2 not configured: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to store artifacts in R2: {exc}") from exc

    attempt = Attempt(
        id=attempt_id,
        problem_id=problem.id,
        user_id=user.id,
        mode=mode,
        problem_image_key=problem_image_key,
        solution_image_key=solution_image_key,
        drawing_data_key=drawing_data_key,
        verdict=_text_or_none(payload.get("verdict"), max_len=64),
        response_type=_text_or_none(payload.get("response_type"), max_len=64),
        error_type=error_type,
        model_name=model_name,
        prompt_version=prompt_version,
        latency_ms=latency_ms,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        tokens_thoughts=tokens_thoughts,
        tokens_total=tokens_total,
        trace_id=trace_id,
        observation_id=observation_id,
        request_id=request_id,
        message_is=_text_or_none(payload.get("message_is")),
        created_at=datetime.now(timezone.utc),
    )
    session.add(attempt)
    # Ensure the parent attempt row is inserted before analytics FK inserts.
    session.flush()
    _record_event(
        session=session,
        user_id=user.id,
        problem_id=problem.id,
        attempt_id=attempt_id,
        event_type="attempt_submitted",
        mode=mode,
        verdict=attempt.verdict,
    )
    _record_event(
        session=session,
        user_id=user.id,
        problem_id=problem.id,
        attempt_id=attempt_id,
        event_type="attempt_failed" if attempt.verdict in {"incorrect", "unclear"} else "attempt_succeeded",
        mode=mode,
        verdict=attempt.verdict,
    )
    session.commit()

    response_payload = dict(payload)
    response_payload["observability"] = {
        "traceId": trace_id,
        "observationId": observation_id,
        "messageId": message_id,
        "requestId": request_id,
        "modelName": model_name,
        "promptVersion": prompt_version,
        "retryCount": retry_count,
        "clientRequestId": resolved_client_request_id,
        "sessionId": resolved_session_id,
    }
    return JSONResponse(content=response_payload)
