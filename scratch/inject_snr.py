import sys
import struct
import zipfile
import os

zip_path = '/home/net77/koedit/web_client/game/water2.zip'
with zipfile.ZipFile(zip_path, 'r') as z:
    data = bytearray(z.read('SNR1.DAT'))

# Find the sequence C0 01 CC 00 06 C8 00 00
seq = bytes([0xC0, 0x01, 0xCC, 0x00, 0x06, 0xC8, 0x00, 0x00])
pos = data.find(seq)

if pos != -1:
    print(f"Found sequence at offset 0x{pos:04X} ({pos})")
    
    offsets = []
    idx = 0x10
    while True:
        val = struct.unpack('>I', data[idx:idx+4])[0]
        if val == 0xFFFFFFFF:
            break
        offsets.append(val)
        idx += 4
        
    print(f"Original offsets: {[hex(o) for o in offsets]}")
    
    new_data = bytearray()
    new_data.extend(data[:pos])
    
    # Insert new dialogue
    # C0 01 (Left) CC 00 1F (Rocco) C8 04 94 (Message ID 0x0494 = 1172) C7 (Wait)
    new_dialogue = bytes([0xC0, 0x01, 0xCC, 0x00, 0x1F, 0xC8, 0x04, 0x94, 0xC7])
    new_data.extend(new_dialogue)
    
    new_data.extend(data[pos:])
    
    # Update offsets: any offset > pos needs to be shifted by len(new_dialogue)
    for i in range(len(offsets)):
        if offsets[i] > pos:
            offsets[i] += len(new_dialogue)
            
    # Rewrite offsets
    idx = 0x10
    for i in range(len(offsets)):
        new_data[idx:idx+4] = struct.pack('>I', offsets[i])
        idx += 4
        
    print(f"New offsets: {[hex(o) for o in offsets]}")
    
    os.makedirs('/home/net77/koedit/scratch/gamedata', exist_ok=True)
    with open('/home/net77/koedit/scratch/gamedata/SNR1_NEW.DAT', 'wb') as f:
        f.write(new_data)
        
    print("Created SNR1_NEW.DAT with injected dialogue!")
else:
    print("Sequence not found.")
