import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image

# 1. Ładowanie modelu GOT-OCR 2.0
# To jest model 5GB, więc przygotuj RAM, ale na CPU pójdzie bez fochów
model_name = 'ucas_vg/GOT-OCR2_0'

print("Ładowanie modelu GOT-OCR (to potrwa chwilę na CPU)...")

# KLUCZ: attn_implementation="sdpa" wyłącza wymóg Flash Attention!
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_name,
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    device_map='cpu', # Wymuszamy CPU
    attn_implementation="sdpa", # TO ROZWIĄZUJE PROBLEM 'FLASH-ATTN'
    torch_dtype=torch.float32
).eval()

def ocr_handwriting_one_step(image_path):
    try:
        # Model GOT-OCR ma specyficzną funkcję do odczytu
        # 'ocr_type' może być 'ocr' (cała strona) lub 'format' (zachowuje formatowanie)
        res = model.chat(tokenizer, image_path, ocr_type='ocr')
        return res
    except Exception as e:
        return f"Błąd: {str(e)}"

# --- START ---
image_file = "tescik.jpg"
print("Rozpoczynam odczyt... na CPU to może zająć od 10 do 30 sekund.")
wynik = ocr_handwriting_one_step(image_file)

print("\n--- ODCZYTANY TEKST ---\n")
print(wynik)