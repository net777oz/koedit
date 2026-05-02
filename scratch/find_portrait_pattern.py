import zipfile

z = zipfile.ZipFile('/home/net77/koedit/game_data/water2.zip')
data = z.read('KOUKAI2.DAT')

start_off = 0x0695 # Assuming entry starts 20 bytes before the name '조안'
entry_size = 50

print("Dumping 50-byte entries for first 6 characters:")
for i in range(6):
    base = start_off + (i * entry_size)
    entry = data[base:base+50]
    name_chunk = data[base+20:base+33].split(b'\x00')[0] # Name is at offset 20?
    try: name = name_chunk.decode('cp949')
    except: name = "[Error]"
    print(f"ID {i+1} ({name}): {entry.hex(' ')}")

# We are looking for a byte that goes 00, 01, 02, 03, 04, 05...
print("\nScanning for incremental byte pattern across entries:")
for offset in range(50):
    vals = [data[start_off + (i * entry_size) + offset] for i in range(6)]
    if vals == [0, 1, 2, 3, 4, 5]:
        print(f"FOUND! Portrait ID is likely at offset {offset}")
        break
else:
    # Try 1-based pattern 01, 02, 03, 04, 05, 06
    for offset in range(50):
        vals = [data[start_off + (i * entry_size) + offset] for i in range(6)]
        if vals == [1, 2, 3, 4, 5, 6]:
            print(f"FOUND! Portrait ID is likely at offset {offset} (1-based)")
            break
    else:
        print("Incremental pattern not found in first 50 bytes. Checking wider range...")
