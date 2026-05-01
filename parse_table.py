import sys
import struct

with open(sys.argv[1], 'rb') as f:
    data = f.read()

# Header: 16 bytes
# Dict: 256 bytes
offset = 272

entries = []
while offset < len(data):
    comp_size, dec_size = struct.unpack_from('>II', data, offset)
    if comp_size == 0 and dec_size == 0:
        print(f"Table ended at offset {offset}")
        break
    if comp_size > 50000 or dec_size > 50000:
        print(f"Likely end of table at {offset}. Values: {comp_size}, {dec_size}")
        break
        
    entries.append((comp_size, dec_size))
    offset += 8

print(f"Found {len(entries)} entries in the table.")
for i in range(min(5, len(entries))):
    print(f"Entry {i}: Comp={entries[i][0]}, Dec={entries[i][1]}")

data_start = offset
print(f"Data starts around {data_start}")
