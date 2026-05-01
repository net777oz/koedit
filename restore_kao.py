import zipfile
import os

zip_path = 'web_client/game/water2.zip'
if os.path.exists(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extract('KAO.LZW', '.')
    print("Success: KAO.LZW restored from water2.zip")
else:
    print(f"Error: {zip_path} not found")
