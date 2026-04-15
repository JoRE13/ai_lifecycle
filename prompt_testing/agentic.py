from google import genai
from google.genai.errors import ServerError
from PIL import Image
import time
import pandas as pd
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import base64
import json
import mimetypes
from pathlib import Path
from urllib import request, error

class LLMResponse(BaseModel):
    verdict: str
    response_type: str
    message_is: str


class LegibilityRegion(BaseModel):
    page: int | None = None
    snippet: str | None = None
    reason: str | None = None


class LegibilityResponse(BaseModel):
    all_readable: bool
    reading_confidence: float | None = None
    ambiguous_steps: list[LegibilityRegion] = Field(default_factory=list)

class LatexResponse(BaseModel):
    problem: str
    solution: str
    

load_dotenv()
load_dotenv(Path(__file__).with_name(".env"))
api_key = os.getenv("GEMINI_API_KEY")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")


client = genai.Client(api_key=api_key)
df = pd.read_csv("./prompt_testing/test_cases.csv")

def call_model_with_retry(prompt: str, image, basemodel, max_retries=5) -> str:
    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(
                model="models/gemini-3-flash-preview",
                contents=[prompt, image],
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": basemodel.model_json_schema(),
                    "thinking_config": {"thinking_level": "low"},
                },
            )
            return resp.text
        except ServerError:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"Server busy, retrying in {wait}s...")
            time.sleep(wait)


def _extract_json_object(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Response did not contain a JSON object")
    return text[start : end + 1]


def call_openrouter_legibility_with_retry(prompt: str, image_path: str, basemodel, max_retries=5) -> str:
    if not openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/png"

    image_bytes = Path(image_path).read_bytes()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    response_schema = basemodel.model_json_schema()
    payload = {
        "model": "openai/gpt-5.4-nano",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_base64}"},
                    },
                ],
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": basemodel.__name__,
                "strict": True,
                "schema": response_schema,
            },
        },
    }

    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "ai_lifecycle_prompt_testing",
    }

    for attempt in range(max_retries):
        try:
            req = request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with request.urlopen(req) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            return _extract_json_object(content)
        except error.HTTPError as exc:
            if attempt == max_retries - 1:
                detail = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"OpenRouter HTTP {exc.code}: {detail}") from exc
            wait = 2 ** attempt
            print(f"OpenRouter busy, retrying in {wait}s...")
            time.sleep(wait)
        except Exception:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"OpenRouter request failed, retrying in {wait}s...")
            time.sleep(wait)


def evaluate():
    mode_map = {
        "reveal": 0,
        "check_solution": 1,
        "hint": 2,
    }

    for v in ["v6"]:
        prompts = []
        for mode in mode_map:
            with open(f"./backend/prompts/modes/{v}/{mode}/prompt.txt", "r") as file:
                prompts.append(file.read())

        rows = []

        for row in df.itertuples():
            file_path = f"./prompt_testing/img/{row.image}"
            print(f"[{v}] Processing {file_path}")

            try:
                t1 = time.perf_counter()
                with Image.open(file_path) as image:
                    result = call_model_with_retry(prompts[mode_map[row.mode]], image, LLMResponse)
                t2 = time.perf_counter()

                parsed = LLMResponse.model_validate_json(result)  # pydantic model
                out = parsed.model_dump()                         # dict

                out["file_path"] = file_path
                out["expected_verdict"] = row.expected_verdict
                out["prompt_version"] = v
                out["latency"] = t2-t1
                rows.append(out)

            except Exception as e:
                print(f"Failed on {file_path}: {e}")
                #  keep failures in the output too
                rows.append({
                    "file_path": file_path,
                    "expected_verdict": getattr(row, "expected_verdict", None),
                    "prompt_version": v,
                    "verdict": None,
                    "response_type": "error",
                    "message_is": str(e),
                })

            time.sleep(1)

        result_df = pd.DataFrame(rows)
        result_df.to_csv(f"./prompt_testing/results_{"flash_med_v6"}.csv", index=False)
      
def evaluate_2():
    mode_map = {
        "reveal": 0,
        "check_solution": 1,
        "hint": 2,
    }

    for v in ["v6"]:
        prompts = []
        for mode in mode_map:
            with open(f"./backend/prompts/modes/{v}/{mode}/prompt.txt", "r") as file:
                prompts.append(file.read())

        rows = []

        for row in df.itertuples():
            file_path = f"./prompt_testing/img_tex/{row.id}.txt"
            print(f"[{v}] Processing {row.id}")
            with open(file_path, 'r') as f:
                work = f.read()

            try:
                t1 = time.perf_counter()
                result = call_model_with_retry(prompts[mode_map[row.mode]], work, LLMResponse)
                t2 = time.perf_counter()

                parsed = LLMResponse.model_validate_json(result)  # pydantic model
                out = parsed.model_dump()                         # dict

                out["file_path"] = file_path
                out["expected_verdict"] = row.expected_verdict
                out["prompt_version"] = v
                out["latency"] = t2-t1
                rows.append(out)

            except Exception as e:
                print(f"Failed on {file_path}: {e}")
                #  keep failures in the output too
                rows.append({
                    "file_path": file_path,
                    "expected_verdict": getattr(row, "expected_verdict", None),
                    "prompt_version": v,
                    "verdict": None,
                    "response_type": "error",
                    "message_is": str(e),
                })

            time.sleep(1)

        result_df = pd.DataFrame(rows)
        result_df.to_csv(f"./prompt_testing/results_{"flash_med_v6"}.csv", index=False)
  
def legibility():
    with open("./backend/prompts/legibility/v4/prompt.txt", 'r') as file:
        prompt = file.read()
    for row in df.itertuples():
        if row.id in [6,48]:
            file_path = f"./prompt_testing/img/{row.image}"
            print(f"Processing {file_path}")

            try:
                t1 = time.perf_counter()
                with Image.open(file_path) as image:
                    result = call_model_with_retry(prompt, image, LegibilityResponse)
                t2 = time.perf_counter()

                parsed = LegibilityResponse.model_validate_json(result)  # pydantic model
                out = parsed.model_dump()                         # dict
                print(f"Finished in {t2-t1:.1f} seconds")
                if not out["all_readable"]:
                    print(out)

            except Exception as e:
                print(f"Failed on {file_path}: {e}")

            time.sleep(1)

def latex():
    prompt = "You will receive an image of handwritten mathematics. Write out what is written excactly in mathJax latex. Everything should be in icelandic. Output JSON only, {problem: 'excact problem statement', 'solution': 'excact solution statement'}"
    for row in df.itertuples():
            file_path = f"./prompt_testing/img/{row.image}"
            print(f"Processing {file_path}")

           
            t1 = time.perf_counter()
            with Image.open(file_path) as image:
                result = call_model_with_retry(prompt, image, LatexResponse)
            t2 = time.perf_counter()
            
            parsed = LatexResponse.model_validate_json(result)  # pydantic model
            out = parsed.model_dump()                         # dict
            print(f"Finished in {t2-t1:.1f} seconds")
            with open (f"./prompt_testing/img_tex/{row.id}.txt", 'w') as f:
                f.write(out['problem'] + "\n\n")
                f.write(out['solution'])



if __name__ == "__main__":
    legibility()
       
