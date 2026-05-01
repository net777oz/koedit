import zipfile
import struct

zip_path = '/home/net77/koedit/game_data/water2.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    d = z.read('SNR1.DAT')

# Block 0 start offset from header
off = struct.unpack('>I', d[0x10:0x14])[0]
print(f"Block 0 Start: 0x{off:04X}")

# Dump first 256 bytes
block_data = d[off:off+256]
print(f"Hex Dump: {block_data.hex(' ')}")

# Look for our injected dialogue ID 1172 (0x0494)
target = b'\x04\x94'
pos = block_data.find(target)
if pos != -1:
    print(f"Found 04 94 at offset +0x{pos:02X}")
    # Show context around it
    context = block_data[max(0, pos-4):min(len(block_data), pos+6)]
    print(f"Context: {context.hex(' ')}")
else:
    print("04 94 not found in the first 256 bytes of Block 0.")
