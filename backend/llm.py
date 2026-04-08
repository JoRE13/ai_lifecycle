from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
from pydantic import BaseModel, Field

try:
    from langfuse import Langfuse
except Exception:  # pragma: no cover - defensive import guard for platform/library mismatch
    Langfuse = None

load_dotenv(Path(__file__).resolve().parent / ".env")

logger = logging.getLogger(__name__)

# Gemini 3 Flash Preview paid-tier rates used elsewhere in this project docs.
INPUT_COST_PER_1M_TOKENS_USD = float(os.getenv("INPUT_COST_PER_1M_TOKENS_USD", "0.50"))
OUTPUT_COST_PER_1M_TOKENS_USD = float(os.getenv("OUTPUT_COST_PER_1M_TOKENS_USD", "3.00"))

# Alert if estimated per-call cost jumps above this delta compared to previous call.
COST_SPIKE_THRESHOLD_USD = float(os.getenv("COST_SPIKE_THRESHOLD_USD", "0.005"))

# In-memory baseline for simple spike detection (first call seeds baseline only).
previous_estimated_call_cost_usd: float | None = None


class LLMResponse(BaseModel):
    verdict: str
    response_type: str
    message_is: str
    error_type: str
    error_step: str | None = None
    correct_approach: str | None = None
    error_confidence: float | None = None
    all_readable: bool
    ambiguous_regions: list["LegibilityRegion"] = Field(default_factory=list)
    missing_parts: list[str] = Field(default_factory=list)
    clarity_warning: bool | None = None
    missing_justification: bool | None = None
    concept_tag: str | None = None
    suggested_justification: str | None = None
    step_reference: str | None = None
    can_skip: bool | None = None


class ModeV3Response(BaseModel):
    verdict: str
    response_type: str
    message_is: str


class LegibilityRegion(BaseModel):
    page: int | None = None
    snippet: str | None = None
    reason: str | None = None


class LegibilityInterpretedStep(BaseModel):
    page: int | None = None
    text: str


class LegibilityResponse(BaseModel):
    all_readable: bool
    ambiguous_regions: list[LegibilityRegion] = Field(default_factory=list)
    missing_parts: list[str] = Field(default_factory=list)
    message_is: str | None = None
    reading_confidence: float | None = None
    interpreted_text: str | None = None
    interpreted_steps: list[LegibilityInterpretedStep] = Field(default_factory=list)


class DeferredErrorResponse(BaseModel):
    topic: str | None = None
    subtopic: str | None = None
    wrong_step: str | None = None
    correct_step: str | None = None
    error_type: str
    confidence: float | None = None


def is_langfuse_enabled() -> bool:
    return langfuse is not None


def _build_langfuse_client() -> Langfuse | None:
    """Create a Langfuse client when credentials are available.

    Returns None if tracing is not configured or initialization fails.
    """
    if Langfuse is None:
        logger.warning("Langfuse disabled: import failed")
        return None

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")

    if not public_key or not secret_key:
        logger.info("Langfuse disabled: LANGFUSE_PUBLIC_KEY/SECRET_KEY not set")
        return None

    # Support both host-style and base-url-style env naming.
    host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL")

    try:
        if host:
            return Langfuse(public_key=public_key, secret_key=secret_key, host=host)
        return Langfuse(public_key=public_key, secret_key=secret_key)
    except Exception:
        logger.exception("Langfuse initialization failed")
        return None


def _build_genai_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    return genai.Client(api_key=api_key)


langfuse = _build_langfuse_client()
client = _build_genai_client()


def _trace_event(trace: Any, name: str, metadata: dict[str, Any]) -> None:
    if trace is None:
        return
    try:
        if hasattr(trace, "event"):
            trace.event(name=name, metadata=metadata)
        elif hasattr(trace, "create_event"):
            trace.create_event(name=name, metadata=metadata)
        elif hasattr(langfuse, "create_event"):
            langfuse.create_event(name=name, metadata=metadata)
        else:
            logger.warning("No compatible Langfuse event API found")
    except Exception:
        logger.exception("Failed to send Langfuse trace event")


