from llama_cpp import Llama
import json
llm = Llama(
    model_path="C:/Users/aleks/Bielik-11B-v2.3-Instruct.Q4_K_M.gguf",
    n_ctx=2048,      # wielkość "pamięci" modelu (kontekst)
    n_threads=6,     # zmień na liczbę swoich rdzeni procesora (zostaw 1-2 wolne dla systemu)
    n_gpu_layers=0   # WYMUSZENIE pracy na samym procesorze (CPU)
)

print("--- Bielik gotowy do pracy (Tryb CPU) ---")

class Asses:
    def __init__(self):

        with open('json_outputs/gemini3_1.json', 'r') as file:
            self.user_answers = json.load(file)

        with open('bielik_dop.json', 'r') as file:
            self.correct_answers = json.load(file)

        self.user_map = {item['id']: item for item in self.user_answers['arkusz']}

        self.exam_max_points = 0
        self.user_score = 0.0
        self.results_list = []

    def print_jsons(self):
        print(self.user_answers['arkusz'])
        print(self.correct_answers['klucz'])

    def give_score(self):

        for correct in self.correct_answers['klucz']:
            q_id = correct['id']
            q_typ = correct['typ']
            q_correct_val = correct['wartosc']
            points = correct['punkty']
            self.exam_max_points += points
            user_item = self.user_map.get(q_id)

            if user_item:
                u_val = user_item['odpowiedz_user']
                if user_item['typ'] == "zamkniete":
                    if u_val.lower() == q_correct_val.lower():
                        self.user_score += points
                        self.results_list.append({
                            "id": q_id,
                            "typ": "zamkniete",
                            "zdobyte_punkty": points,
                            "max_punktów": points,
                            "komentarz": "poprawna"
                        })
                    else:
                        self.results_list.append({
                            "id": q_id,
                            "typ": "zamkniete",
                            "zdobyte_punkty": 0,
                            "max_punktów": points,
                            "komentarz": "bledna"
                        })
                else:
                    if correct['metoda_weryfikacji'] == "slowa_kluczowe":
                        wzorzec_str = f"Słowa kluczowe, które powinny się pojawić: {', '.join(q_correct_val)}"
                    else:
                        wzorzec_str = f"Wzorcowa odpowiedź: {q_correct_val}"

                    prompt = f"""Jesteś profesjonalnym egzaminatorem przedmiotów technicznych. Twoim zadaniem jest sprawiedliwa ocena odpowiedzi ucznia na podstawie dostarczonego wzorca merytorycznego. 
                        Zadanie jest warte maksymalnie {points} pkt.
                        
                        KONTEKST (WZORZEC):
                        {wzorzec_str}
                        
                        ODPOWIEDŹ UCZNIA:
                        "{u_val}"
                        
                        ZASADY OCENY:
                        1. MERYTORYKA PRZEDE WSZYSTKIM: Oceniaj wiedzę techniczną i intencję ucznia. Nie odejmuj punktów za brak identycznego słownictwa, jeśli uczeń użył synonimów lub opisał zjawisko własnymi słowami w sposób poprawny.
                        2. DOKŁADNOŚĆ PUNKTACJI: Możesz wystawiać punkty ułamkowe z krokiem 0.5 PKT (np. 0.5, 1.0, 1.5, 2.0 itd.).
                        3. PYTANIA KRÓTKIE (Waga <= 1 PKT): Są to pytania o konkretne fakty. Spodziewaj się zwięzłości. Jeśli uczeń podał merytoryczne "sedno" (nawet jednym słowem lub krótką frazą), przyznaj 100% punktów. Daj 0.5 PKT tylko jeśli odpowiedź jest bardzo niejasna lub niepełna.
                        4. PYTANIA ROZBUDOWANE (Waga > 1 PKT): 
                           - Szukaj zrozumienia procesów i przyczynowości.
                           - Jeśli uczeń poprawnie opisał mechanizm działania, ale pominął drugorzędne detale (np. konkretne nazwy środowisk programistycznych czy parametry poboczne), przyznaj wysoką notę (np. 3.5/4 lub 4/4).
                           - Punktuj cząstkowo za każdą poprawną część skomplikowanej odpowiedzi.
                        5. BŁĘDY: Obniżaj punktację znacząco tylko w przypadku błędów rzeczowych (nieprawda techniczna) lub całkowitego pomylenia definicji.
                        
                        WYMAGANY FORMAT ODPOWIEDZI (BEZ WYJĄTKÓW):
                        WYNIK: [liczba] PKT | UZASADNIENIE: [krótkie zdanie lub slowo w jednej linii]
                        
                        Przykład: WYNIK: 3.5 PKT | UZASADNIENIE: Uczeń rozumie istotę SLAM, pominął jedynie techniczny aspekt zamykania pętli.
                        Przykład: WYNIK: 1 PKT | UZASADNIENIE: Prawidłowa i konkretna nazwa systemu.
                    """

                    response = llm.create_chat_completion(
                        messages=[
                            {"role": "system",
                                "content": "Jesteś surowym, ale sprawiedliwym egzaminatorem inżynieryjnym. Odpowiadasz krótko i konkretnie."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1,  # Niska temperatura dla stabilności ocen
                        max_tokens=200
                    )

                    feedback = response["choices"][0]["message"]["content"]

                    try:
                        parts = feedback.split("|")
                        score_part = parts[0].replace("WYNIK:", "").replace("PKT", "").strip()
                        current_points = float(score_part.replace(',', '.'))

                        justification_str = parts[1].replace("UZASADNIENIE:", "").strip()

                        self.user_score += current_points
                        print(f"Zadanie {q_id}: {current_points}/{points} pkt. (Feedback: {feedback})")

                        self.results_list.append({
                            "id": q_id,
                            "typ": "otwarte",
                            "zdobyte_punkty": current_points,
                            "max_punktów": points,
                            "komentarz": justification_str
                        })
                    except Exception as e:
                        print(f"Błąd parsowania wyniku dla zadania {q_id}. Bielik napisał: {feedback}. Szczegóły: {e}")

            else:
                print(f"Zadanie {q_id}: Brak odpowiedzi (0/{points})")
                self.results_list.append({
                    "id": q_id,
                    "typ": q_typ,
                    "zdobyte_punkty": 0,
                    "max_punktów": points,
                    "komentarz": "Brak odpowiedzi w arkuszu."
                })
    def save_data(self):
        final_data = {
            "wynik": f"{self.user_score}/{self.exam_max_points}",
            "procent": f"{round((self.user_score/self.exam_max_points)*100, 2)}%",
            "szczegoly": self.results_list
        }

        with open('final_report.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
        print("Everything went well results saved!")
        print(f"\nres: {self.user_score}/{self.exam_max_points}")

bielik = Asses()
bielik.print_jsons()
bielik.give_score()
bielik.save_data()