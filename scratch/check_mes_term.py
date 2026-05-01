import struct

with open('/home/net77/koedit/scratch/gamedata/SNR1.MES', 'rb') as f:
    data = f.read()

first_offset = struct.unpack('>I', data[0:4])[0]
start = first_offset
# Find where message 0 ends
end = struct.unpack('>I', data[4:8])[0]
msg0 = data[start:end]
print(f"Message 0 raw bytes: {msg0.hex(' ')}")
