from google import genai
from google.genai import types
import PIL.Image
import os
from dotenv import load_dotenv
import json
class Ocr:
    def __init__(self):
        load_dotenv()
        self.API_KEY = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.API_KEY)

        self.MODEL_ID = "gemini-3.1-flash-lite-preview"


    def read_exam_with_confidence(self, image_path):
        img = PIL.Image.open(image_path)

        prompt = """
            Jesteś precyzyjnym asystentem do transkrypcji odręcznych egzaminów w języku polskim. Twoim zadaniem jest zamiana obrazu na obiekt JSON.
    
            ### ZASADY TRANSKRYPCJI:
            1. **Dosłowność i Brak Parafraz:** Przepisuj wszystko dokładnie tak, jak jest napisane. Nie zmieniaj formy. Jeśli słowo jest nieczytelne, wpisz "[nieczytelne]".
            2. **Zachowanie Numeracji:** Zachowaj oryginalne numery zadań (np. 21, 22, 30...).
            3. **Ignorowanie Punktacji:** Cyfry lub ułamki (np. 1, 3, 1/2, 0.5) widoczne obok numerów zadań to punkty przyznane przez prowadzącego — CAŁKOWICIE JE IGNORUJ.
            4. **Obsługa Odpowiedzi Testowych (KLUCZOWE):**
               - Rozpoznaj odpowiedzi wielokrotnego wyboru (a/b/c/d), nawet jeśli są zapisane jako:
                 * Ciąg: "1-a|2-b|3-c" lub "1. A, 2. B, 3. C".
                 * Układ pionowy: numer zadania w jednej linii, a litera odpowiedzi bezpośrednio pod nim.
               - KAŻDĄ taką odpowiedź rozbij na osobny obiekt w liście JSON (Atomizacja).
            5. **Klasyfikacja Typu:**
               - Jeśli odpowiedź to tylko jedna litera -> `typ: "zamkniete"`.
               - Jeśli odpowiedź to słowo lub zdanie -> `typ: "otwarte"`.
            6. **Pominięcia:** Jeśli na stronie widoczny jest rysunek, schemat lub wykres — całkowicie go pomiń, przepisuj wyłącznie tekst.
            
            ### WYMAGANY FORMAT WYJŚCIOWY:
            Zwróć wynik WYŁĄCZNIE jako obiekt JSON (bez markdown, bez żadnego tekstu przed/po).
            
            STRUKTURA:
            {
              "arkusz": [
                {
                  "id": "numer_zadania",
                  "typ": "zamkniete | otwarte",
                  "odpowiedz_user": "treść odpowiedzi",
                  "pewnosc": 0.0-1.0,
                  "uwagi": "czytelne / fragment nieczytelny / itp."
                }
              ]
            }
            
            Jeśli na stronie nie ma żadnych zadań/odpowiedzi, zwróć: {"arkusz": []}
        """

        response = self.client.models.generate_content(
            model=self.MODEL_ID,
            contents=[prompt, img],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        return json.loads(response.text)

bot = Ocr()
res = bot.read_exam_with_confidence("anonim/p12.jpg")
print(res)
# if __name__ == "__main__":
#     foto_path = "anonim/p2.png"
#
#     print(f"--- START ANALIZY (Model: {MODEL_ID}) ---")
#     res = read_exam_with_confidence(foto_path)
#     print(res)