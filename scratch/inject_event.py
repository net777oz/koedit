import sys

with open('/home/net77/koedit/scratch/gamedata/EVENT1.DAT', 'rb') as f:
    data = bytearray(f.read())

# Find the sequence C0 01 CC 00 06 C8 00 00
seq = bytes([0xC0, 0x01, 0xCC, 0x00, 0x06, 0xC8, 0x00, 0x00])
pos = data.find(seq)

if pos != -1:
    print(f"Found sequence at offset 0x{pos:04X} ({pos})")
    
    # We want to insert our new dialogue BEFORE this sequence!
    # Our dialogue:
    # C0 01 (Left) CC 00 1F (Rocco portrait) C8 04 94 (Message 0x0494) C7 (Wait)
    # Wait, if we INSERT bytes, the offset table at the beginning of EVENT1.DAT must be updated!
    # The offset table is 5 offsets. If we add 9 bytes, all offsets after the first one must be shifted by +9.
    
    # Let's print the original offset table
    import struct
    offsets = [struct.unpack('>I', data[i*4:i*4+4])[0] for i in range(5)]
    print(f"Original offsets: {[hex(o) for o in offsets]}")
    
    new_data = bytearray()
    new_data.extend(data[:pos])
    
    # Insert new dialogue
    new_dialogue = bytes([0xC0, 0x01, 0xCC, 0x00, 0x1F, 0xC8, 0x04, 0x94, 0xC7])
    new_data.extend(new_dialogue)
    
    new_data.extend(data[pos:])
    
    # Update offset table. Since 'pos' is in the first chunk, all subsequent chunks are shifted by +9.
    # The first chunk starts at offsets[0] (0x14). Since 'pos' > 0x14, we shift offsets[1] to offsets[4].
    for i in range(1, 5):
        if pos < offsets[i]:
            # Actually, all offsets after the block containing 'pos' need shifting.
            # pos is inside block 0. So block 1, 2, 3, 4 are shifted.
            offsets[i] += len(new_dialogue)
            
    # Rewrite offsets in the header
    for i in range(5):
        new_data[i*4:i*4+4] = struct.pack('>I', offsets[i])
        
    print(f"New offsets: {[hex(o) for o in offsets]}")
    
    with open('/home/net77/koedit/scratch/gamedata/EVENT1_NEW.DAT', 'wb') as f:
        f.write(new_data)
        
    print("Created EVENT1_NEW.DAT with injected dialogue!")
else:
    print("Sequence not found.")
