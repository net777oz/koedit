import zipfile
import struct

zip_path = '/home/net77/koedit/game_data/water2.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    d = z.read('SNR2.DAT')

# SNR header: Block count at offset 0x08? 
# Wait, UW2 SNR header is:
# 0x00: "SNR " (4 bytes)
# 0x04: ??
# 0x08: ??
# 0x10...: Offset table

# Actually, we can count offsets until 0xFFFFFFFF
count = 0
idx = 0x10
while idx < len(d):
    off = struct.unpack('>I', d[idx:idx+4])[0]
    if off == 0xFFFFFFFF: break
    count += 1
    idx += 4

print(f"SNR2.DAT Block Count: {count}")

# Check first few bytes of each block to find common patterns
for i in range(min(count, 10)):
    off = struct.unpack('>I', d[0x10 + i*4:0x10 + i*4 + 4])[0]
    next_off = struct.unpack('>I', d[0x10 + (i+1)*4:0x10 + (i+1)*4 + 4])[0]
    if next_off == 0xFFFFFFFF: next_off = len(d)
    
    snippet = d[off:off+20].hex(' ')
    print(f"Block {i}: Offset 0x{off:04X}, Start: {snippet}")
