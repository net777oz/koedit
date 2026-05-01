import zipfile
import sys
import os

zip_path = '/home/net77/koedit/web_client/game/water2.zip'
if not os.path.exists(zip_path):
    print("Zip not found")
    sys.exit(1)

with zipfile.ZipFile(zip_path, 'r') as z:
    for f in z.infolist():
        fn = f.filename.upper()
        if 'DAT' in fn or 'MSG' in fn or 'EVT' in fn or 'SCEN' in fn or 'SCRIPT' in fn:
            print(f.filename)
