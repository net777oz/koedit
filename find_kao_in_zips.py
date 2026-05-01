import zipfile
import os

game_dir = '/mnt/c/Ubuntu-24.04/home/net77/koedit/web_client/game/'
for filename in os.listdir(game_dir):
    if filename.endswith('.zip'):
        path = os.path.join(game_dir, filename)
        print(f"Checking {filename}...")
        try:
            with zipfile.ZipFile(path, 'r') as z:
                # Look for KAO.LZW
                for name in z.namelist():
                    if 'KAO' in name.upper():
                        print(f"  FOUND: {name}")
        except Exception as e:
            print(f"  Error reading {filename}: {e}")
