import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

def fix_and_summarize(root_dir):
    stud_res = {}

    folders = sorted([f for f in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, f))])


    for student_id in folders:
        folder_path = os.path.join(root_dir, student_id)
        file_name = f"ocena_bielik_{student_id}.json"
        file_path = os.path.join(folder_path, file_name)

        if not os.path.exists(file_path):
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except:
                print(f"Błąd czytania pliku u studenta {student_id}")
                continue                                  #_sumaryczny
        stud_res[student_id] = {"wynik": float(data["wynik"].split("/")[0]), "max_score": float(data["wynik"].split("/")[1])}
    return stud_res

def read_original_res(path):
    with open(path, 'r', encoding='utf-8') as f:
        stud = json.load(f)

    for s in stud:
        stud[s]["wynik"] = stud[s]["wynik"] * 5/7
        stud[s]["max_score"] = stud[s]["max_score"] * 5 / 7
    return stud



def analyze_grading_quality(ai_res, human_res):
    ids = []
    y_ai = []
    y_human = []

    # 1. Synchronizacja danych
    for s_id in ai_res:
        if s_id in human_res and human_res[s_id]["wynik"] is not None:
            ids.append(s_id)
            y_ai.append(ai_res[s_id]["wynik"])
            y_human.append(human_res[s_id]["wynik"])

    y_ai = np.array(y_ai)
    y_human = np.array(y_human)
    diffs = y_ai - y_human

    # 2. Obliczanie metryk
    mae = np.mean(np.abs(diffs))
    rmse = np.sqrt(np.mean(diffs ** 2))
    correlation, _ = stats.pearsonr(y_human, y_ai)
    bias = np.mean(diffs)

    print(f"--- ANALIZA METRYK (N={len(ids)}) ---")
    print(f"MAE (Średni błąd bezwzględny): {mae:.2f} pkt")
    print(f"RMSE (Błąd średniokwadratowy): {rmse:.2f} pkt")
    print(f"Korelacja Persona: {correlation:.4f}")
    print(f"Bias (Skrzywienie AI): {bias:.2f} pkt")

    # 3. Wizualizacja
    plt.style.use('seaborn-v0_8-muted')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Wykres 1: Scatter Plot z linią regresji
    sns.regplot(x=y_human, y=y_ai, ax=ax1, scatter_kws={'alpha': 0.5}, line_kws={'color': 'red'})
    # Linia idealnej zgodności (y=x)
    max_val = max(max(y_ai), max(y_human))
    ax1.plot([0, max_val], [0, max_val], '--', color='gray', alpha=0.8, label="Idealna zgodność")
    ax1.set_title("Zgodność Ocen: Nauczyciel vs Gemini")
    ax1.set_xlabel("Punkty Nauczyciela")
    ax1.set_ylabel("Punkty Gemini")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Wykres 2: Błąd per student (Residuals)
    colors = ['red' if d > 0 else 'blue' for d in diffs]
    ax2.bar(ids, diffs, color=colors, alpha=0.7)
    ax2.axhline(0, color='black', linewidth=1)
    ax2.set_title("Różnica punktowa na studenta (AI - Nauczyciel)")
    ax2.set_ylabel("Różnica [pkt]")
    ax2.tick_params(axis='x', rotation=90)

    plt.tight_layout()
    plt.show()


# Odpalenie


if __name__ == "__main__":
    ROOT = "grupped/"
    if os.path.exists(ROOT):
        students = fix_and_summarize(ROOT)
        students = dict(sorted(students.items(), key=lambda item: int(item[0])))
        print(students)

        ori_students = read_original_res("original_res.json")
        ori_students = dict(sorted(ori_students.items(), key=lambda item: int(item[0])))
        print(ori_students)

        analyze_grading_quality(students, ori_students)

    else:
        print(f"Błąd: Ścieżka {ROOT} nie istnieje na Twoim Drive!")