from google import genai
from google.genai.errors import ServerError
from PIL import Image
import time
import pandas as pd
from pydantic import BaseModel

class LLMResponse(BaseModel):
    verdict: str
    response_type: str
    message_is: str

client = genai.Client()
df = pd.read_csv("assignment3.csv")

def call_model_with_retry(prompt: str, image, mode: str, max_retries=5) -> str:
    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(
                model="models/gemini-3-flash-preview",
                contents=[prompt, mode, image],
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": LLMResponse.model_json_schema(),
                },
            )
            return resp.text
        except ServerError:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"Server busy, retrying in {wait}s...")
            time.sleep(wait)

#for v in ["v1", "v2", "v3", "v4"]:
#    with open(f"./prompts/{v}.txt", "r") as file:
#        prompt = file.read()
#
#    rows = []
#
#    for row in df.itertuples():
#        file_path = f"./img/{row.image}"
#        print(f"[{v}] Processing {file_path}")
#
#        try:
#            with Image.open(file_path) as image:
#                result = call_model_with_retry(prompt, image, row.mode)
#
#            parsed = LLMResponse.model_validate_json(result)  # pydantic model
#            out = parsed.model_dump()                         # dict
#
#            out["file_path"] = file_path
#            out["expected_verdict"] = row.expected_verdict
#            out["prompt_version"] = v
#            rows.append(out)
#
#        except Exception as e:
#            print(f"Failed on {file_path}: {e}")
#            #  keep failures in the output too
#            rows.append({
#                "file_path": file_path,
#                "expected_verdict": getattr(row, "expected_verdict", None),
#                "prompt_version": v,
#                "verdict": None,
#                "response_type": "error",
#                "message_is": str(e),
#            })
#
#        time.sleep(1)
#
#    result_df = pd.DataFrame(rows)
#    result_df.to_csv(f"results_{v}.csv", index=False)

with open(f"./prompts/v4.txt", "r") as file:
       prompt = file.read()
       
       image = Image.open("./img/40.png")
       result = call_model_with_retry(prompt, image, "check_solution")
       parsed = LLMResponse.model_validate_json(result)  # pydantic model
       out = parsed.model_dump() 
       print(out)