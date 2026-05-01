import zipfile
import os
import shutil

zip_path = '/home/net77/koedit/web_client/game/water2.zip'
backup_path = '/home/net77/koedit/web_client/game/water2_backup.zip'
scratch_dir = '/home/net77/koedit/scratch/gamedata'

# 1. Backup the original zip if not exists
if not os.path.exists(backup_path):
    shutil.copy2(zip_path, backup_path)
    print(f"Created backup at {backup_path}")

# 2. Update the zip
# We create a new zip and copy everything, replacing the target files
# Or more simply, open in 'a' mode and overwrite. 
# In Python's zipfile, to replace, you usually have to rebuild or use a library that supports it.
# We'll rebuild it to be safe and clean.

temp_zip = zip_path + ".tmp"
with zipfile.ZipFile(zip_path, 'r') as zin:
    with zipfile.ZipFile(temp_zip, 'w') as zout:
        for item in zin.infolist():
            if item.filename == 'SNR1.MES':
                zout.write(os.path.join(scratch_dir, 'SNR1_NEW.MES'), 'SNR1.MES')
                print("Replaced SNR1.MES")
            elif item.filename == 'SNR1.DAT':
                zout.write(os.path.join(scratch_dir, 'SNR1_NEW.DAT'), 'SNR1.DAT')
                print("Replaced SNR1.DAT")
            else:
                zout.writestr(item, zin.read(item.filename))

os.replace(temp_zip, zip_path)
print("Successfully updated water2.zip with new story events!")
