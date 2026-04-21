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
        self.user_score = 0
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

                    prompt = f"""Jesteś rzetelnym egzaminatorem. Twoim zadaniem jest ocena odpowiedzi ucznia na podstawie podanego wzorca.
                    Zadanie jest warte maksymalnie {points} pkt.
        
                    KONTEKST:
                    {wzorzec_str}
        
                    ODPOWIEDŹ UCZNIA:
                    "{u_val}"
        
                    ZASADY OCENY:
                    1. Porównaj sens odpowiedzi ucznia z wzorcem.
                    2. Przyznaj punkty w skali od 0 do {points}.
                    3. Jeśli odpowiedź jest częściowa, przyznaj odpowiednio mniej punktów.
                    4. Odpowiedz WYŁĄCZNIE w formacie: WYNIK: [liczba] PKT | UZASADNIENIE: [krótkie zdanie]
        
                    Przykład: WYNIK: 3 PKT | UZASADNIENIE: Uczeń wymienił połowę wymaganych elementów.
                    """

                    response = llm.create_chat_completion(
                        messages=[
                            {"role": "system",
                                "content": "Jesteś surowym, ale sprawiedliwym egzaminatorem inżynieryjnym. Odpowiadasz krótko i konkretnie."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1,  # Niska temperatura dla stabilności ocen
                        max_tokens=100
                    )

                    feedback = response["choices"][0]["message"]["content"]

                    try:

                        score_str = feedback.split("WYNIK:")[1].split("PKT")[0].strip()
                        justification_str = feedback.split("UZASADNIENIE:")[1].strip()
                        current_points = int(float(score_str))
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
                        print(f"Błąd parsowania wyniku dla zadania {q_id}. Bielik napisał: {feedback}")

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

