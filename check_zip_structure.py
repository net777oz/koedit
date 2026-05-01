import zipfile
import os

zip_path = 'web_client/game/water2.zip'
if os.path.exists(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        print("Files in ZIP containing 'KAO':")
        for name in z.namelist():
            if 'KAO' in name.upper():
                print(f"  {name}")
else:
    print(f"File not found: {zip_path}")
