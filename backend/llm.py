from google import genai
from google.genai.errors import ServerError
from PIL import Image
import time
import pandas as pd
from pydantic import BaseModel
from datetime import datetime
from langfuse import Langfuse
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

# Initialize Langfuse once
try:
    langfuse = Langfuse()
except Exception:
    langfuse = None

class LLMResponse(BaseModel):
    verdict: str
    response_type: str
    message_is: str

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def call_model_with_retry(prompt: str, prob_image , sol_image, mode: str, max_retries=5, regenerate=False):
    t0 = time.time()

    # Start a trace (one per call)
    trace = None
    if langfuse is not None:
        try:
            trace = langfuse.trace(
                name="gemini-call",
                input={"prompt": prompt, "mode": mode}
            )
        except Exception:
            trace = None

    for attempt in range(max_retries):
        model = "gemini-3-pro-preview" if regenerate else "models/gemini-3-flash-preview"
        try:
            resp = client.models.generate_content(
                model=model,
                contents=[prompt, mode, prob_image, sol_image],
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": LLMResponse.model_json_schema(),
                },
            )

            usage = resp.usage_metadata
            tokens_in = usage.prompt_token_count
            tokens_out = usage.candidates_token_count
            tokens_total = usage.total_token_count
            tokens_thoughts = usage.thoughts_token_count

            latency = time.time() - t0

            # Log generation to Langfuse
            if trace is not None:
                trace.generation(
                    name="gemini-generation",
                    model=model,
                    input=prompt,
                    output=resp.text,
                    usage={
                        "prompt_tokens": tokens_in,
                        "completion_tokens": tokens_out,
                        "total_tokens": tokens_total,
                    },
                    metadata={
                        "mode": mode,
                        "latency": latency,
                        "thought_tokens": tokens_thoughts
                    }
                )

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
                tokens_total
            )

        except ServerError as e:
            if attempt == max_retries - 1:
                if trace is not None:
                    trace.event(name="error", metadata={"error": str(e)})
                raise

            wait = 2 ** attempt
            print(f"Server busy, retrying in {wait}s...")
            time.sleep(wait)

    return None
