import zipfile
import os
import shutil

BASE_DIR = '/home/net77/koedit'
CENTRAL_DIR = os.path.join(BASE_DIR, 'game_data')
os.makedirs(CENTRAL_DIR, exist_ok=True)

CENTRAL_ZIP = os.path.join(CENTRAL_DIR, 'water2.zip')
BACKUP_ZIP = os.path.join(BASE_DIR, 'web_client/game/water2_backup.zip')
SCRATCH_DIR = os.path.join(BASE_DIR, 'scratch/gamedata')

# 1. Create the Final Central Zip
temp_zip = CENTRAL_ZIP + ".tmp"
with zipfile.ZipFile(BACKUP_ZIP, 'r') as zin:
    with zipfile.ZipFile(temp_zip, 'w') as zout:
        for item in zin.infolist():
            if item.filename == 'SNR1.MES':
                zout.write(os.path.join(SCRATCH_DIR, 'SNR1_CLEAN.MES'), 'SNR1.MES')
            elif item.filename == 'SNR1.DAT':
                zout.write(os.path.join(SCRATCH_DIR, 'SNR1_CLEAN.DAT'), 'SNR1.DAT')
            else:
                zout.writestr(item, zin.read(item.filename))

if os.path.exists(CENTRAL_ZIP):
    os.remove(CENTRAL_ZIP)
os.rename(temp_zip, CENTRAL_ZIP)
print(f"Created CENTRAL source of truth at: {CENTRAL_ZIP}")

# 2. Delete ALL other redundant zip files and symlinks
redundant_paths = [
    '/home/net77/koedit/static/game/water2.zip',
    '/home/net77/koedit/web_client/static/game/water2.zip',
    '/home/net77/koedit/web_client/dist/static/game/water2.zip',
    '/home/net77/koedit/web_client/game/water2.zip'
]

for p in redundant_paths:
    if os.path.exists(p):
        if os.path.islink(p):
            os.unlink(p)
            print(f"Deleted symlink: {p}")
        else:
            os.remove(p)
            print(f"Deleted file: {p}")

print("Cleanup complete. Only game_data/water2.zip remains.")
