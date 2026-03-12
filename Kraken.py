from PIL import Image, ImageDraw
from kraken import blla
from kraken.lib import vgsl
from importlib import resources
import matplotlib.pyplot as plt
import os



def gen_predictions(path, index):

    im = Image.open(path).convert("RGB")

    model_path = resources.files("kraken").joinpath("blla.mlmodel")
    model = vgsl.TorchVGSLModel.load_model(str(model_path))

    seg = blla.segment(im, model=model)

    print(seg.type)
    print(len(seg.lines))

    vis = im.copy()
    draw = ImageDraw.Draw(vis)

    for line in seg.lines:
        boundary = [tuple(pt) for pt in line.boundary]
        if len(boundary) > 1:
            draw.line(boundary + [boundary[0]], fill="red", width=2)

    plt.figure(figsize=(12, 12))
    plt.imshow(vis)
    plt.axis("off")

    output_dir = 'kraken'

    os.makedirs(output_dir, exist_ok=True)

    plt.savefig(f'{output_dir}/res{index}.png', dpi=300, bbox_inches='tight')
    plt.show()

paths = ["bez_kratki.png", "tescik.jpg", "test.png", "scan_15_krotka.jpg", "scan_28_srednia.jpg", "p03-189.png"]
for i, path in enumerate(paths):
    gen_predictions(path, i)