def _extract_entity_id(entity: Any) -> str | None:
    if entity is None:
        return None
    for attr in ("id", "trace_id", "observation_id"):
        value = getattr(entity, attr, None)
        if value:
            return str(value)
    if isinstance(entity, dict):
        for key in ("id", "trace_id", "observation_id"):
            value = entity.get(key)
            if value:
                return str(value)
    return None


def _estimate_call_cost_usd(*, tokens_in: int, tokens_out: int, tokens_thoughts: int) -> float:
    safe_tokens_in = 0 if tokens_in is None else tokens_in
    safe_tokens_out = 0 if tokens_out is None else tokens_out
    safe_tokens_thoughts = 0 if tokens_thoughts is None else tokens_thoughts
    billed_output_tokens = max(0, safe_tokens_out) + max(0, safe_tokens_thoughts)
    return (max(0, safe_tokens_in) / 1_000_000.0) * INPUT_COST_PER_1M_TOKENS_USD + (
        billed_output_tokens / 1_000_000.0
    ) * OUTPUT_COST_PER_1M_TOKENS_USD


def _warn_if_cost_spike(current_cost_usd: float) -> None:
    global previous_estimated_call_cost_usd
    if previous_estimated_call_cost_usd is None:
        previous_estimated_call_cost_usd = current_cost_usd
        return

    increase = current_cost_usd - previous_estimated_call_cost_usd
    if increase > COST_SPIKE_THRESHOLD_USD:
        logger.warning(
            "COST SPIKE DETECTED\nPrevious cost: $%.6f\nCurrent cost: $%.6f\nIncrease: $%.6f",
            previous_estimated_call_cost_usd,
            current_cost_usd,
            increase,
        )
    previous_estimated_call_cost_usd = current_cost_usd


def _start_trace(
    *,
    prompt: str,
    mode: str,
    name: str,
    request_id: str | None,
    user_id: str | None,
    session_id: str | None,
    metadata: dict[str, Any] | None,
) -> tuple[Any, str | None]:
    if langfuse is None:
        return None, None
    trace_input = {"prompt": prompt, "mode": mode}
    base_kwargs: dict[str, Any] = {"name": name, "input": trace_input}
    if metadata:
        base_kwargs["metadata"] = metadata
    try:
        # Legacy clients with explicit trace objects.
        if hasattr(langfuse, "trace"):
            trace_kwargs = dict(base_kwargs)
            if user_id:
                trace_kwargs["user_id"] = user_id
            if session_id:
                trace_kwargs["session_id"] = session_id
            if request_id:
                trace_kwargs["id"] = request_id
            trace = langfuse.trace(**trace_kwargs)
            return trace, _extract_entity_id(trace) or request_id
        if hasattr(langfuse, "create_trace"):
            trace_kwargs = dict(base_kwargs)
            if user_id:
                trace_kwargs["user_id"] = user_id
            if session_id:
                trace_kwargs["session_id"] = session_id
            if request_id:
                trace_kwargs["id"] = request_id
            trace = langfuse.create_trace(**trace_kwargs)
            return trace, _extract_entity_id(trace) or request_id

        # Langfuse v3 OTEL-style clients: use spans and attach trace metadata explicitly.
        if hasattr(langfuse, "start_span"):
            trace_context = None
            if hasattr(langfuse, "create_trace_id"):
                if request_id:
                    trace_context = {"trace_id": langfuse.create_trace_id(seed=request_id)}
                else:
                    trace_context = {"trace_id": langfuse.create_trace_id()}
            trace = langfuse.start_span(trace_context=trace_context, **base_kwargs)
            if hasattr(trace, "update_trace"):
                trace.update_trace(
                    user_id=user_id,
                    session_id=session_id,
                    metadata=metadata,
                    input=trace_input,
                )
            resolved_trace_id = (
                getattr(trace, "trace_id", None)
                or _extract_entity_id(trace)
                or (trace_context or {}).get("trace_id")
                or request_id
            )
            return trace, resolved_trace_id
        logger.warning("No compatible Langfuse trace/span API found")
        return None, None
    except Exception:
        logger.exception("Failed to start Langfuse trace/span")
        return None, None


