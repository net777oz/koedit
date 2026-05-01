import os

def hex_dump(filename, size=256):
    with open(filename, 'rb') as f:
        data = f.read(size)
    res = [f"--- {filename} ---"]
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_str = ' '.join(f'{b:02x}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        res.append(f"{i:04x}: {hex_str:<48} | {ascii_str}")
    return '\n'.join(res)

print(hex_dump('/home/net77/koedit/scratch/gamedata/SNR1.MES', 256))
