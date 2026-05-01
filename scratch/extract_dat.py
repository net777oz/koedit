import zipfile
import sys
import os

zip_path = '/home/net77/koedit/web_client/game/water2.zip'
out_dir = '/home/net77/koedit/scratch/gamedata'
os.makedirs(out_dir, exist_ok=True)

targets = ['EVENT0.DAT', 'SNR0.DAT', 'MESSAGE.DAT', 'EVENT1.DAT']

with zipfile.ZipFile(zip_path, 'r') as z:
    for f in z.infolist():
        fn = f.filename.upper()
        if any(fn.endswith(t) for t in targets):
            z.extract(f, out_dir)
            print(f"Extracted {fn}")
