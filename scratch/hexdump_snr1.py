import os
import zipfile

zip_path = '/home/net77/koedit/web_client/game/water2.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    snr1_data = z.read('SNR1.DAT')

def hex_dump(data, size=256):
    res = []
    for i in range(0, min(len(data), size), 16):
        chunk = data[i:i+16]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        res.append(f"{i:04x}: {hex_str:<48} | {ascii_str}")
    return '\n'.join(res)

print("--- SNR1.DAT ---")
print(hex_dump(snr1_data, 512))
