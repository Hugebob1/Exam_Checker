from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from PIL import Image, ImageOps
import numpy as np
import cv2
import os
import subprocess
import tempfile
from pathlib import Path

import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel


# =========================
# 1) docTR tylko do linii
# =========================
model_dc = ocr_predictor(
    det_arch="db_resnet50",
    reco_arch="crnn_vgg16_bn",
    pretrained=True,
    resolve_lines=True
)


def crop_img(img, x1, y1, x2, y2, w, h, pad_x=0.03, pad_y=0.15):
    left = max(0, int((x1 - pad_x) * w))
    top = max(0, int((y1 - pad_y) * h))
    right = min(w, int((x2 + pad_x) * w))
    bottom = min(h, int((y2 + pad_y) * h))
    return img.crop((left, top, right, bottom))


def detect_line_images(path):
    image = Image.open(path).convert("RGB")
    doc = DocumentFile.from_images(path)
    out = model_dc(doc)

    page = out.pages[0].export()
    h, w = page["dimensions"]

    line_images = []
    for block in page["blocks"]:
        for line in block["lines"]:
            (x1, y1), (x2, y2) = line["geometry"]
            line_img = crop_img(image, x1, y1, x2, y2, w, h)
            line_images.append(line_img)

    return line_images


# =======================================
# 2) DELIKATNY preprocessing dla HTR
# =======================================
def prepare_line_for_htr(image_pil, scale=2.5, use_clahe=True, rgb=True):
    """
    Bez adaptiveThreshold i bez mocnego blur.
    Dla cienkiego, jasnego pisma to zwykle daje lepszy efekt.
    """
    img = ImageOps.exif_transpose(image_pil).convert("L")
    arr = np.array(img)

    # lekka normalizacja kontrastu
    arr = cv2.normalize(arr, None, 0, 255, cv2.NORM_MINMAX)

    if use_clahe:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        arr = clahe.apply(arr)

    h, w = arr.shape
    new_w = max(32, int(w * scale))
    new_h = max(32, int(h * scale))
    arr = cv2.resize(arr, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    # biały margines
    arr = cv2.copyMakeBorder(
        arr, 18, 18, 28, 28,
        cv2.BORDER_CONSTANT,
        value=255
    )

    out = Image.fromarray(arr)
    return out.convert("RGB") if rgb else out


# =======================================
# 3) TrOCR jako benchmark nr 2
# =======================================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

TROCR_MODEL_NAME = "microsoft/trocr-large-handwritten"
processor_tr = TrOCRProcessor.from_pretrained(TROCR_MODEL_NAME)
model_tr = VisionEncoderDecoderModel.from_pretrained(TROCR_MODEL_NAME).to(DEVICE)
model_tr.eval()


@torch.inference_mode()
def predict_trocr_line(image_pil):
    img = prepare_line_for_htr(image_pil, rgb=True)

    pixel_values = processor_tr(images=img, return_tensors="pt").pixel_values.to(DEVICE)

    # beam=1 -> mniej "zgadywania słów"
    generated_ids = model_tr.generate(
        pixel_values,
        max_new_tokens=96,
        num_beams=1,
        do_sample=False,
        early_stopping=True
    )

    text = processor_tr.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return text.strip()


# =======================================
# 4) Kraken jako benchmark nr 1
# =======================================
def predict_kraken_line(image_pil, kraken_model_path):
    """
    Wersja przez CLI, bo jest najprostsza i najmniej upierdliwa do wpięcia.
    Zakłada, że masz zainstalowane polecenie `kraken`.
    """
    img = prepare_line_for_htr(image_pil, rgb=False)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        in_path = td / "line.png"
        out_path = td / "out.txt"

        img.save(in_path)

        cmd = [
            "kraken",
            "-i", str(in_path), str(out_path),
            "ocr",
            "-m", str(kraken_model_path)
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True)

        if proc.returncode != 0:
            raise RuntimeError(
                f"KRAKEN ERROR\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
            )

        return out_path.read_text(encoding="utf-8").strip()


# =======================================
# 5) wspólna funkcja porównawcza
# =======================================
def run_pipeline(path, recognizer="trocr", kraken_model_path=None):
    line_images = detect_line_images(path)

    lines = []
    for line_img in line_images:
        if recognizer == "trocr":
            txt = predict_trocr_line(line_img)
        elif recognizer == "kraken":
            if not kraken_model_path:
                raise ValueError("Podaj kraken_model_path.")
            txt = predict_kraken_line(line_img, kraken_model_path)
        else:
            raise ValueError("recognizer musi być: 'trocr' albo 'kraken'")
        lines.append(txt)

    return "\n".join(lines)


if __name__ == "__main__":
    img_path = "dataset_brudny/test.png"

    print("=== TrOCR ===")
    print(run_pipeline(img_path, recognizer="trocr"))

    # przykład:
    # print("=== Kraken ===")
    # print(run_pipeline(img_path, recognizer="kraken",
    #                    kraken_model_path="twoj_model.mlmodel"))