import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def preprocess_image_remove_grid(input_path, output_path):

    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Błąd: Nie można wczytać obrazu z {input_path}")
        return False

    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (img.shape[1] // 30, 1))

    detected_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    img_no_horizontal = img.copy()
    img_no_horizontal[detected_horizontal > 0] = 255

    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, img.shape[0] // 30))

    _, thresh_v = cv2.threshold(img_no_horizontal, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    detected_vertical = cv2.morphologyEx(thresh_v, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    img_cleaned = img_no_horizontal.copy()
    img_cleaned[detected_vertical > 0] = 255

    kernel_clean = np.ones((2, 2), np.uint8)
    img_final = cv2.erode(img_cleaned, kernel_clean, iterations=1)

    cv2.imwrite(output_path, img_final)
    print(f"Przetworzony obraz zapisano jako: {output_path}")
    return True



input_image = 'scan_15_krotka.jpg'
output_image = 'scan_15_krotka_bez_kratki.png'

if preprocess_image_remove_grid(input_image, output_image):

    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(cv2.imread(input_image, cv2.IMREAD_GRAYSCALE), cmap='gray')
    plt.title("Oryginał")
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(cv2.imread(output_image, cv2.IMREAD_GRAYSCALE), cmap='gray')
    plt.title("Po usunięciu kratki")
    plt.axis('off')
    plt.show()