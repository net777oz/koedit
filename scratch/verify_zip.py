import zipfile
import struct

zip_path = '/home/net77/koedit/web_client/game/water2.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    data = z.read('SNR1.DAT')

print(f"SNR1.DAT size: {len(data)}")
offsets = []
idx = 0x10
while True:
    val = struct.unpack('>I', data[idx:idx+4])[0]
    if val == 0xFFFFFFFF:
        break
    offsets.append(val)
    idx += 4
print(f"Offsets: {[hex(o) for o in offsets]}")

# Check if our new message ID 0x0494 is there
if bytes([0xC8, 0x04, 0x94]) in data:
    print("Found injected message ID 0x0494!")
    pos = data.find(bytes([0xC8, 0x04, 0x94]))
    print(f"Location: 0x{pos:04X}")
else:
    print("Injected message ID NOT found in SNR1.DAT!")
