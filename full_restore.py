import os
import zipfile
import shutil
import subprocess

BASE_DIR = '/home/net77/koedit'
ZIP_PATH = os.path.join(BASE_DIR, 'web_client/static/game/water2.zip')
EXPORT_DIR = os.path.join(BASE_DIR, 'export')
ORIGINALS_DIR = os.path.join(BASE_DIR, 'originals')

def restore():
    print("Starting full restoration...")
    
    # 1. Extract KAO.LZW as base dictionary
    if os.path.exists(ZIP_PATH):
        with zipfile.ZipFile(ZIP_PATH, 'r') as zin:
            zin.extract('KAO.LZW', path=BASE_DIR)
            print("Extracted KAO.LZW from zip.")
    
    # 2. Reset export directory with originals
    if os.path.exists(EXPORT_DIR):
        shutil.rmtree(EXPORT_DIR)
    os.makedirs(EXPORT_DIR)
    
    for fn in os.listdir(ORIGINALS_DIR):
        if fn.endswith('.png'):
            shutil.copy(os.path.join(ORIGINALS_DIR, fn), os.path.join(EXPORT_DIR, fn))
    print("Restored original images to export directory.")

    # 3. Re-pack using originals
    VENV_PYTHON = os.path.join(BASE_DIR, 'venv/bin/python3')
    KOEDIT_PY = os.path.join(BASE_DIR, 'koedit.py')
    subprocess.run([VENV_PYTHON, KOEDIT_PY, 'pack'], cwd=BASE_DIR)
    print("Re-packed KAO.LZW using original images.")

    # 4. Inject back into ZIPs
    kn = os.path.join(BASE_DIR, 'KAO_NEW.LZW')
    ko = os.path.join(BASE_DIR, 'KAO.LZW')
    if os.path.exists(kn):
        shutil.copy(kn, ko)
        targets = [
            os.path.join(BASE_DIR, 'web_client/game/water2.zip'),
            os.path.join(BASE_DIR, 'web_client/static/game/water2.zip')
        ]
        for zp in targets:
            if os.path.exists(zp):
                tmp_zp = zp + '.tmp'
                with zipfile.ZipFile(zp, 'r') as zin, zipfile.ZipFile(tmp_zp, 'w') as zout:
                    for item in zin.infolist():
                        if item.filename != 'KAO.LZW':
                            zout.writestr(item, zin.read(item.filename))
                    zout.write(ko, 'KAO.LZW')
                shutil.move(tmp_zp, zp)
                print(f"Updated {zp} with original assets.")
    
    print("Restoration COMPLETE. System is now back to pristine state.")

if __name__ == '__main__':
    restore()
