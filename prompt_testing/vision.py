from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
from PIL import Image, ImageDraw
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x_min: float = Field(ge=0.0, le=1.0)
    y_min: float = Field(ge=0.0, le=1.0)
    x_max: float = Field(ge=0.0, le=1.0)
    y_max: float = Field(ge=0.0, le=1.0)


class VisionResponse(BaseModel):
    error_found: bool
    verdict: str | None = None
    error_step: str | None = None
    explanation: str | None = None
    bounding_box: BoundingBox | None = None


PROMPT = """
You will receive an image of handwritten mathematics showing a problem and a student's solution.

Your task:
1. Read the student's work.
2. Decide whether the student has made a mathematical error.
3. If there is an error, identify the first incorrect step.
4. Return one bounding box around the handwritten region containing that incorrect step.

Important requirements:
- Return JSON only.
- The bounding box must be tightly around the incorrect handwritten step, not the whole page.
- Use normalized coordinates between 0 and 1 relative to the full image:
  - x_min, y_min = top-left corner
  - x_max, y_max = bottom-right corner
- If there is no mathematical error, set error_found to false and bounding_box to null.
- If the handwriting is too unclear to localize confidently, set error_found to false and explain that in explanation.
- Prefer the first mathematical mistake, not later downstream consequences.
""".strip()


def build_client() -> genai.Client:
    load_dotenv()
    load_dotenv(Path(__file__).with_name(".env"))
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in environment or prompt_testing/.env")
    return genai.Client(api_key=api_key)


def call_model_with_retry(
    client: genai.Client,
    prompt: str,
    image: Image.Image,
    response_model: type[BaseModel],
    max_retries: int = 5,
) -> str:
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="models/gemini-3-flash-preview",
                contents=[prompt, image],
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": response_model.model_json_schema(),
                    "thinking_config": {"thinking_level": "medium"},
                },
            )
            return response.text
        except ServerError:
            if attempt == max_retries - 1:
                raise
            wait_seconds = 2 ** attempt
            print(f"Server busy, retrying in {wait_seconds}s...")
            time.sleep(wait_seconds)

    raise RuntimeError("Exhausted retries without a response.")


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def draw_box_on_image(
    image: Image.Image,
    box: BoundingBox,
    label: str | None = None,
) -> Image.Image:
    annotated = image.copy().convert("RGB")
    draw = ImageDraw.Draw(annotated)

    width, height = annotated.size
    x_min = int(clamp(box.x_min, 0.0, 1.0) * width)
    y_min = int(clamp(box.y_min, 0.0, 1.0) * height)
    x_max = int(clamp(box.x_max, 0.0, 1.0) * width)
    y_max = int(clamp(box.y_max, 0.0, 1.0) * height)

    if x_max <= x_min or y_max <= y_min:
        raise ValueError("Model returned an invalid bounding box.")

    stroke = max(3, min(width, height) // 200)
    draw.rectangle((x_min, y_min, x_max, y_max), outline="red", width=stroke)

    if label:
        text_x = x_min
        text_y = max(0, y_min - 24)
        draw.text((text_x, text_y), label, fill="red")

    return annotated


def process_image(image_path: Path, output_path: Path | None = None) -> VisionResponse:
    client = build_client()

    with Image.open(image_path) as image:
        raw_json = call_model_with_retry(client, PROMPT, image, VisionResponse)
        parsed = VisionResponse.model_validate_json(raw_json)

        print(f"error_found={parsed.error_found}")
        if parsed.verdict:
            print(f"verdict={parsed.verdict}")
        if parsed.error_step:
            print(f"error_step={parsed.error_step}")
        if parsed.explanation:
            print(f"explanation={parsed.explanation}")

        if parsed.error_found and parsed.bounding_box:
            if output_path is None:
                output_path = image_path.with_name(f"{image_path.stem}_boxed{image_path.suffix}")
            elif output_path.exists() and output_path.is_dir():
                output_path = output_path / f"{image_path.stem}_boxed{image_path.suffix}"
            elif not output_path.suffix:
                output_path.mkdir(parents=True, exist_ok=True)
                output_path = output_path / f"{image_path.stem}_boxed{image_path.suffix}"

            output_path.parent.mkdir(parents=True, exist_ok=True)
            annotated = draw_box_on_image(image, parsed.bounding_box, "Possible error")
            annotated.save(output_path)
            print(f"Saved annotated image to {output_path}")
        else:
            print("No box drawn.")

    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Use Gemini 3 Flash to find and box the first handwritten math error in an image."
    )
    parser.add_argument("image_path", nargs="?", help="Path to the input image.")
    parser.add_argument(
        "--image_path",
        dest="image_path_flag",
        help="Path to the input image.",
    )
    parser.add_argument(
        "--output",
        help="Optional path for the annotated output image. Defaults to <input>_boxed.<ext>.",
    )
    args = parser.parse_args()
    args.image_path = args.image_path or args.image_path_flag
    if not args.image_path:
        parser.error("an image path is required via positional `image_path` or `--image_path`")
    return args


def main() -> None:
    args = parse_args()
    image_path = Path(args.image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    output_path = Path(args.output) if args.output else None
    process_image(image_path, output_path)


if __name__ == "__main__":
    main()
