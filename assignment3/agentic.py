from google import genai
from google.genai.errors import ServerError
from PIL import Image
from pathlib import Path
import time
import pandas as pd


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


for row in df.itertuples():
    file_path = f"./img/{row.image}"
    print(f"Processing {file_path}")
    with Image.open(file_path) as image:
        try:
            result = call_model_with_retry(image, row.mode)
            print(result)
        except Exception as e:
            print(f"Failed on {file_path}: {e}")
    # pacing between requests helps a lot
    time.sleep(1)
