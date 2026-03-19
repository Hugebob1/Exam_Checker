from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import torch
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import easyocr
from PIL import Image
import gc
import cv2
import numpy as np
from PIL import Image, ImageOps



def crop_img(img, x1, y1, x2, y2, w, h, pad_x=0.02, pad_y=0.08):
    left = max(0, int((x1 - pad_x) * w))
    top = max(0, int((y1 - pad_y) * h))
    right = min(w, int((x2 + pad_x) * w))
    bottom = min(h, int((y2 + pad_y) * h))
    return img.crop((left, top, right, bottom))

model_dc = ocr_predictor(
    det_arch='db_resnet50',
    reco_arch='crnn_vgg16_bn',
    pretrained=True,
    resolve_lines=True
)

def preprocess_line_for_ocr(image_pil):
    img = image_pil.convert("L")
    arr = np.array(img)

    # autokontrast
    arr = cv2.normalize(arr, None, 0, 255, cv2.NORM_MINMAX)

    # lekkie odszumienie
    arr = cv2.GaussianBlur(arr, (3, 3), 0)

    # powiększenie x3
    h, w = arr.shape
    arr = cv2.resize(arr, (w * 3, h * 3), interpolation=cv2.INTER_CUBIC)

    # biały margines dookoła
    arr = cv2.copyMakeBorder(arr, 20, 20, 30, 30, cv2.BORDER_CONSTANT, value=255)

    # lekki threshold, ale nie za agresywny
    arr = cv2.adaptiveThreshold(
        arr, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 11
    )

    # recognizer zwykle lubi 3 kanały
    arr = cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
    return arr

def gen_predictions(path):
    image = Image.open(path).convert('RGB')
    doc = DocumentFile.from_images(path)
    result = model_dc(doc)

    page = result.pages[0]
    data = page.export()

    img = page.page
    h, w = data["dimensions"]

    result = ""
    for block in data["blocks"]:
        for line in block["lines"]:
            (x1, y1), (x2, y2) = line["geometry"]
            tmp_img = crop_img(image, x1, y1, x2, y2, w, h)
            result += predict_txt_from_line(tmp_img)+"\n"
            #predict_txt_from_line(tmp_img)
    return result


import os
import numpy as np


#os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

from paddleocr import TextRecognition

rec_engine = TextRecognition(model_name="PP-OCRv5_server_rec")


def predict_txt_from_line(image_pil):
    try:
        if image_pil.size[0] < 8 or image_pil.size[1] < 8:
            return ""

        img = preprocess_line_for_ocr(image_pil)
        results = rec_engine.predict(input=img, batch_size=1)

        texts = []
        for res in results:
            data = res.json if hasattr(res, "json") else res
            if isinstance(data, dict) and "res" in data:
                data = data["res"]
            if isinstance(data, dict) and "rec_text" in data:
                texts.append(str(data["rec_text"]))

        return " ".join(texts).strip()

    except Exception as e:
        print(f"PADDLE ERROR: {type(e).__name__}: {e}")
        return ""


def clean_memory():
    global model_tr, processor
    if 'model_tr' in globals():
        del model_tr
    if 'processor' in globals():
        del processor

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print("Memory cleaned!")

print(gen_predictions("test.png"))
#clean_memory()