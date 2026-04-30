import os
import json
import PIL.Image
from dotenv import load_dotenv
from google import genai
from google.genai import types
import time


class OcrAutomation:
    def __init__(self):
        load_dotenv()
        self.API_KEY = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.API_KEY)
        # Używamy wersji flash, bo jest szybka i tania przy dużej ilości zdjęć
        self.MODEL_ID = "gemini-3.1-pro-preview" # gemini-3.1-flash-lite-preview

    def process_student_folder(self, folder_path):
        """Przetwarza wszystkie zdjęcia w folderze jednego ucznia."""
        # Obsługiwane rozszerzenia
        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')

        # Pobierz listę plików i zamień na obiekty PIL.Image
        images = []
        file_names = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)])

        if not file_names:
            print(f"Skipping {folder_path} - brak zdjęć.")
            return None

        for file_name in file_names:
            full_path = os.path.join(folder_path, file_name)
            images.append(PIL.Image.open(full_path))

        print(f"Przetwarzanie folderu: {folder_path} ({len(images)} zdjęć)...")

        prompt = """
                    Jesteś elitarnym, precyzyjnym asystentem do transkrypcji odręcznych egzaminów w języku polskim. 
                    Twoim celem jest wyodrębnienie WYŁĄCZNIE odpowiedzi ucznia.

                    ### KLUCZOWE ZASADY FILTROWANIA (BARDZO WAŻNE):
                    1. **CAŁKOWICIE IGNORUJ PUNKTY:** Na arkuszach znajdują się dopiski prowadzącego: cyfry w kółkach, ułamki (np. 1/2, 0/5), liczby z przecinkiem (0.5, 1.0) lub pojedyncze cyfry zapisane przy numerach zadań. 
                       - TO SĄ PUNKTY. Nie przepisyj ich. 
                       - Nie myl ich z treścią odpowiedzi ani z numerem zadania. 
                       - Jeśli obok "Zad. 5" widzisz "3", to "3" ignorujesz, a interesuje Cię tylko to, co uczeń napisał pod spodem.
                    2. **DOSŁOWNOŚĆ:** Przepisuj odpowiedzi ucznia 1:1, ze wszystkimi błędami. Jeśli tekst jest nieczytelny, wpisz "[nieczytelne]".

                    ### LOGIKA POSZUKIWANIA TREŚCI:
                    3. **ŁĄCZENIE KONTYNUACJI:** Jeśli na stronie widzisz blok tekstu bez numeru zadania, przeanalizuj go w kontekście całego egzaminu. Zazwyczaj jest to dokończenie odpowiedzi z poprzedniej strony. Dopisz ten tekst do odpowiedniego "id".
                    4. **SKANOWANIE MARGINESÓW:** Uczniowie często dopisują brakujące zadania lub poprawki na marginesach, bokach kartki lub w rogach. Znajdź je i przypisz do właściwego ID.
                    5. **ODPOWIEDZI TESTOWE:** Jeśli widzisz listę (np. "1-a, 2-b, 3-c"), rozbij ją na osobne obiekty JSON. Nawet jeśli jest to nabazgrane pionowo na marginesie.
                    6. **POMINIĘCIA:** Całkowicie ignoruj rysunki, schematy, tabele pomocnicze i skreślone fragmenty.

                    ### LOGIKA PORZĄDKOWANIA:
                    - Zdjęcia mogą być w złej kolejności. Najpierw zmapuj wszystkie zadania, a potem ułóż je w JSONIE rosnąco według "id" (1, 2, 3...).
                    - Upewnij się, że żadne zadanie widoczne na zdjęciach nie zostało pominięte.

                    ### WYMAGANY FORMAT WYJŚCIOWY:
                    Zwróć wyłącznie czysty obiekt JSON:
                    {
                      "arkusz": [
                        {
                          "id": "numer_zadania",
                          "typ": "zamkniete | otwarte",
                          "odpowiedz_user": "pełna treść odpowiedzi (połączona, jeśli była rozbita)",
                          "pewnosc": 0.0-1.0,
                          "uwagi": "np. 'czytelne', 'znalezione na marginesie', 'kontynuacja ze strony X'"
                        }
                      ]
                    }
                """

        try:
            # Wysyłamy listę obrazów + prompt
            response = self.client.models.generate_content(
                model=self.MODEL_ID,
                contents=[prompt, *images],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Błąd przy folderze {folder_path}: {e}")
            return None

    def run_batch(self, root_directory):
        """Przechodzi przez wszystkie podfoldery w katalogu głównym."""
        # Słownik na wszystkie wyniki: { "numer_indeksu": {wyniki} }
        all_results = {}

        # Listujemy tylko foldery w katalogu głównym
        folders = [f for f in os.listdir(root_directory) if os.path.isdir(os.path.join(root_directory, f))]

        for student_id in folders:
            folder_path = os.path.join(root_directory, student_id)
            result = self.process_student_folder(folder_path)

            if result:
                all_results[student_id] = result

                # Opcjonalnie: Zapisuj każdy wynik do osobnego pliku .json w folderze ucznia
                output_file = os.path.join(folder_path, f"wynik_{student_id}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                print(f"Zapisano: {output_file}")
            print("Chwila oddechu dla API (10s)...")
            time.sleep(10)

        return all_results


# --- UŻYCIE ---
if __name__ == "__main__":
    # Ścieżka do folderu, w którym masz podfoldery z numerami (np. 311016, 307427 itd.)
    PATH_TO_EXAMS = "grupped/"

    bot = OcrAutomation()
    final_data = bot.run_batch(PATH_TO_EXAMS)

    # Zapisanie zbiorczego pliku ze wszystkimi studentami
    with open("wszyscy_studenci_wyniki.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

    print("\n--- KONIEC: Wszystkie dane zostały przetworzone ---")
