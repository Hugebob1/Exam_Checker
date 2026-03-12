from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def gen_predictions(path, index):

    model = ocr_predictor(
        det_arch='db_resnet50',
        reco_arch='crnn_vgg16_bn',
        pretrained=True,
        resolve_lines=True
    )

    doc = DocumentFile.from_images(path)
    result = model(doc)

    page = result.pages[0]
    data = page.export()

    img = page.page
    h, w = data["dimensions"]

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.imshow(img)
    ax.axis("off")

    for block in data["blocks"]:
        for line in block["lines"]:
            (x1, y1), (x2, y2) = line["geometry"]
            rect = patches.Rectangle(
                (x1 * w, y1 * h),
                (x2 - x1) * w,
                (y2 - y1) * h,
                fill=False,
                linewidth=2
            )
            ax.add_patch(rect)


    output_dir = 'docTr'

    os.makedirs(output_dir, exist_ok=True)

    plt.savefig(f'{output_dir}/res{index}.png', dpi=300, bbox_inches='tight')
    plt.show()

paths = ["bez_kratki.png", "tescik.jpg", "test.png", "scan_15_krotka.jpg", "scan_28_srednia.jpg", "p03-189.png"]

for i, path in enumerate(paths):
    gen_predictions(path, i)