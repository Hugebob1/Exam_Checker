from google import genai
from google.genai import types
import PIL.Image
import os
from dotenv import load_dotenv
import json

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

MODEL_ID = "gemini-3.1-flash-lite-preview"


def read_exam_with_confidence(image_path):
    img = PIL.Image.open(image_path)

    prompt = """
    Jesteś asystentem do transkrypcji odręcznych egzaminów w języku polskim.

    Przepisz ABSOLUTNIE WSZYSTKIE zadania widoczne na stronie.

    ZASADY:
    - Zachowaj oryginalne numery zadań (np. 21, 22, 30...)
    - Cyfry lub ułamki (np. 1, 3, 1/2) widoczne obok numerów zadań to punkty przyznane przez prowadzącego — całkowicie je ignoruj
    - Odpowiedzi wielokrotnego wyboru (a/b/c/d lub A/B/C/D) mogą być zapisane jako:
      * ciąg w stylu: 1-a|2-b|3-c lub 1. A, 2. B, 3. C
      * numer zadania nad literką odpowiedzi (liczba w jednej linii, litera pod nią)
      * W obu przypadkach przepisz je jako listę par: [{"numer": "1", "odpowiedz": "a"}, ...]
    - Jeśli na stronie widoczny jest rysunek, schemat lub wykres — całkowicie go pomiń, przepisuj wyłącznie tekst
    - Jeśli słowo jest nieczytelne, wpisz [nieczytelne]
    - Nie parafrazuj, przepisuj dosłownie

    Zwróć wynik WYŁĄCZNIE jako obiekt JSON (bez markdown, bez ```json):
    {
      "odpowiedzi_testowe": [
        {"numer": "1", "odpowiedz": "a"},
        ...
      ],
      "zadania": [
        {
          "numer_zadania": "21",
          "tresc": "pełna treść pytania i odpowiedzi...",
          "pewnosc": 0.95,
          "uwagi": "czytelne / fragment nieczytelny / itp."
        }
      ]
    }

    Jeśli nie ma odpowiedzi testowych, zwróć "odpowiedzi_testowe": []
    """

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[prompt, img],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    return json.loads(response.text)


if __name__ == "__main__":
    foto_path = "anonim/p3.jpg"

    print(f"--- START ANALIZY (Model: {MODEL_ID}) ---")
    res = read_exam_with_confidence(foto_path)
    print(res)