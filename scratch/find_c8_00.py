import struct
import zipfile

zip_path = '/home/net77/koedit/web_client/game/water2.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    data = z.read('SNR1.DAT')

for i in range(len(data)-2):
    if data[i] == 0xC8 and data[i+1] == 0 and data[i+2] == 0:
        print(f"Found C8 00 00 at offset 0x{i:04X}")
