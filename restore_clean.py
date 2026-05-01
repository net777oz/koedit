import zipfile
import os
import shutil

zip_path = 'web_client/game/mod_correction_v1.08.zip'
target_zip = 'web_client/game/water2.zip'

print(f"Extracting KAO.LZW from {zip_path}...")
with zipfile.ZipFile(zip_path, 'r') as z:
    z.extract('KAO.LZW', '.')

print("Success: KAO.LZW restored.")

print("Syncing with water2.zip...")
tmp_zip = 'water2.zip.tmp'
with zipfile.ZipFile(target_zip, 'r') as zin:
    with zipfile.ZipFile(tmp_zip, 'w') as zout:
        for item in zin.infolist():
            if item.filename != 'KAO.LZW':
                zout.writestr(item, zin.read(item.filename))
        # Add the new KAO
        zout.write("KAO.LZW", "KAO.LZW")

shutil.move(tmp_zip, target_zip)
print("Success: water2.zip updated with clean KAO.LZW.")
