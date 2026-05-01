import zipfile

zip_path = '/home/net77/koedit/game_data/water2.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    d = z.read('SNR2.MES')

messages = d.split(b'\x00')
for i in range(800, 1200):
    if i < len(messages):
        try:
            text = messages[i].decode('cp949')
            if text.strip():
                print(f"Msg {i}: {text}")
        except:
            pass
