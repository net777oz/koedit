import zipfile
import sys

zip_path = sys.argv[1]
try:
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for f in zf.infolist():
            if 'KAO' in f.filename.upper() or 'SAVEDATA' in f.filename.upper() or 'PAL' in f.filename.upper():
                print(f.filename)
except Exception as e:
    print("Error:", e)
