import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types


class Asses:
    def __init__(self, key_path):
        load_dotenv()
        self.API_KEY = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.API_KEY)
        self.MODEL_ID = "gemini-3.1-flash-lite-preview"

        with open(key_path, 'r', encoding='utf-8') as file:
            self.correct_answers = json.load(file)

    def evaluate_with_gemini(self, wzorzec, u_val, points):

        prompt = f"""Jesteś sprawiedliwym egzaminatorem na uczelni technicznej. Twoim zadaniem jest rzetelna ocena odpowiedzi studenta.

        ### DANE WEJŚCIOWE:
        - WZORZEC (Klucz): {wzorzec}
        - ODPOWIEDŹ UCZNIA: "{u_val}"
        - MAKSYMALNA NOTA: {points} pkt

        ### ZASADY OCENIANIA:
        1. SKALA: Oceniasz w krokach co 0.5 pkt (np. 0, 0.5, 1.0, 1.5, itd.).
        2. KONKRET VS LANIE WODY: Nie dawaj punktów za samą długość wypowiedzi. Jeśli uczeń pisze dużo, ale omija sedno techniczne – obniż ocenę.
        3. BŁĘDY OCR: Ignoruj oczywiste błędy odczytu tekstu.
        4. SPRAWIEDLIWOŚĆ: Za częściową odpowiedź daj proporcjonalną liczbę punktów.
        5. BRAK ODPOWIEDZI: Jeśli odpowiedź jest pusta lub błędna – 0 pkt.
        6. ZADANIA ZA 1 punkt: Odpowiedz wymagana jest krotka wiec wystarczy ze jest sens lub slowa kluczowe pasuja
        7. ZADANIA Za WIECEJ NIZ 1 punkt: Wymagaj troche wiecej szczegolow ale sens ma byc zachowany z kluczem lub slowami kluczowymi

        ### WYMAGANY FORMAT JSON:
        {{
          "zdobyte": liczba,
          "pewnosc": 0.0-1.0,
          "uzasadnienie": "krótko: co jest dobrze, a czego zabrakło"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.MODEL_ID,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"  ! Błąd API przy ocenie: {e}")
            return {"zdobyte": 0, "uzasadnienie": "Błąd połączenia z API/Modelu"}

    def process_student(self, student_data, student_id, folder_path):
        user_map = {str(item['id']): item for item in student_data['arkusz']}
        user_score = 0.0
        max_points_total = 0
        results = []

        print(f"  > Oceniam studenta {student_id}...")

        for correct in self.correct_answers['klucz']:
            q_id = str(correct['id'])
            points = float(correct['punkty'])
            max_points_total += points
            user_item = user_map.get(q_id)

            if user_item:
                u_val = user_item['odpowiedz_user']

                if correct['typ'] == "zamkniete":
                    is_ok = str(u_val).strip().lower() == str(correct['wartosc']).strip().lower()
                    earned = points if is_ok else 0
                    results.append({
                        "id": q_id, "typ": "zamkniete", "zdobyte": earned, "max": points,
                        "komentarz": "Zgodne z kluczem" if is_ok else f"Błąd (oczekiwano: {correct['wartosc']})"
                    })
                    user_score += earned

                else:
                    if correct.get('metoda_weryfikacji') == "slowa_kluczowe":
                        wzorzec = f"Wymagane słowa kluczowe: {', '.join(correct['wartosc'])}"
                    else:
                        wzorzec = f"Modelowa odpowiedź: {correct['wartosc']}"

                    feedback = self.evaluate_with_gemini(wzorzec, u_val, points)

                    earned = float(feedback.get('zdobyte', 0))
                    user_score += earned
                    results.append({
                        "id": q_id, "typ": "otwarte", "zdobyte": earned, "max": points,
                        "komentarz": feedback.get('uzasadnienie', '')
                    })
                    time.sleep(1)

            else:
                results.append({"id": q_id, "zdobyte": 0, "max": points, "komentarz": "Brak odpowiedzi w arkuszu"})

        final_report = {
            "student_id": student_id,
            "wynik_sumaryczny": f"{user_score}/{max_points_total}",
            "procent": f"{round((user_score / max_points_total) * 100, 2) if max_points_total > 0 else 0}%",
            "szczegoly": results
        }

        # Zapis do pliku
        output_name = f"ocena_gemini_{student_id}.json"
        with open(os.path.join(folder_path, output_name), 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=4, ensure_ascii=False)

        return user_score


def run_grading(root_path, key_path):

    grader = Asses(key_path)

    folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]
    print(f"--- START OCENIANIA ({len(folders)} folderów) ---")

    for student_id in folders:
        folder_path = os.path.join(root_path, student_id)

        input_file = os.path.join(folder_path, f"wynik_{student_id}.json")

        if os.path.exists(input_file):
            with open(input_file, 'r', encoding='utf-8') as f:
                student_data = json.load(f)
            grader.process_student(student_data, student_id, folder_path)
        else:
            print(f"  ! Pomijam {student_id}: brak pliku wynik_{student_id}.json")


if __name__ == "__main__":
    ROOT_DIR = "grupped/"
    KEY_FILE = "bielik_dop.json"

    run_grading(ROOT_DIR, KEY_FILE)
    print("\n--- ZAKOŃCZONO: Wszystkie prace zostały ocenione ---")