import zipfile

zip_path = '/home/net77/koedit/web_client/game/water2.zip'

def search_all_dat():
    with zipfile.ZipFile(zip_path, 'r') as z:
        for f in z.namelist():
            if f.endswith('.DAT'):
                data = z.read(f)
                pos = data.find(bytes([0xC8, 0x00, 0x00]))
                if pos != -1:
                    print(f"Found C8 00 00 in {f} at 0x{pos:04X}")

search_all_dat()
