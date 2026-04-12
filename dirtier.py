import cv2
import numpy as np
import os
import random


def dodaj_szum(obraz, intensywnosc=30):

    row, col, ch = obraz.shape

    mean = 0
    sigma = intensywnosc
    gauss = np.random.normal(mean, sigma, (row, col, ch))
    gauss = gauss.reshape(row, col, ch)

    zanieczyszczony = obraz + gauss
    zanieczyszczony = np.clip(zanieczyszczony, 0, 255)
    return zanieczyszczony.astype(np.uint8)


def dodaj_cien_gradientowy(obraz):

    rows, cols, _ = obraz.shape

    if random.choice([0, 1]) == 0:

        gradient = np.tile(np.linspace(random.uniform(0.5, 0.8), 1.0, rows), (cols, 1)).T
    else:

        gradient = np.tile(np.linspace(random.uniform(0.5, 0.8), 1.0, cols), (rows, 1))

    maska_cienia = cv2.merge([gradient, gradient, gradient])

    obraz_float = obraz.astype(np.float32) / 255.0
    obraz_zacieniony = obraz_float * maska_cienia
    return (obraz_zacieniony * 255).astype(np.uint8)


def dodaj_lekkie_rozmycie(obraz):
    k_size = random.choice([3, 5])
    return cv2.GaussianBlur(obraz, (k_size, k_size), 0)


def pobrudz_zdjecie(sciezka_wejsciowa, sciezka_wyjsciowa):
    img = cv2.imread(sciezka_wejsciowa)
    if img is None:
        print(f"Błąd wczytania: {sciezka_wejsciowa}")
        return

    img = dodaj_cien_gradientowy(img)

    img = dodaj_szum(img, intensywnosc=random.randint(15, 40))

    if random.random() > 0.5:
        img = dodaj_lekkie_rozmycie(img)

    cv2.imwrite(sciezka_wyjsciowa, img)
    print(f"Pobrudzono i zapisano: {sciezka_wyjsciowa}")



folder_zrodlowy = "dataset"
folder_wynikowy = "dataset_brudny"

if not os.path.exists(folder_wynikowy):
    os.makedirs(folder_wynikowy)

print("Rozpoczynam proces 'psucia' idealnych skanów...")

for nazwa_pliku in os.listdir(folder_zrodlowy):
    if nazwa_pliku.endswith((".jpg", ".png")):
        sciezka_in = os.path.join(folder_zrodlowy, nazwa_pliku)
        sciezka_out = os.path.join(folder_wynikowy, nazwa_pliku)

        pobrudz_zdjecie(sciezka_in, sciezka_out)

print(f"\nGotowe! Sprawdź folder '{folder_wynikowy}'.")