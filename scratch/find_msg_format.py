import zipfile

zip_path = '/home/net77/koedit/game_data/water2.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    d = z.read('SNR1.MES')

target = "안녕 조안".encode('cp949')
pos = d.find(target)

if pos != -1:
    print(f"Found target at: {pos}")
    context = d[max(0, pos-20):pos+80]
    print(f"Hex: {context.hex(' ')}")
    # Try to see if there is a null terminator
    null_pos = d.find(b'\x00', pos)
    print(f"Next Null at: {null_pos}")
else:
    print("Target string not found in SNR1.MES")
