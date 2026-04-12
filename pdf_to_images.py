from pdf2image import convert_from_path
from pathlib import Path

Path("egz_photos").mkdir(parents=True, exist_ok=True)
images = convert_from_path('Egzamin1_20230202.pdf')
for i in range(len(images)):
    images[i].save(f'egz_photos/page{str(i)}.jpg', 'JPEG')