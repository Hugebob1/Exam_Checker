import os
import torch
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from surya.detection import DetectionPredictor

# --- KALIBRACJA CZUŁOŚCI ---
# Te dwie linijki są kluczowe. Jeśli model nadal zaznacza za dużo,
# zwiększaj TEXT_THRESHOLD (np. do 0.5) i zmniejszaj BLANK_THRESHOLD (np. do 0.1).
os.environ["DETECTOR_TEXT_THRESHOLD"] = "0.40"
os.environ["DETECTOR_BLANK_THRESHOLD"] = "0.15"

# Inicjalizacja modelu (raz, na początku)
if 'det_predictor' not in globals():
    print("Inicjalizacja modelu Surya...")
    det_predictor = DetectionPredictor()


def gen_predictions_surya_v3(path, index):
    image = Image.open(path).convert("RGB")

    # Skalowanie do optymalnej rozdzielczości
    target_width = 1200  # Zwiększamy nieco, by lepiej widział przerwy między liniami
    w, h = image.size
    image_res = image.resize((target_width, int(h * target_width / w)), Image.LANCZOS)

    # Predykcja
    predictions = det_predictor([image_res])
    pred = predictions[0]

    print(f"Zdjęcie {index}: Wykryto {len(pred.bboxes)} obszarów.")

    # Rysowanie
    vis = image_res.copy()
    draw = ImageDraw.Draw(vis)

    for box in pred.bboxes:
        # Rysujemy ramki. Jeśli wciąż jest jedna wielka, model
        # uważa, że nie ma wystarczająco dużo "ciszy" między liniami.
        x1, y1, x2, y2 = box.bbox
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)

    plt.figure(figsize=(12, 12))
    plt.imshow(vis)
    plt.title(f"Surya Calibrated - Test {index}")
    plt.axis("off")

    output_dir = 'surya_calibrated'
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(f'{output_dir}/res{index}.png', bbox_inches='tight')
    plt.show()


# Test na Twoich plikach
paths = ["bez_kratki.png", "tescik.jpg"]
for i, p in enumerate(paths):
    if os.path.exists(p):
        gen_predictions_surya_v3(p, i)