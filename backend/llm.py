from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
from langfuse import Langfuse
from pydantic import BaseModel

load_dotenv(Path(__file__).resolve().parent / ".env")

logger = logging.getLogger(__name__)


class LLMResponse(BaseModel):
    verdict: str
    response_type: str
    message_is: str


def _build_langfuse_client() -> Langfuse | None:
    """Create a Langfuse client when credentials are available.

    Returns None if tracing is not configured or initialization fails.
    """
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


def _start_trace(prompt: str, mode: str) -> Any:
    if langfuse is None:
        return None
    try:
        if hasattr(langfuse, "trace"):
            return langfuse.trace(name="gemini-call", input={"prompt": prompt, "mode": mode})
        if hasattr(langfuse, "start_span"):
            return langfuse.start_span(name="gemini-call", input={"prompt": prompt, "mode": mode})
        logger.warning("No compatible Langfuse trace/span API found")
        return None
    except Exception:
        logger.exception("Failed to start Langfuse trace/span")
        return None


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
) -> None:
    if trace is None:
        return

    try:
        if hasattr(trace, "generation"):
            trace.generation(
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
            return

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
            return

        logger.warning("No compatible Langfuse generation API found")
    except Exception:
        logger.exception("Failed to send Langfuse generation")


def call_model_with_retry(
    prompt: str,
    prob_image: Any,
    sol_image: Any,
    mode: str,
    max_retries: int = 5,
    regenerate: bool = False,
):
    """Call Gemini with retries and optional Langfuse tracing.

    Returns the same tuple shape as before for compatibility.
    """
    if max_retries < 1:
        raise ValueError("max_retries must be >= 1")

    t0 = time.time()
    trace = None

    trace = _start_trace(prompt=prompt, mode=mode)

    model = "gemini-3-pro-preview" if regenerate else "models/gemini-3-flash-preview"

    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(
                model=model,
                contents=[prompt, mode, prob_image, sol_image],
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": LLMResponse.model_json_schema(),
                },
            )

            usage = getattr(resp, "usage_metadata", None)
            tokens_in = getattr(usage, "prompt_token_count", 0)
            tokens_out = getattr(usage, "candidates_token_count", 0)
            tokens_total = getattr(usage, "total_token_count", 0)
            tokens_thoughts = getattr(usage, "thoughts_token_count", 0)
            latency = time.time() - t0

            _trace_generation(
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
            if langfuse is not None and hasattr(langfuse, "flush"):
                # Useful during local debugging and short-lived runs.
                langfuse.flush()
            if trace is not None and hasattr(trace, "end"):
                try:
                    trace.end()
                except Exception:
                    logger.exception("Failed to end Langfuse trace/span")

            return (
                resp.text,
                prompt,
                prob_image,
                sol_image,
                mode,
                model,
                datetime.now(),
                latency,
                tokens_in,
                tokens_out,
                tokens_thoughts,
                tokens_total,
            )

        except ServerError as exc:
            is_last_attempt = attempt == max_retries - 1
            _trace_event(
                trace,
                name="server_error",
                metadata={"attempt": attempt + 1, "max_retries": max_retries, "error": str(exc)},
            )

            if is_last_attempt:
                logger.exception("Gemini server error after %s attempts", max_retries)
                if trace is not None and hasattr(trace, "end"):
                    try:
                        trace.end()
                    except Exception:
                        logger.exception("Failed to end Langfuse trace/span")
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
            if trace is not None and hasattr(trace, "end"):
                try:
                    trace.end()
                except Exception:
                    logger.exception("Failed to end Langfuse trace/span")
            raise

    # This point should be unreachable because we either return or raise.
    raise RuntimeError("Gemini request failed unexpectedly")