def _trace_generation(
    trace: Any,
    *,
    model: str,
    prompt: str,
    output: str,
    mode: str,
    latency: float,
    tokens_in: int,
    tokens_out: int,
    tokens_total: int,
    tokens_thoughts: int,
) -> str | None:
    if trace is None:
        return None

    try:
        if hasattr(trace, "generation"):
            generation = trace.generation(
                name="gemini-generation",
                model=model,
                input=prompt,
                output=output,
                usage={
                    "prompt_tokens": tokens_in,
                    "completion_tokens": tokens_out,
                    "total_tokens": tokens_total,
                },
                metadata={
                    "mode": mode,
                    "latency": latency,
                    "thought_tokens": tokens_thoughts,
                },
            )
            return _extract_entity_id(generation)

        if hasattr(trace, "start_generation"):
            generation = trace.start_generation(
                name="gemini-generation",
                model=model,
                input=prompt,
                output=output,
                usage_details={
                    "input": tokens_in,
                    "output": tokens_out,
                    "total": tokens_total,
                },
                metadata={
                    "mode": mode,
                    "latency": latency,
                    "thought_tokens": tokens_thoughts,
                },
            )
            if hasattr(generation, "end"):
                generation.end()
            return _extract_entity_id(generation)

        logger.warning("No compatible Langfuse generation API found")
    except Exception:
        logger.exception("Failed to send Langfuse generation")
    return None


def _end_trace(trace: Any, *, output: Any = None, metadata: dict[str, Any] | None = None) -> None:
    if trace is None:
        return
    try:
        # Langfuse v3 span API: update trace attrs first, then end span.
        if hasattr(trace, "update_trace") and hasattr(trace, "end"):
            trace.update_trace(output=output, metadata=metadata)
            trace.end()
            return
        if hasattr(trace, "end"):
            kwargs: dict[str, Any] = {}
            if output is not None:
                kwargs["output"] = output
            if metadata:
                kwargs["metadata"] = metadata
            trace.end(**kwargs)
            return
        if hasattr(trace, "update"):
            kwargs = {}
            if output is not None:
                kwargs["output"] = output
            if metadata:
                kwargs["metadata"] = metadata
            trace.update(**kwargs)
    except Exception:
        logger.exception("Failed to finalize Langfuse trace")


