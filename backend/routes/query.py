from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from PIL import Image, UnidentifiedImageError

from backend.auth.deps import get_current_user
from backend.llm import call_model_with_retry
from backend.models.auth_models import User

router = APIRouter(tags=["query"])

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompt.txt"


def _load_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail="Prompt file not found") from exc


def _to_pil_image(upload: UploadFile, data: bytes) -> Image.Image:
    try:
        return Image.open(BytesIO(data))
    except UnidentifiedImageError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid image uploaded for field '{upload.filename}'",
        ) from exc


@router.post("/query")
async def query(
    mode: Literal["hint", "check_solution", "reveal"] = Form(...),
    prob_image: UploadFile = File(...),
    sol_image: UploadFile = File(...),
    _: User = Depends(get_current_user),
):
    prompt = _load_prompt()

    prob_bytes = await prob_image.read()
    sol_bytes = await sol_image.read()

    if not prob_bytes or not sol_bytes:
        raise HTTPException(status_code=422, detail="Both images are required")

    prob_pil = _to_pil_image(prob_image, prob_bytes)
    sol_pil = _to_pil_image(sol_image, sol_bytes)

    try:
        result = call_model_with_retry(
            prompt=prompt,
            prob_image=prob_pil,
            sol_image=sol_pil,
            mode=mode,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail="LLM request failed") from exc

    if not result:
        raise HTTPException(status_code=502, detail="LLM request failed")

    resp_text = result[0] if isinstance(result, tuple) else result
    return Response(content=resp_text, media_type="application/json")

