import zipfile, struct
z = zipfile.ZipFile('/home/net77/koedit/game_data/water2.zip')
data = z.read('SNR2.DAT')
idx = 0x10 # Block 0
start = struct.unpack('>I', data[idx:idx+4])[0]
next_val = struct.unpack('>I', data[idx+4:idx+8])[0]
end = next_val if next_val != 0xFFFFFFFF else len(data)
block = data[start:end]
print(f"Block 0 (start: {start:04X}, end: {end:04X}):")
print(block[:100].hex(' '))