def submit_langfuse_score(
    *,
    name: str,
    value: float,
    observation_id: str | None = None,
    trace_id: str | None = None,
    comment: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> tuple[bool, str | None]:
    if langfuse is None:
        return False, "Langfuse client not initialized"
    if not observation_id and not trace_id:
        return False, "Missing trace_id and observation_id"

    base_kwargs: dict[str, Any] = {
        "name": name,
        "value": value,
    }
    if comment:
        base_kwargs["comment"] = comment
    if metadata:
        base_kwargs["metadata"] = metadata

    target_kwargs: list[dict[str, str]] = []
    if trace_id and observation_id:
        target_kwargs.append({"trace_id": trace_id, "observation_id": observation_id})
        target_kwargs.append({"traceId": trace_id, "observationId": observation_id})
    if observation_id:
        target_kwargs.append({"observation_id": observation_id})
        target_kwargs.append({"observationId": observation_id})
    if trace_id:
        target_kwargs.append({"trace_id": trace_id})
        target_kwargs.append({"traceId": trace_id})

    score_methods = []
    if hasattr(langfuse, "score"):
        score_methods.append(langfuse.score)
    if hasattr(langfuse, "create_score"):
        score_methods.append(langfuse.create_score)

    last_error: str | None = None
    for method in score_methods:
        for target in target_kwargs:
            try:
                method(**base_kwargs, **target)
                if hasattr(langfuse, "flush"):
                    langfuse.flush()
                return True, None
            except TypeError:
                continue
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                logger.warning("Langfuse score submission attempt failed: %s", last_error)
                continue

    if last_error:
        logger.error("Langfuse score submission failed after all attempts: %s", last_error)
        return False, last_error
    return False, "No compatible Langfuse score method/parameters found"


def _build_multipage_contents(*, prompt: str, prob_image: Any, sol_images: Sequence[Any]) -> list[Any]:
    sol_images_list = list(sol_images)
    if not sol_images_list:
        raise ValueError("At least one solution image is required")

    contents: list[Any] = [prompt, "Problem image:", prob_image]
    total_solution_pages = len(sol_images_list)
    for page_index, page_image in enumerate(sol_images_list, start=1):
        contents.append(f"Student solution page {page_index} of {total_solution_pages} (ordered).")
        contents.append(page_image)
    return contents


def _call_model_with_retry_internal(
    *,
    prompt: str,
    prob_image: Any,
    sol_images: Sequence[Any],
    mode: str,
    response_schema: type[BaseModel],
    max_retries: int = 5,
    regenerate: bool = False,
    trace_name: str = "gemini-call",
    trace_metadata: dict[str, Any] | None = None,
    trace_user_id: str | None = None,
    trace_session_id: str | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    if max_retries < 1:
        raise ValueError("max_retries must be >= 1")

    sol_images_list = list(sol_images)
    contents = _build_multipage_contents(prompt=prompt, prob_image=prob_image, sol_images=sol_images_list)

    t0 = time.time()
    trace, trace_id = _start_trace(
        prompt=prompt,
        mode=mode,
        name=trace_name,
        request_id=request_id,
        user_id=trace_user_id,
        session_id=trace_session_id,
        metadata=trace_metadata,
    )

    model = "gemini-3.1-flash-lite-preview"

    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(
                model=model,
                contents=contents,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": response_schema.model_json_schema(),
                    "thinking_config": {"thinking_level": "minimal"},
                },
            )

            usage = getattr(resp, "usage_metadata", None)
            tokens_in = getattr(usage, "prompt_token_count", 0)
            tokens_out = getattr(usage, "candidates_token_count", 0)
            tokens_total = getattr(usage, "total_token_count", 0)
            tokens_thoughts = getattr(usage, "thoughts_token_count", 0)
            latency = time.time() - t0
            retry_count = attempt
            estimated_call_cost_usd = _estimate_call_cost_usd(
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                tokens_thoughts=tokens_thoughts,
            )
            _warn_if_cost_spike(estimated_call_cost_usd)

            observation_id = _trace_generation(
                trace,
                model=model,
                prompt=prompt,
                output=resp.text,
                mode=mode,
                latency=latency,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                tokens_total=tokens_total,
                tokens_thoughts=tokens_thoughts,
            )
            end_metadata = dict(trace_metadata or {})
            end_metadata.update({"success": True, "retryCount": retry_count})
            _end_trace(trace, output=resp.text, metadata=end_metadata)
            if langfuse is not None and hasattr(langfuse, "flush"):
                langfuse.flush()

            return {
                "response_text": resp.text,
                "prompt": prompt,
                "prob_image": prob_image,
                "sol_images": sol_images_list,
                "mode": mode,
                "model_name": model,
                "timestamp": datetime.now(),
                "latency_seconds": latency,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "tokens_thoughts": tokens_thoughts,
                "tokens_total": tokens_total,
                "estimated_call_cost_usd": estimated_call_cost_usd,
                "retry_count": retry_count,
                "trace_id": trace_id,
                "observation_id": observation_id,
                "message_id": None,
                "request_id": request_id,
            }

        except ServerError as exc:
            is_last_attempt = attempt == max_retries - 1
            _trace_event(
                trace,
                name="server_error",
                metadata={"attempt": attempt + 1, "max_retries": max_retries, "error": str(exc)},
            )
            if is_last_attempt:
                logger.exception("Gemini server error after %s attempts", max_retries)
                end_metadata = dict(trace_metadata or {})
                end_metadata.update({"success": False, "retryCount": attempt + 1, "error": str(exc)})
                _end_trace(trace, output={"error": str(exc)}, metadata=end_metadata)
                raise

            wait_seconds = 2**attempt
            logger.warning(
                "Gemini server error on attempt %s/%s. Retrying in %ss",
                attempt + 1,
                max_retries,
                wait_seconds,
            )
            time.sleep(wait_seconds)

        except Exception as exc:
            _trace_event(trace, name="unexpected_error", metadata={"error": str(exc)})
            logger.exception("Gemini request failed with non-retryable error")
            end_metadata = dict(trace_metadata or {})
            end_metadata.update({"success": False, "retryCount": attempt, "error": str(exc)})
            _end_trace(trace, output={"error": str(exc)}, metadata=end_metadata)
            raise

    raise RuntimeError("Gemini request failed unexpectedly")


def call_legibility_with_retry(
    prompt: str,
    prob_image: Any,
    sol_images: Sequence[Any],
    mode: str,
    max_retries: int = 5,
    regenerate: bool = False,
    trace_name: str = "gemini-legibility",
    trace_metadata: dict[str, Any] | None = None,
    trace_user_id: str | None = None,
    trace_session_id: str | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    return _call_model_with_retry_internal(
        prompt=prompt,
        prob_image=prob_image,
        sol_images=sol_images,
        mode=mode,
        response_schema=LegibilityResponse,
        max_retries=max_retries,
        regenerate=regenerate,
        trace_name=trace_name,
        trace_metadata=trace_metadata,
        trace_user_id=trace_user_id,
        trace_session_id=trace_session_id,
        request_id=request_id,
    )


def call_mode_v3_with_retry(
    prompt: str,
    prob_image: Any,
    sol_images: Sequence[Any],
    mode: str,
    max_retries: int = 5,
    regenerate: bool = False,
    trace_name: str = "gemini-mode-v3",
    trace_metadata: dict[str, Any] | None = None,
    trace_user_id: str | None = None,
    trace_session_id: str | None = None,
    request_id: str | None = None,
):
    return _call_model_with_retry_internal(
        prompt=prompt,
        prob_image=prob_image,
        sol_images=sol_images,
        mode=mode,
        response_schema=ModeV3Response,
        max_retries=max_retries,
        regenerate=regenerate,
        trace_name=trace_name,
        trace_metadata=trace_metadata,
        trace_user_id=trace_user_id,
        trace_session_id=trace_session_id,
        request_id=request_id,
    )


def call_deferred_error_with_retry(
    prompt: str,
    prob_image: Any,
    sol_images: Sequence[Any],
    mode: str,
    max_retries: int = 5,
    regenerate: bool = False,
    trace_name: str = "gemini-deferred-error",
    trace_metadata: dict[str, Any] | None = None,
    trace_user_id: str | None = None,
    trace_session_id: str | None = None,
    request_id: str | None = None,
):
    return _call_model_with_retry_internal(
        prompt=prompt,
        prob_image=prob_image,
        sol_images=sol_images,
        mode=mode,
        response_schema=DeferredErrorResponse,
        max_retries=max_retries,
        regenerate=regenerate,
        trace_name=trace_name,
        trace_metadata=trace_metadata,
        trace_user_id=trace_user_id,
        trace_session_id=trace_session_id,
        request_id=request_id,
    )


def call_model_with_retry(
    prompt: str,
    prob_image: Any,
    sol_images: Sequence[Any],
    mode: str,
    max_retries: int = 5,
    regenerate: bool = False,
    trace_name: str = "gemini-call",
    trace_metadata: dict[str, Any] | None = None,
    trace_user_id: str | None = None,
    trace_session_id: str | None = None,
    request_id: str | None = None,
):
    """Call Gemini with retries and optional Langfuse tracing."""
    return _call_model_with_retry_internal(
        prompt=prompt,
        prob_image=prob_image,
        sol_images=sol_images,
        mode=mode,
        response_schema=LLMResponse,
        max_retries=max_retries,
        regenerate=regenerate,
        trace_name=trace_name,
        trace_metadata=trace_metadata,
        trace_user_id=trace_user_id,
        trace_session_id=trace_session_id,
        request_id=request_id,
    )
