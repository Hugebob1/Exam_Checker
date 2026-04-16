from llama_cpp import Llama
import json
llm = Llama(
    model_path="C:/Users/aleks/Bielik-11B-v2.3-Instruct.Q4_K_M.gguf",
    n_ctx=2048,      # wielkość "pamięci" modelu (kontekst)
    n_threads=6,     # zmień na liczbę swoich rdzeni procesora (zostaw 1-2 wolne dla systemu)
    n_gpu_layers=0   # WYMUSZENIE pracy na samym procesorze (CPU)
)

print("--- Bielik gotowy do pracy (Tryb CPU) ---")


with open('json_outputs/gemini3_1.json', 'r') as file:
    user_answers = json.load(file)

with open('bielik_dop.json', 'r') as file:
    correct_answers = json.load(file)

print(user_answers['arkusz'])
print(correct_answers['klucz'])

user_map = {item['id']: item for item in user_answers['arkusz']}

exam_max_points = 0
user_score = 0

results_list = []  # Tu będą lądować wyniki każdego zadania

for correct in correct_answers['klucz']:
    q_id = correct['id']
    q_typ = correct['typ']
    q_correct_val = correct['wartosc']
    points = correct['punkty']
    exam_max_points += points
    user_item = user_map.get(q_id)

    if user_item:
        u_val = user_item['odpowiedz_user']
        if user_item['typ'] == "zamkniete":
            if u_val.lower() == q_correct_val.lower():
                user_score += points
                results_list.append({
                    "id": q_id,
                    "typ": "zamkniete",
                    "zdobyte_punkty": points,
                    "max_punktów": points,
                    "komentarz": "poprawna"
                })
            else:
                results_list.append({
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
                user_score += current_points
                print(f"Zadanie {q_id}: {current_points}/{points} pkt. (Feedback: {feedback})")
                results_list.append({
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
        results_list.append({
            "id": q_id,
            "typ": q_typ,
            "zdobyte_punkty": 0,
            "max_punktów": points,
            "komentarz": "Brak odpowiedzi w arkuszu."
        })

final_data = {
    "wynik": f"{user_score}/{exam_max_points}",
    "procent": f"{round((user_score/exam_max_points)*100, 2)}%",
    "szczegoly": results_list
}

with open('final_report.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, indent=4, ensure_ascii=False)

print(f"\nres: {user_score}/{exam_max_points}")