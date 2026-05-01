import zipfile

zip_path = '/home/net77/koedit/web_client/game/water2.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    for f in z.infolist():
        print(f.filename)
