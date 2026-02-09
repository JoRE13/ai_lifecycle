from google import genai
from google.genai.errors import ServerError
from PIL import Image
from pathlib import Path
import time
import pandas as pd
import json
import re


client = genai.Client()

df = pd.read_csv('assignment3.csv')



with open("./prompts/v1.txt", "r") as file:
    prompt_v1 = file.read()


def call_model_with_retry(image,mode, max_retries=5):
    for attempt in range(max_retries):
        try:
            resp = client.models.generate_content(
                model="models/gemini-3-flash-preview",
                contents=[prompt_v1, mode, image],
            )
            return resp.text

        except ServerError as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"Server busy, retrying in {wait}s...")
            time.sleep(wait)

result_df = pd.DataFrame()

for row in df.itertuples():
    file_path = f"./img/{row.image}"
    print(f"Processing {file_path}")

    with Image.open(file_path) as image:
        try:
            result = call_model_with_retry(image, row.mode)
            if result.startswith("```"):
                result = re.sub(r"^```(?:json)?\s*", "", result)
                result = re.sub(r"\s*```$", "", result).strip()

            # convert model response (string) to dict
            result_json = json.loads(result)

            # add extra fields
            result_json["file_path"] = file_path
            result_json["expected_verdict"] = row.expected_verdict

            # append to dataframe
            result_df = pd.concat(
                [result_df, pd.DataFrame([result_json])],
                ignore_index=True
            )

        except Exception as e:
            print(f"Failed on {file_path}: {e}")

    time.sleep(1)

print(result_df)
result_df.to_csv('results_v1.csv')

