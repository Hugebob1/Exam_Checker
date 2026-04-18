import json
from difflib import SequenceMatcher
import re
import numpy as np
import matplotlib.pyplot as plt

with open('metrics/benchmark.json', 'r', encoding='utf-8') as file:
    bench = json.load(file)
with open('metrics/claude.json', 'r', encoding='utf-8') as file:
    claude = json.load(file)
with open('metrics/gpt.json', 'r', encoding='utf-8') as file:
    gpt = json.load(file)
with open('metrics/gpt_plus.json', 'r', encoding='utf-8') as file:
    gptPlus = json.load(file)
with open('metrics/gemini3pro.json', 'r', encoding='utf-8') as file:
    geminiPro = json.load(file)
with open('metrics/gemini3fast.json', 'r', encoding='utf-8') as file:
    geminiFast = json.load(file)
with open('json_outputs/gemini3_1.json', 'r', encoding='utf-8') as file:
    gemini3_1 = json.load(file)


def plot_model_comparison(results):
    # Ustawienie stylu - 'seaborn-v0_8' lub 'ggplot' dają ładne tło
    plt.style.use('seaborn-v0_8-muted')

    models = list(results.keys())
    wer_values = [results[m]['avg_wer_open'] for m in models]
    sim_values = [results[m]['avg_similarity_open'] for m in models]
    closed_values = [results[m]['accuracy_closed'] / 100 for m in models]

    x = np.arange(len(models))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 7), dpi=100)

    color_wer = '#e74c3c'
    color_sim = '#3498db'
    color_acc = '#2ecc71'

    rects1 = ax.bar(x - width, wer_values, width, label='Average WER', color=color_wer, edgecolor='white',
                    linewidth=0.7)
    rects2 = ax.bar(x, sim_values, width, label='Similarity', color=color_sim, edgecolor='white',
                    linewidth=0.7)
    rects3 = ax.bar(x + width, closed_values, width, label='Accuracy Test', color=color_acc,
                    edgecolor='white', linewidth=0.7)

    ax.set_ylabel('Metric value', fontsize=12, fontweight='bold', alpha=0.7)
    ax.set_title('LLM comparison', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=30, ha='right', fontsize=10)

    ax.yaxis.grid(True, linestyle='--', alpha=0.6)
    ax.set_axisbelow(True)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_alpha(0.3)
    ax.spines['bottom'].set_alpha(0.3)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False, fontsize=10)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 5),  # lekko wyżej nad słupkiem
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontsize=9, fontweight='bold', alpha=0.8)

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    fig.tight_layout()
    plt.subplots_adjust(bottom=0.2)

    plt.savefig('porownanie_modeli_v2.png', bbox_inches='tight')
    plt.show()


def clean_text(text):
    """Usuwa interpunkcję i zbędne spacje, zamienia na małe litery."""
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = " ".join(text.split())
    return text


def calculate_metrics(benchmark_data, model_data):
    closed_correct = 0
    closed_total = 0

    open_wer_scores = []
    open_sim_scores = []

    bench_dict = {item['id']: item for item in benchmark_data['arkusz']}

    for item in model_data['arkusz']:
        item_id = item['id']
        if item_id not in bench_dict:
            continue

        target = bench_dict[item_id]

        # TUTAJ używamy nowej funkcji czyszczącej
        ref_text = clean_text(target['odpowiedz_user'])
        hyp_text = clean_text(item['odpowiedz_user'])

        if item['typ'] == 'zamkniete':
            closed_total += 1
            # Porównanie bez kropek/przecinków i wielkości liter
            if ref_text == hyp_text:
                closed_correct += 1

        elif item['typ'] == 'otwarte':
            # 1. Similarity
            sim = SequenceMatcher(None, ref_text, hyp_text).ratio()
            open_sim_scores.append(sim)

            # 2. WER (Word Error Rate)
            r = ref_text.split()
            h = hyp_text.split()

            if len(r) == 0:
                wer = 1.0 if len(h) > 0 else 0.0
            else:
                d = np.zeros((len(r) + 1) * (len(h) + 1), dtype=np.uint16)
                d = d.reshape((len(r) + 1, len(h) + 1))
                for i in range(len(r) + 1): d[i][0] = i
                for j in range(len(h) + 1): d[0][j] = j
                for i in range(1, len(r) + 1):
                    for j in range(1, len(h) + 1):
                        if r[i - 1] == h[j - 1]:
                            d[i][j] = d[i - 1][j - 1]
                        else:
                            d[i][j] = min(d[i - 1][j - 1], d[i - 1][j], d[i][j - 1]) + 1
                wer = d[len(r)][len(h)] / len(r)

            open_wer_scores.append(wer)

    accuracy = (closed_correct / closed_total) * 100 if closed_total > 0 else 0
    avg_wer = sum(open_wer_scores) / len(open_wer_scores) if open_wer_scores else 0
    avg_sim = sum(open_sim_scores) / len(open_sim_scores) if open_sim_scores else 0

    return {
        "accuracy_closed": round(accuracy, 2),
        "avg_wer_open": round(avg_wer, 4),
        "avg_similarity_open": round(avg_sim, 4)
    }


models = {
    "Claude": claude,
    "GPT": gpt,
    "GPT Plus": gptPlus,
    "Gemini 3 Pro": geminiPro,
    "Gemini 3 Fast": geminiFast,
    "Gemini 3.1 flash api": gemini3_1
}

results = {}
for name, data in models.items():
    results[name] = calculate_metrics(bench, data)
    print(f"--- {name} ---")
    print(f"Accuracy (Zamknięte): {results[name]['accuracy_closed']}%")
    print(f"Średni WER (Otwarte): {results[name]['avg_wer_open']}")
    print(f"Podobieństwo (Otwarte): {results[name]['avg_similarity_open']}\n")

with open("metrics/results.json", "w", encoding='utf-8') as file:
    json.dump(results, file, ensure_ascii=False, indent=4)


plot_model_comparison(results)