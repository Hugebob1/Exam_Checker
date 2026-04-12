import requests
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER")

models = [
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "google/gemma-3-27b-it:free",
    "nvidia/nemotron-nano-12b-v2-vl:free"
]

MODEL_ID = models[1]

def read_exam_with_confidence(image_path):
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    prompt = """
    Przepisz tekst ze zdjęcia sprawdzianu. 
    Zwróć wynik WYŁĄCZNIE jako obiekt JSON o strukturze:
    {
      "zadania": [
        {
          "numer_zadania": "1",
          "tresc": "treść zadania...",
          "pewnosc": 0.95, 
          "uwagi": "czytelne"
        },
        ...
      ]
    }
    W polu 'pewnosc' wpisz wartość od 0.0 do 1.0. 
    Jeśli pismo jest bardzo niewyraźne i zgadywałeś, daj niską wartość.
    """

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL_ID,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
                    {"type": "text", "text": prompt}
                ]
            }],
            "response_format": {"type": "json_object"}  # wymuszamy JSON jak w Gemini
        }
    )

    raw = response.json()
    print(raw)
    return json.loads(raw["choices"][0]["message"]["content"])


if __name__ == "__main__":
    foto_path = "egz_photos/page0.jpg"

    print(f"--- START ANALIZY (Model: {MODEL_ID}) ---")
    wynik = read_exam_with_confidence(foto_path)
    print(wynik)