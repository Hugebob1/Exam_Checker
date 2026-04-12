import os

# Wyłączenie ostrzeżenia o serwerach (musi być przed importem Paddle)
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from paddleocr import PaddleOCR  # TYLKO TO! Zepsute draw_ocr wyrzucone.
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def test_paddle(paths):
    # Inicjalizacja modelu
    ocr = PaddleOCR(use_angle_cls=True, lang='pl', use_mkldnn=False)

    output_dir = 'paddle_res'
    os.makedirs(output_dir, exist_ok=True)

    for i, path in enumerate(paths):
        if not os.path.exists(path):
            print(f"Brak pliku: {path}")
            continue

        print(f"Przetwarzam {path}...")

        # Detekcja i odczyt
        result = ocr.predict(path)

        # Jeśli nic nie wykryto, pomiń
        if result[0] is None:
            print(f"Brak tekstu na {path}")
            continue

        # Wczytanie obrazu
        img = cv2.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Ustawiamy płótno tak jak w docTR
        fig, ax = plt.subplots(figsize=(12, 12))
        ax.imshow(img)
        ax.axis('off')

        # Rysujemy ramki WŁASNORĘCZNIE, ignorując zepsute narzędzia Paddle
        for line in result[0]:
            box = line[0]  # Współrzędne ramki: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            text = line[1][0]  # Rozpoznany tekst

            # Rysujemy wielokąt (ramkę) wokół tekstu
            polygon = patches.Polygon(box, closed=True, fill=False, edgecolor='red', linewidth=2)
            ax.add_patch(polygon)

            # Wypisujemy tekst w konsoli, żebyś widział, jak dobrze czyta
            print(f"Odczytano: {text}")

        # Zapis i wyświetlanie
        save_path = f'{output_dir}/res{i}.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Zapisano wynik w: {save_path}\n")

        plt.show()
        plt.close(fig)


# Twoje pliki
paths = ["bez_kratki.png", "tescik.jpg", "test.png", "scan_15_krotka.jpg", "scan_28_srednia.jpg"]
test_paddle(paths)