import zipfile

zip_path = '/home/net77/koedit/game_data/water2.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    d = z.read('SNR2.MES')

print(f"File Size: {len(d)}")
print(f"Header Hex: {d[:100].hex(' ')}")

# Look for actual Korean text anywhere in the file
# "제독" in CP949
target = "\xbca6\xb5b6".encode('latin1') # Wait, I'll use bytes
target = b'\xc1\xa6\xb5\xb6'
pos = d.find(target)
if pos != -1:
    print(f"Found '제독' at: {pos}")
    print(f"Context: {d[pos-10:pos+30].hex(' ')}")
else:
    print("'제독' not found in SNR2.MES")
